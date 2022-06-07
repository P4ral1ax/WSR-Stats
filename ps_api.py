from flask import Flask
from flask_restful import Resource, Api
import pandas as pd

  
# App Constructor
app = Flask(__name__)
api = Api(app)

# Endpoint Classes
class sessionLaps(Resource):
    def get(self):
        return("pass")

class sessionStats(Resource):
    def get(self):
        return("pass")

class driver(Resource):
    pass

class team(Resource):
    pass

class Hello(Resource):
    def get(self):
        return "hello World", 201

api.add_resource(Hello, '/')
api.add_resource(sessionLaps, '/laps')
api.add_resource(sessionStats, '/stats')


if __name__ == '__main__':
    app.run(debug = True, port=33507)