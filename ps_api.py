from flask import Flask
from flask_restful import Resource, Api, reqparse
import ir_api as ir
import traceback
import stats
import dotenv
import os

dotenv.load_dotenv()
  
# App Constructor
app = Flask(__name__)
api = Api(app)

### Endpoint Classes ###

# Returns all the Laps
class sessionLaps(Resource):
    def get(self):
        # Get args
        parser = reqparse.RequestParser()
        parser.add_argument('session', required=True, location="args") 
        args = parser.parse_args()       
        
        try:
            laps_json = ir.get_session_laps(args['session'])
            return laps_json, 200, {"Access-Control-Allow-Origin": "*"} # Return File and status code 200

        # Return Exception Message and specific error code
        # This can be anything from invalid session to API Failure
        except KeyError as e:
            print(f"Error Getting data from iRacing API")
            return 500
        except Exception as e:
            print(f"Exception Thrown : {repr(e)}")
            traceback.print_exc()


# Returns the Statistics
class sessionStats(Resource):
    def get(self):
         # Get args
        parser = reqparse.RequestParser()
        parser.add_argument('session', required=True, location="args") 
        parser.add_argument('top_laps', required=False, location="args")
        args = parser.parse_args()
        
        try:
            stats_json = stats.get_stats(args['session'])
            return stats_json, 200, {"Access-Control-Allow-Origin": "*"}
        
        except KeyError as e:
            msg = f"Error Getting data from iRacing API"
            return msg, 500

        except Exception as e:
            print(f"Exception Thrown : {repr(e)}")
            traceback.print_exc()


class sessionInfo(Resource):
    def get(self):
        return "Feature not Operational", 400


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
api.add_resource(sessionInfo, '/info')

if __name__ == '__main__':
    flask_port = os.getenv('PORT')
    app.run(port=flask_port, host="0.0.0.0")
    # app.run(debug=True)