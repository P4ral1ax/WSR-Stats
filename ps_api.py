from flask import Flask
from flask_restful import Resource, Api, reqparse
import ir_api as ir
import traceback

  
# App Constructor
app = Flask(__name__)
api = Api(app)

### Endpoint Classes ###

# Returns all the Laps
class sessionLaps(Resource):
    def post(self):
        # Get args
        parser = reqparse.RequestParser()
        parser.add_argument('session', required=True) 
        args = parser.parse_args()
        
        try:
            laps_json = ir.get_session_laps(args['session'])
            return laps_json, 200 # Return File and status code 200

        # Return Exception Message and specific error code
        # This can be anything from invalid session to API Failure
        except Exception as e:
            print(f"Exception Thrown : {repr(e)}")
            traceback.print_exc()

# Returns the Statistics
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