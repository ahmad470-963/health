import azure.functions as func
import logging
import json
import os
import pyodbc
import base64

app = func.FunctionApp()

@app.route(route="http_trigger", auth_level=func.AuthLevel.FUNCTION)
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger: Verwerken gezondheidsdata met database opslag.')

    # 1. DATABASE VERBINDING OPHALEN
    db_connection_string = os.environ.get("AzureSqlDbConnection")
    
    # 2. IDENTITEIT OPHALEN (Wie is ingelogd?)
    user_id = None
    user_name = "Onbekend"
    
    header = req.headers.get('x-ms-client-principal')
    if header:
        try:
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

        # 4. ADVIES GENEREREN (Jouw logica voor meerdere adviezen)
        advices = []
        
        if heart_rate < 60: advices.append("Hartslag: Je hartslag is laag. Raadpleeg een arts bij klachten.")
        elif heart_rate > 100: advices.append("Hartslag: Je hartslag is hoog. Probeer te ontspannen.")
        else: advices.append("Hartslag: Je hartslag in rust is gezond.")

        if sleep_hours < 7: advices.append("Slaap: Je slaapt te weinig. Streef naar minimaal 7-9 uur.")
        elif sleep_hours > 9: advices.append("Slaap: Te veel slaap kan ook nadelig zijn.")
        else: advices.append("Slaap: Je slaapuren per nacht zijn gezond.")

        if steps_per_day < 5000: advices.append("Beweging: Je beweegt te weinig. Probeer meer te wandelen.")
        elif steps_per_day >= 5000 and steps_per_day < 8000: advices.append("Beweging: Goed bezig, maar streef naar 8000 stappen.")
        else: advices.append("Beweging: Je stappentelling is uitstekend!")

        final_advice = "\n".join(advices)

        # 5. OPSLAAN IN DATABASE
        if db_connection_string:
            try:
                conn = pyodbc.connect(db_connection_string)
                cursor = conn.cursor()

                # STAP A: Als we een UserID hebben, sla de gebruiker eerst op in de Users tabel
                if user_id:
                    check_user = "SELECT UserID FROM Users WHERE UserID = ?"
                    cursor.execute(check_user, user_id)
                    if not cursor.fetchone():
                        insert_user = "INSERT INTO Users (UserID, Username) VALUES (?, ?)"
                        cursor.execute(insert_user, user_id, user_name)
                        conn.commit()
                        logging.info(f"Nieuwe gebruiker toegevoegd: {user_name}")

                # STAP B: Sla de meting op in HealthMetrics
                insert_metric = """
                    INSERT INTO HealthMetrics 
                    (HeartRate, SleepHours, StepsPerDay, AdviceText, UserID) 
                    VALUES (?, ?, ?, ?, ?)
                """
                cursor.execute(insert_metric, heart_rate, sleep_hours, steps_per_day, final_advice, user_id)
                conn.commit()
                logging.info("Data succesvol opgeslagen in HealthMetrics.")

            except Exception as e:
                # DIT IS BELANGRIJK: We loggen de specifieke databasefout
                logging.error(f"CRITISCHE DATABASE FOUT: {str(e)}")
                # We gaan door zodat de gebruiker wel zijn advies ziet, ook als DB faalt

        # 6. ANTWOORD NAAR WEBSITE (Staat nu buiten het database-blok!)
        return func.HttpResponse(
            json.dumps({"advice": final_advice}),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        return func.HttpResponse(json.dumps({"error": str(e)}), status_code=500)