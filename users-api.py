"""
Joanna Lowry & Arturo Lara

Users API
"""

from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from jose import jwk, jwt
from jose.utils import base64url_decode
import json
import time
import urllib.request
import mysql.connector

cnx = mysql.connector.connect(user='admin', password='capstone', host='pellego-db.cdkdcwucys6e.us-west-2.rds.amazonaws.com', database='pellego_database')
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

class QuizResults(Resource):
    def post(self, submodule_id):
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
                query = ("insert ignore into ProgressCompleted (UID, SMID) values (%s, $s)")
                cursor.execute(query, (userID, submodule_id))
                cursor.close()

api.add_resource(QuizResults, "/modules/submodules/<int:submodule_id>/")
if __name__ == "__main__":
    app.run(host="0.0.0.0", port='5000')
