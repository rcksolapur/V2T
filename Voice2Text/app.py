import requests
from chalice import Chalice
import boto3
import botocore.exceptions
import hmac
import hashlib
import base64
import json

USER_POOL_ID = 'us-east-2_OmAVfEdyX'
CLIENT_ID = '32k0k505fo6joogl06bt2aprbo'
CLIENT_SECRET = '17uje8tick45o9svv5je0v8k3kfgj07e43nk7gas7ntda74j91pg'



app = Chalice(app_name='Voice2Text')
client = boto3.client('cognito-idp')

def github_repos(username):
    formatted_repos = []

    if username:
        url = "https://api.github.com/users/{}/repos".format(username)

        r = requests.get(url)

        list_of_repos = r.json()

        for repo in list_of_repos:
            repo_object = {
                "name": repo["name"],
                "stars": repo["watchers"],
                "language": repo["language"],
            }

            formatted_repos.append(repo_object)

    return formatted_repos


@app.route('/')
def index():
    return {'hello': 'world'}


def get_secret_hash(username):
  msg = username + CLIENT_ID
  dig = hmac.new(str(CLIENT_SECRET).encode('utf-8'),
  msg = str(msg).encode('utf-8'), digestmod=hashlib.sha256).digest()
  d2 = base64.b64encode(dig).decode()
  return d2

@app.route('/login')
def initiate_auth():
    username = 'rcksolapur@gmail.com'
    password = 'India@2020'
    secret_hash = get_secret_hash(username)
    try:
      resp = client.admin_initiate_auth(
                 UserPoolId=USER_POOL_ID,
                 ClientId=CLIENT_ID,
                 AuthFlow='USER_PASSWORD_AUTH',
                 AuthParameters={
                     'USERNAME': username,
                     'SECRET_HASH': secret_hash,
                     'PASSWORD': password,
                  },
                ClientMetadata={
                  'username': username,
                  'password': password,
              })
    except client.exceptions.NotAuthorizedException:
        return None, "The username or password is incorrect"
    except client.exceptions.UserNotConfirmedException:
        return None, "User is not confirmed"
    except Exception as e:
        return None, e.__str__()
    return resp, None

@app.route('/user/{username}')
def github(username):
    return {"repos": github_repos(username)}

@app.route('/upload', methods=['POST'])
def upload():
    s3 = boto3.resource('s3')

    s3.Bucket('prettyprinted').put_object(Key='a_python_file.py', Body=request.files['myfile'])

    return '<h1>File saved to S3</h1>'

