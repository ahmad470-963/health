import azure.functions as func
import logging
import json

app = func.FunctionApp()

@app.route(route="http_trigger", auth_level=func.AuthLevel.FUNCTION)
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger: Advies genereren zonder database.')

    try:
        # 1. DATA UIT HET FORMULIER LEZEN
        req_body = req.get_json()
        heart_rate = req_body.get('HeartRate')
        sleep_hours = req_body.get('SleepHours')
        steps_per_day = req_body.get('StepsPerDay')

        # Controleer of alle velden zijn ingevuld
        if heart_rate is None or sleep_hours is None or steps_per_day is None:
            return func.HttpResponse(
                json.dumps({"error": "Vul alle velden in."}), 
                status_code=400,
                mimetype="application/json"
            )

        # 2. ADVIES GENEREREN (Logica)
        advices = []
        
        # Hartslag logica
        if heart_rate < 60: 
            advices.append("Hartslag: Je hartslag is aan de lage kant. Rustig aan.")
        elif heart_rate > 100: 
            advices.append("Hartslag: Je hartslag is hoog. Probeer wat ontspanningsoefeningen.")
        else: 
            advices.append("Hartslag: Je hartslag is in rust uitstekend.")

        # Slaap logica
        if sleep_hours < 7: 
            advices.append("Slaap: Je hebt minder dan 7 uur geslapen. Probeer vanavond vroeger naar bed te gaan.")
        elif sleep_hours > 9: 
            advices.append("Slaap: Je hebt veel geslapen. Let op dat je overdag wel actief blijft.")
        else: 
            advices.append("Slaap: Je hebt een gezonde hoeveelheid geslapen.")

        # Stappen logica
        if steps_per_day < 5000: 
            advices.append("Beweging: Je hebt weinig bewogen vandaag. Maak eens een korte wandeling.")
        elif steps_per_day < 10000: 
            advices.append("Beweging: Goed bezig! Je bent bijna bij de aanbevolen 10.000 stappen.")
        else: 
            advices.append("Beweging: Top! Je hebt je bewegingsdoelen ruimschoots gehaald.")

        # Voeg alle adviezen samen tot één tekst
        final_advice = "\n".join(advices)

        # 3. ANTWOORD TERUGSTUREN
        return func.HttpResponse(
            json.dumps({"advice": final_advice}),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.error(f"Fout opgetreden: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": "Er is iets misgegaan bij het verwerken van je gegevens."}),
            status_code=500,
            mimetype="application/json"
        )
