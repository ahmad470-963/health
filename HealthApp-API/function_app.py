import azure.functions as func
import logging
import json
import os
import pyodbc
import base64

app = func.FunctionApp()

@app.route(route="http_trigger", auth_level=func.AuthLevel.FUNCTION)
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger: Verwerken gezondheidsdata met user-login.')

    # 1. Haal de database verbinding op
    db_connection_string = os.environ.get("AzureSqlDbConnection")
    
    # 2. IDENTITEIT OPHALEN (Wie is ingelogd?)
    # Azure SWA stopt de user info in een header genaamd 'x-ms-client-principal'
    user_id = None
    user_name = "Onbekend"
    
    header = req.headers.get('x-ms-client-principal')
    if header:
        try:
            # De header is gecodeerd (base64), we moeten hem decoderen
            decoded = base64.b64decode(header).decode('utf-8')
            user_json = json.loads(decoded)
            
            user_id = user_json.get('userId')
            user_name = user_json.get('userDetails')
            logging.info(f"Gebruiker herkend: {user_name} (ID: {user_id})")
        except Exception as e:
            logging.error(f"Fout bij lezen gebruiker: {e}")
    else:
        logging.warning("Geen ingelogde gebruiker gevonden (Anoniem verzoek).")

    # 3. DATA UIT HET FORMULIER LEZEN
    try:
        req_body = req.get_json()
        heart_rate = req_body.get('HeartRate')
        sleep_hours = req_body.get('SleepHours')
        steps_per_day = req_body.get('StepsPerDay')

        if not all([heart_rate, sleep_hours, steps_per_day]):
            return func.HttpResponse(json.dumps({"error": "Vul alle velden in."}), status_code=400)

        # 4. ADVIES GENEREREN (Jouw logica)
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

                # STAP A: Als we een UserID hebben, sla de gebruiker eerst op in de Users tabel
                if user_id:
                    # Check of gebruiker al bestaat
                    check_sql = "SELECT UserID FROM Users WHERE UserID = ?"
                    cursor.execute(check_sql, user_id)
                    if not cursor.fetchone():
                        # Bestaat niet? Voeg toe!
                        insert_user = "INSERT INTO Users (UserID, Username) VALUES (?, ?)"
                        cursor.execute(insert_user, user_id, user_name)
                        logging.info(f"Nieuwe gebruiker toegevoegd: {user_name}")
                        conn.commit()

                # STAP B: Sla de meting op (inclusief UserID!)
                # Let op: Als user_id None is (niet ingelogd), wordt NULL opgeslagen in de database
                insert_metric = """
                    INSERT INTO HealthMetrics 
                    (HeartRate, SleepHours, StepsPerDay, AdviceText, UserID) 
                    VALUES (?, ?, ?, ?, ?)
                """
                cursor.execute(insert_metric, heart_rate, sleep_hours, steps_per_day, final_advice, user_id)
                conn.commit()
                
                logging.info("Data succesvol opgeslagen.")

            except Exception as e:
                logging.error(f"Database fout: {e}")
                return func.HttpResponse(json.dumps({"error": "Database fout, probeer later opnieuw."}), status_code=500)

        return func.HttpResponse(
            json.dumps({"advice": final_advice}),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        return func.HttpResponse(json.dumps({"error": str(e)}), status_code=500)