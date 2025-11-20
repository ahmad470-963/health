import azure.functions as func
import logging
import json # Importeer json ook als je het nodig hebt

app = func.FunctionApp()

@app.route(route="http_trigger", auth_level=func.AuthLevel.FUNCTION)
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Test trigger zonder database-connectie.')

    # Stuur een simpel JSON-antwoord terug
    return func.HttpResponse(
        json.dumps({"advice": "TEST GESLAAGD: De API werkt nu! Het lag aan de database setup."}),
        status_code=200,
        mimetype="application/json"
    )