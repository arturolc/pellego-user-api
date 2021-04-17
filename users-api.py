"""
Joanna Lowry & Arturo Lara & Chris Bordoy

Users API
"""

from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from jose import jwk, jwt
from jose.utils import base64url_decode
from datetime import date, datetime, timedelta
import simplejson as json
import time
import urllib.request
import mysql.connector
from dateutil.relativedelta import relativedelta

app = Flask(__name__)
api = Api(app)

region = 'us-west-2'
userpool_id = 'us-west-2_AdDJsuC6f'
app_client_id = 'o4uoksbrsfa78eo644tpf20um'
keys_url = 'https://cognito-idp.{0}.amazonaws.com/{1}/.well-known/jwks.json'.format(region, userpool_id)


# instead of re-downloading the public keys every time
# we download them only on cold start
# https://aws.amazon.com/blogs/compute/container-reuse-in-lambda/
with urllib.request.urlopen(keys_url) as f:
  response = f.read()
keys = json.loads(response.decode('utf-8'))['keys']

def verifyToken(token):
    # get the kid from the headers prior to verification
    headers = jwt.get_unverified_headers(token)
    kid = headers['kid']
    # search for the kid in the downloaded public keys
    key_index = -1
    for i in range(len(keys)):
        if kid == keys[i]['kid']:
            key_index = i
            break
    if key_index == -1:
        print('Public key not found in jwks.json')
        return False
    # construct the public key
    public_key = jwk.construct(keys[key_index])
    # get the last two sections of the token,
    # message and signature (encoded in base64)
    message, encoded_signature = str(token).rsplit('.', 1)
    # decode the signature
    decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))
    # verify the signature
    if not public_key.verify(message.encode("utf8"), decoded_signature):
        print('Signature verification failed')
        return False
    print('Signature successfully verified')
    # since we passed the verification, we can now safely
    # use the unverified claims
    claims = jwt.get_unverified_claims(token)
    # additionally we can verify the token expiration
    if time.time() > claims['exp']:
        print('Token is expired')
        return False
    # and the Audience  (use claims['client_id'] if verifying an access token)
    if claims['aud'] != app_client_id:
        print('Token was not issued for this audience')
        return False
    # now we can use the claims
    print(claims)
    return claims

def json_serial(obj):
   """JSON serializer for objects not serializable by default json code"""

   if isinstance(obj, (datetime, date)):
       return obj.isoformat()
   raise TypeError ("Type %s not serializable" % type(obj))

class ProgressLastDate(Resource):
    def post(self):
         # json_data = request.get_json(force=True)
        
        # res = verifyToken(json_data['token'])
        # if res is False:
        #    return "401 Unauthorized", 401 
        res = request.get_json(force=True)
        cnx = mysql.connector.connect(user='admin', password='capstone', host='pellego-db.cdkdcwucys6e.us-west-2.rds.amazonaws.com', database='pellego_database')
        
        cursor = cnx.cursor(dictionary=True)
        cursor.execute(("select UID from Users where Email = %s"), (res['email'],))
        userID = int(cursor.fetchall()[0]['UID'])
        cursor.close()

        cursor = cnx.cursor(dictionary=True)
        cursor.execute(("select Recorded as date from User_Word_Values where UID = %s order by Recorded desc limit 1"), (userID,))
        result = cursor.fetchone()
        cursor.close()

        cnx.commit()
        cnx.close()
        return json.loads(json.dumps(result, default=json_serial))
        

class Progress(Resource):
    def post(self):
        # json_data = request.get_json(force=True)
        
        # res = verifyToken(json_data['token'])
        # if res is False:
        #    return "401 Unauthorized", 401 
        res = request.get_json(force=True)
        cnx = mysql.connector.connect(user='admin', password='capstone', host='pellego-db.cdkdcwucys6e.us-west-2.rds.amazonaws.com', database='pellego_database')

        cursor = cnx.cursor(dictionary=True)
        cursor.execute(("select UID from Users where Email = %s"), (res['email'],))
        userID = int(cursor.fetchall()[0]['UID'])
        cursor.close()

        ret = {}
        cursor = cnx.cursor(dictionary=True)
        cursor.execute(("select * from User_Word_Values where Recorded > %s and UID = %s"), (res['date'], userID))
        ret['values'] = cursor.fetchall()
        cursor.close()

        cnx.commit()
        cnx.close()
        return json.loads(json.dumps(ret, default=json_serial))


class QuizResults(Resource):
    def post(self, module_id, submodule_id):
        #json_data = request.get_json(force=True)
        #
        #res = verifyToken(json_data['token'])
        #if res is False:
        #    return "401 Unauthorized", 401
        res = request.get_json(force=True)
        cnx = mysql.connector.connect(user='admin', password='capstone', host='pellego-db.cdkdcwucys6e.us-west-2.rds.amazonaws.com', database='pellego_database')

        cursor = cnx.cursor(dictionary=True)
        cursor.execute(("select UID from Users where Email = %s"), (res['email'],))
        userID = int(cursor.fetchall()[0]['UID'])
        cursor.close()

        cursor = cnx.cursor(dictionary=True)
        query = ("insert ignore into ProgressCompleted (UID, MID, SMID) values (%s, %s, %s)")
        cursor.execute(query, (userID, module_id, submodule_id,))
        cursor.close()

        cnx.commit()
        cnx.close()
        return "Success"

class UserWordValues(Resource):
    def post(self, words_read, wpm):
        #json_data = request.get_json(force=True)
        #
        #res = verifyToken(json_data['token'])
        #if res is False:
        #    return "401 Unauthorized", 401
        res = request.get_json(force=True)
        cnx = mysql.connector.connect(user='admin', password='capstone', host='pellego-db.cdkdcwucys6e.us-west-2.rds.amazonaws.com', database='pellego_database')

        cursor = cnx.cursor(dictionary=True)
        cursor.execute(("select UID from Users where Email = %s"), (res['email'],))
        userID = int(cursor.fetchall()[0]['UID'])
        cursor.close()

        cursor = cnx.cursor(dictionary=True)
        query = ("insert ignore into User_Word_Values (UID, WordsRead, WPM, Recorded) values (%s, %s, %s, %s)")

        #DATES ARE SAVED IN UTC TIMEZONE
        cursor.execute(query, (userID, words_read, wpm, date.today(),))
        cursor.close()

        cnx.commit()
        cnx.close()
        return "Success"

class CompletionCount(Resource):
    def post(self):
        #json_data = request.get_json(force=True)
        #
        #res = verifyToken(json_data['token'])
        #if res is False:
        #    return "401 Unauthorized", 401
        res = request.get_json(force=True)
        cnx = mysql.connector.connect(user='admin', password='capstone', host='pellego-db.cdkdcwucys6e.us-west-2.rds.amazonaws.com', database='pellego_database')

        cursor = cnx.cursor(dictionary=True)
        cursor.execute(("select UID from Users where Email = %s"), (res['email'],))
        userID = int(cursor.fetchall()[0]['UID'])
        cursor.close()

        cursor = cnx.cursor(dictionary=True)
        query = ("select MID, SMID from ProgressCompleted where UID = %s")
        cursor.execute(query, (userID, ))
        result = cursor.fetchall()
        cursor.close()

        cnx.close()
        return json.loads(json.dumps(result))

class ProgressValues(Resource):
    def post(self):
        #json_data = request.get_json(force=True)
        #
        #res = verifyToken(json_data['token'])
        #if res is False:
        #    return "401 Unauthorized", 401
        res = request.get_json(force=True)
        cnx = mysql.connector.connect(user='admin', password='capstone', host='pellego-db.cdkdcwucys6e.us-west-2.rds.amazonaws.com', database='pellego_database')

        cursor = cnx.cursor(dictionary=True)
        cursor.execute(("select UID from Users where Email = %s"), (res['email'],))
        userID = int(cursor.fetchall()[0]['UID'])
        cursor.close()

        currDate = datetime.utcnow().date()
        cursor = cnx.cursor(dictionary=True)
        query = ("select sum(WordsRead) as WordsRead, round(cast(avg(WPM) as UNSIGNED), 0) as WPM, Recorded from User_Word_Values where UID = %s and Recorded = %s")
        cursor.execute(query, (userID, currDate))
        result = cursor.fetchall()
        if result[0]['WordsRead'] == None:
            result[0]['WordsRead'] = 0
            result[0]['WPM'] = 0
            result[0]['Recorded'] = currDate.strftime("%Y-%m-%d")
        cursor.close()

        for item in range(1, 7):
            cursor = cnx.cursor(dictionary=True)
            query = ("select sum(WordsRead) as WordsRead, round(cast(avg(WPM) as UNSIGNED), 0) as WPM, Recorded from User_Word_Values where UID = %s and Recorded = %s")
            currDate -= timedelta(days=1)
            cursor.execute(query, (userID, currDate))
            result += cursor.fetchall()
            if result[item]['WordsRead'] == None:
                result[item]['WordsRead'] = 0
                result[item]['WPM'] = 0
                result[item]['Recorded'] = currDate.strftime("%Y-%m-%d")
            cursor.close()

        currMonth = datetime.utcnow().date()
        for item in range(7,19):
            cursor = cnx.cursor(dictionary=True)
            query = ("select sum(WordsRead) as WordsRead, round(cast(avg(WPM) as UNSIGNED), 0) as WPM, Recorded from User_Word_Values where UID = %s and Month(Recorded) = Month(%s)")
            cursor.execute(query, (userID, currMonth))     
            result += cursor.fetchall()
            if result[item]['WordsRead'] == None:
                result[item]['WordsRead'] = 0
                result[item]['WPM'] = 0
                result[item]['Recorded'] = currMonth.strftime("%Y-%m-%d")
            cursor.close()
            currMonth -= relativedelta(months=1)

        cnx.close()
        return json.loads(json.dumps(result, indent=4, sort_keys=True, default=str))

class TotalWordsRead(Resource):
    def post(self):
        #json_data = request.get_json(force=True)
        #
        #res = verifyToken(json_data['token'])
        #if res is False:
        #    return "401 Unauthorized", 401
        res = request.get_json(force=True)
        cnx = mysql.connector.connect(user='admin', password='capstone', host='pellego-db.cdkdcwucys6e.us-west-2.rds.amazonaws.com', database='pellego_database')

        cursor = cnx.cursor(dictionary=True)
        cursor.execute(("select UID from Users where Email = %s"), (res['email'],))
        userID = int(cursor.fetchall()[0]['UID'])
        cursor.close()

        cursor = cnx.cursor(dictionary=True)
        query = ("select SUM(WordsRead) as TotalWordsRead from User_Word_Values where UID = %s")

        cursor.execute(query, (userID, ))
        result = cursor.fetchone()
        cursor.close()

        cnx.close()
        return json.loads(json.dumps(result))

api.add_resource(ProgressLastDate, '/users/progress/last')
api.add_resource(QuizResults, "/users/<int:module_id>/quiz_results/<int:submodule_id>")
api.add_resource(UserWordValues, "/users/<int:words_read>/<int:wpm>")
api.add_resource(CompletionCount, "/users/completion_count")
api.add_resource(Progress, "/users/progress")
api.add_resource(ProgressValues, "/users/progress_values")
api.add_resource(TotalWordsRead, "/users/profile/total_words_read")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port='5001')
