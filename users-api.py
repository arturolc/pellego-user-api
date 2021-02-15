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


class GetUser(Resource):
    def get(self):
        query = "select * from Users"
        cursor = cnx.cursor(dictionary=True)
        		
        cursor.execute(query)
        result = cursor.fetchall()
        cursor.close()
        return json.loads(json.dumps(result))

api.add_resource(GetUser, "/getuser")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port='5000')
