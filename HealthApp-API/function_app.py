import azure.functions as func
import logging
import json

app = func.FunctionApp()

@app.route(route="http_trigger", auth_level=func.AuthLevel.FUNCTION)
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            "Please pass a JSON body with 'HeartRate', 'SleepHours', and 'StepsPerDay' in the request body",
            status_code=400
        )

    heart_rate = req_body.get('HeartRate')
    sleep_hours = req_body.get('SleepHours')
    steps_per_day = req_body.get('StepsPerDay')

    if heart_rate is None or sleep_hours is None or steps_per_day is None:
        return func.HttpResponse(
            "Please pass 'HeartRate', 'SleepHours', and 'StepsPerDay' in the request body",
            status_code=400
        )

    # --- Hier begint de logica voor MEERDERE adviezen ---
    advices = [] # Lijst om alle adviezen in op te slaan

    # Advies voor Hartslag
    if heart_rate < 60:
        advices.append("Hartslag: Je hartslag is laag. Raadpleeg een arts bij klachten.")
    elif heart_rate > 100:
        advices.append("Hartslag: Je hartslag is hoog. Probeer te ontspannen en raadpleeg een arts bij aanhoudende klachten.")
    elif heart_rate >= 60 and heart_rate <= 100:
        advices.append("Hartslag: Je hartslag in rust is gezond.")
    else:
        advices.append("Hartslag: Geen specifiek advies beschikbaar voor hartslag.")


    # Advies voor Slaapuren
    if sleep_hours < 7:
        advices.append("Slaap: Je slaapt te weinig. Streef naar minimaal 7-9 uur per nacht.")
    elif sleep_hours > 9:
        advices.append("Slaap: Te veel slaap kan ook nadelig zijn. Controleer je energielevel overdag.")
    else:
        advices.append("Slaap: Je slaapuren per nacht zijn gezond.")


    # Advies voor Stappen
    if steps_per_day < 5000:
        advices.append("Beweging: Je beweegt te weinig. Probeer meer stappen te zetten, streef naar minimaal 8000 stappen per dag.")
    elif steps_per_day >= 5000 and steps_per_day < 8000:
        advices.append("Beweging: Goed bezig met je stappen. Streef naar meer dan 8000 stappen voor optimale gezondheid.")
    else:
        advices.append("Beweging: Je stappentelling per dag is uitstekend! Blijf zo doorgaan.")


    # Combineer alle adviezen tot één string, gescheiden door bijvoorbeeld nieuwe regels
    final_advice = "\n".join(advices)
    # --- Einde logica voor MEERDERE adviezen ---

    return func.HttpResponse(
        json.dumps({"advice": final_advice}), # Stuur de gecombineerde advies-string terug
        status_code=200,
        mimetype="application/json"
    )