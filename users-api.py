"""
Joanna Lowry

Users API
"""

from flask import Flask
from flask_restful import Resource, Api

import mysql.connector
import json

cnx = mysql.connector.connect(user='admin', password='capstone', host='127.0.0.1', database='pellego_database')
app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()

#Gets the User first and last name given an email
class GetUser(Resource):
    def get(self, email):
        query = ("select Name from Users where Email=%s")
        cursor = cnx.cursor(dictionary=True)
        		
        cursor.execute(query, (email,))
        #have some sort of error checking here. Not sure how to do that yet
        result = cursor.fetchall()
        cursor.close()
        return json.loads(json.dumps(result))

<<<<<<< HEAD
api.add_resource(GetUser, "/getuser")

=======
#
class AddUser(Resource):
    def post(self):
        parser.add_argument('name', type=str)
        parser.add_argument('email', type=str)
        args = parser.parse_args()
        query = ("INSERT INTO Users (Email, Name) VALUES(%s, %s)")
        cursor = cnx.cursor(dictionary=True)
        data = (args['email'], args['name'])
        
        try: 
            cursor.execute(query, data)

            cnx.commit()
            cursor.close()
            return {'status' : 'User Added'}
        except:
            cnx.rollback()
            cnx.close()
            return {'status' : 'Something went wrong'}
        
        
        #send back something indicating it was successful
   

#current functionality is we can get everything from the users table. This is not practical
#Functionality we need:
#given a user's id (email hash), give them: level status, test status, user analytics, library books
#We should also be able to get a user's name from their hash

#We also need to be able to set things in the database
#Things like, adding a user, updating the status (test or LM), adding a book to the library, updating their words, etc
#Maybe this is setup? But we need to have the authentication send us the user info (name email, etc)
#let's focus on:
#adding a user - we will not be adding hashes right now. It will just be based on email.
#getting a user's name from their email so we can display their name
#and level_status and test_status stuff


api.add_resource(GetUser, "/user/<string:email>")
api.add_resource(AddUser, '/', '/user/add')
>>>>>>> 97821cdbda62a6ec9f4868e5d311e90e1f21644e
if __name__ == "__main__":
    app.run(host="0.0.0.0", port='5000')
