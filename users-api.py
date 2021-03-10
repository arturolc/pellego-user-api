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
        # do a simple query to check if MySQL connection is open
        try:
            cursor = cnx.cursor(dictionary=True)
            cursor.execute("Select 1")
            cursor.fetchall()
            cursor.close()
        except:
            cnx = mysql.connector.connect(user='admin', password='capstone', host='pellego-db.cdkdcwucys6e.us-west-2.rds.amazonaws.com', database='pellego_database')

        query = ("select Name from Users where Email=%s")
        cursor = cnx.cursor(dictionary=True)
        		
        cursor.execute(query, (email,))
        
        result = cursor.fetchall()
        cursor.close()
        return json.loads(json.dumps(result))


class AddUser(Resource):
    def post(self):
        # do a simple query to check if MySQL connection is open
        try:
            cursor = cnx.cursor(dictionary=True)
            cursor.execute("Select 1")
            cursor.fetchall()
            cursor.close()
        except:
            cnx = mysql.connector.connect(user='admin', password='capstone', host='pellego-db.cdkdcwucys6e.us-west-2.rds.amazonaws.com', database='pellego_database')
            
        json_data = request.get_json(force=True)
        query = ("INSERT INTO Users (Email, Name) VALUES(%s, %s)")
        cursor = cnx.cursor(dictionary=True)
        args = json_data[0]
        data = (args['email'], args['name'])
        print(data)        
        try: 
            cursor.execute(query, data)

            cnx.commit()
            cursor.close()
            return [{'status' : 'User Added'}]
        except:
            cnx.rollback()
            cnx.close()
            return [{'status' : 'Something went wrong'}]
        

#Gets and returns the status of all the learning modules intros of a particular user
class GetIntroStatus(Resource):
    def get(self, email):
        # do a simple query to check if MySQL connection is open
        try:
            cursor = cnx.cursor(dictionary=True)
            cursor.execute("Select 1")
            cursor.fetchall()
            cursor.close()
        except:
            cnx = mysql.connector.connect(user='admin', password='capstone', host='pellego-db.cdkdcwucys6e.us-west-2.rds.amazonaws.com', database='pellego_database')

        query = ("select Name, Completed from LM_Module natural join LM_Intro natural join Intro_Status natural join Users where email=%s")
        cursor = cnx.cursor(dictionary=True)
        		
        cursor.execute(query, (email,))
        
        result = cursor.fetchall()
        cursor.close()
        return json.loads(json.dumps(result))

#Gets the all the LM_submodule status's for one user
class GetSubmoduleStatus(Resource):
    def get(self, module, email):
        # do a simple query to check if MySQL connection is open
        try:
            cursor = cnx.cursor(dictionary=True)
            cursor.execute("Select 1")
            cursor.fetchall()
            cursor.close()
        except:
            cnx = mysql.connector.connect(user='admin', password='capstone', host='pellego-db.cdkdcwucys6e.us-west-2.rds.amazonaws.com', database='pellego_database')

        query = ("")
        cursor = cnx.cursor(dictionary=True)
        		
        cursor.execute(query, (email,))
        
        result = cursor.fetchall()
        cursor.close()
        return json.loads(json.dumps(result))


api.add_resource(GetUser, "/user/<string:email>")
api.add_resource(AddUser, "/user/add")
api.add_resource(GetSubmoduleStatus, "/user/submodule/<string:email>")
api.add_resource(GetIntroStatus, "/user/intro/<string:email>")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port='5001')
