import azure.functions as func
import logging
import json

app = func.FunctionApp()

@app.route(route="http_trigger", auth_level=func.AuthLevel.FUNCTION)
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        req_body = req.get_json() # Haal de JSON data op van de frontend
    except ValueError:
        return func.HttpResponse(
            "Please pass a JSON body with 'HeartRate', 'SleepHours', and 'StepsPerDay' in the request body",
            status_code=400
        )

    # Haal de data uit de ontvangen JSON
    heart_rate = req_body.get('HeartRate')
    sleep_hours = req_body.get('SleepHours')
    steps_per_day = req_body.get('StepsPerDay')

    if heart_rate is None or sleep_hours is None or steps_per_day is None:
        return func.HttpResponse(
            "Please pass 'HeartRate', 'SleepHours', and 'StepsPerDay' in the request body",
            status_code=400
        )

    # Hier komt jouw logica voor het genereren van advies
    # Dit is slechts een VOORBEELD; pas dit aan met jouw ECHTE ADVIESLOGICA en eventuele DATABASE-INTERACTIE
    advice_message = "Geen specifiek advies beschikbaar." # Standaard bericht

    if heart_rate < 60:
        advice_message = "Je hartslag is laag, mogelijk ben je een atleet of zeer ontspannen. Raadpleeg een arts bij klachten."
    elif heart_rate > 100:
        advice_message = "Je hartslag is hoog, probeer te ontspannen en raadpleeg een arts bij aanhoudende klachten."
    elif sleep_hours < 6:
        advice_message = "Je slaapt te weinig. Probeer meer rust te pakken voor een betere gezondheid."
    elif steps_per_day < 5000:
        advice_message = "Je beweegt te weinig. Probeer meer stappen te zetten per dag."
    elif heart_rate >= 60 and heart_rate <= 100 and sleep_hours >= 7 and steps_per_day >= 8000:
        advice_message = "Uitstekende gezondheidswaarden! Blijf zo doorgaan!"
    else:
        advice_message = "Je waarden zijn prima, maar er is ruimte voor verbetering. Blijf actief en eet gezond!"

    # Stuur het daadwerkelijke advies terug
    return func.HttpResponse(
        json.dumps({"advice": advice_message}),
        status_code=200,
        mimetype="application/json"
    )