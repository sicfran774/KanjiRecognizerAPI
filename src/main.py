from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from predict import Predictor
from flask_cors import CORS
import json

app = Flask(__name__)
api = Api(app)
CORS(app)

NUMBER_RETURNED = 10

class PredictKanji(Resource):
    def post(self):
        data = request.get_json(force=True)
        uri = data['data']
        predictor = Predictor(uri)
        results = predictor.predict(NUMBER_RETURNED)
        response = jsonify(results)
        return response

api.add_resource(PredictKanji, "/")

if __name__ == "__main__":
    app.run(debug=True)