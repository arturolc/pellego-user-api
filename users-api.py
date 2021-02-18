"""
Joanna Lowry

Users API
"""

from flask import Flask, request
from flask_restful import Resource, Api, reqparse

import mysql.connector
import json

cnx = mysql.connector.connect(user='admin', password='capstone', host='pellego-db.cdkdcwucys6e.us-west-2.rds.amazonaws.com', database='pellego_database')
app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()

#Gets the User first and last name given an email
class GetUser(Resource):
    def get(self, email):
        query = ("select Name from Users where Email=%s")
        cursor = cnx.cursor(dictionary=True)
        		
        cursor.execute(query, (email,))
        
        result = cursor.fetchall()
        cursor.close()
        return json.loads(json.dumps(result))


class AddUser(Resource):
    def post(self):
        #parser.add_argument('name', type=str)
        #parser.add_argument('email', type=str)
        #args = parser.parse_args()
        json_data = request.get_json(force=True)
        query = ("INSERT INTO Users (Email, Name) VALUES(%s, %s)")
        cursor = cnx.cursor(dictionary=True)
        #data = (args['email'], args['name'])
        args = json_data[0]
        data = (args['email'], args['name'])
        #print(args)
        print(data)        
        try: 
            cursor.execute(query, data)

            cnx.commit()
            cursor.close()
            return {'status' : 'User Added'}
        except:
            cnx.rollback()
            cnx.close()
            return {'status' : 'Something went wrong'}
        

api.add_resource(GetUser, "/user/<string:email>")
api.add_resource(AddUser, '/', '/user/add')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port='5000')
