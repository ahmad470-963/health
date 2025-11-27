import azure.functions as func
import logging
import json
import os
import pyodbc
import base64

app = func.FunctionApp()

@app.route(route="http_trigger", auth_level=func.AuthLevel.FUNCTION)
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger: Gezondheidsdata verwerken.')

    # 1. DATABASE VERBINDING
    db_connection_string = os.environ.get("AzureSqlDbConnection")
    
    # 2. GEBRUIKER OPHALEN (Uit de speciale header van Azure)
    # Azure SWA stuurt de user info in een base64 encoded header 'x-ms-client-principal'
    user_id = None
    user_email = "Onbekend"
    
    header = req.headers.get('x-ms-client-principal')
    if header:
        try:
            # De header decoderen van geheimschrift naar leesbare tekst
            decoded = base64.b64decode(header).decode('utf-8')
            user_json = json.loads(decoded)
            
            # Hier halen we de unieke ID en de naam/email uit
            user_id = user_json.get('userId')
            user_email = user_json.get('userDetails')
            logging.info(f"Gebruiker herkend: {user_email} (ID: {user_id})")
        except Exception as e:
            logging.error(f"Fout bij lezen gebruiker: {e}")
    else:
        logging.warning("Geen ingelogde gebruiker gevonden.")

    # 3. GEZONDHEIDSDATA LEZEN
    try:
        req_body = req.get_json()
        heart_rate = req_body.get('HeartRate')
        sleep_hours = req_body.get('SleepHours')
        steps_per_day = req_body.get('StepsPerDay')

        if not all([heart_rate, sleep_hours, steps_per_day]):
            return func.HttpResponse(json.dumps({"error": "Vul alle velden in."}), status_code=400)

        # 4. ADVIES BEREKENEN
        advices = []
        if sleep_hours < 7: advices.append("Slaap: Probeer minimaal 7-8 uur te slapen.")
        else: advices.append("Slaap: Goed bezig met je nachtrust!")
        
        if steps_per_day < 5000: advices.append("Beweging: Probeer wat meer te wandelen.")
        else: advices.append("Beweging: Lekker bezig met bewegen!")
        
        if heart_rate > 100: advices.append("Hartslag: Je rusthartslag is wat hoog.")
        elif heart_rate < 60: advices.append("Hartslag: Lage rusthartslag (sportief!).")
        else: advices.append("Hartslag: Prima hartslag.")

        final_advice = "\n".join(advices)

        # 5. OPSLAAN IN DATABASE
        if db_connection_string:
            try:
                conn = pyodbc.connect(db_connection_string)
                cursor = conn.cursor()

                # STAP A: Als we een gebruiker hebben, zorg dat hij in de Users tabel staat
                if user_id:
                    # Check of gebruiker bestaat, zo niet: voeg toe
                    check_user_sql = "SELECT UserID FROM Users WHERE UserID = ?"
                    cursor.execute(check_user_sql, user_id)
                    if not cursor.fetchone():
                        insert_user_sql = "INSERT INTO Users (UserID, Username) VALUES (?, ?)"
                        cursor.execute(insert_user_sql, user_id, user_email)
                        logging.info(f"Nieuwe gebruiker aangemaakt: {user_email}")

                # STAP B: Sla de meting op (NU MET UserID!)
                sql_query = """
                    INSERT INTO HealthMetrics 
                    (HeartRate, SleepHours, StepsPerDay, AdviceText, UserID) 
                    VALUES (?, ?, ?, ?, ?)
                """
                cursor.execute(sql_query, heart_rate, sleep_hours, steps_per_day, final_advice, user_id)
                conn.commit()
                
            except Exception as e:
                logging.error(f"Database fout: {e}")
                return func.HttpResponse(json.dumps({"error": "Database fout"}), status_code=500)

        return func.HttpResponse(json.dumps({"advice": final_advice}), status_code=200, mimetype="application/json")

    except Exception as e:
        return func.HttpResponse(json.dumps({"error": str(e)}), status_code=500)