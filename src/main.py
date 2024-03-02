from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from predict import Predictor
from flask_cors import CORS
import json

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

class HelloWorld(Resource):
    def get(self):
        return {"message": "Hello World!"}

api.add_resource(PredictKanji, "/api/recognize", endpoint="recognize")
api.add_resource(HelloWorld, "/", endpoint="hello")

CORS(app)

if __name__ == "__main__":
    app.run(ssl_context=('/etc/letsencrypt/live/sicfran.xyz/fullchain.pem', '/etc/letsencrypt/live/sicfran.xyz/privkey.pem'))
