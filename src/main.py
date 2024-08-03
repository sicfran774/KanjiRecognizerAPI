from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from predict import Predictor
from flask_cors import CORS
import json
from send_email import EmailDriver

app = Flask(__name__)
api = Api(app)

NUMBER_RETURNED = 20

class PredictKanji(Resource):
    def get(self):
        return {"numReturned": NUMBER_RETURNED}
    def post(self):
        data = request.get_json(force=True)
        uri = data['data']
        predictor = Predictor(uri)
        results = predictor.predict(NUMBER_RETURNED)
        response = jsonify(results)
        return response
    
class Emailer(Resource):
    def get(self):
        email_driver = EmailDriver()
        results = email_driver.separate_accounts()
        response = jsonify(results)
        return response

api.add_resource(PredictKanji, "/api/recognize")
api.add_resource(Emailer, "/api/emailer")

CORS(app)

if __name__ == "__main__":
    app.run(ssl_context=('/etc/letsencrypt/live/sicfran.xyz/fullchain.pem', '/etc/letsencrypt/live/sicfran.xyz/privkey.pem'))
