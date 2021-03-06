from flask import Flask, request
from flask_restful import Resource, Api
from json import dumps
from flask_cors import CORS


from scoreboard_calc import calculate_espn_rankings


app = Flask(__name__)
api = Api(app)
CORS(app)


class Health(Resource):
    def get(self):
        return {'health': "true"}

class CalculateESPNRankings(Resource):
    def get(self, week_number):
        scores, calculations = calculate_espn_rankings(week_number)

        return {'scores': scores, 'calculations': calculations}

api.add_resource(Health, '/health')
api.add_resource(CalculateESPNRankings, '/espn_rankings/<int:week_number>')

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')