import boto3
import urllib3
import json

urllib3.disable_warnings()

# Declaring variables
http                        =  urllib3.PoolManager()
my_headers                  = {'User-Agent': 'GITHUBUSER'}
git_token                   = 'GITHUBTOKEN'
git_headers                 = {'Authorization': f'token {git_token}', 'User-Agent': 'GITHUBUSER'}
repo_url                    = 'https://api.github.com/users/k8-proxy/repos'
bucket                      = 'wmwaredata'
fileName                    = 'releases.json'
s3                          = boto3.client('s3')

def lambda_handler(event, context):
    # Listing all the repos
    repos                   = []
    resp                    =  http.request('GET',repo_url,headers=my_headers)
    resm                    =  resp.data
    resn                    = json.loads(resm.decode('utf8'))
    for element in resn:
      ids                   = element['id']
      repos.append(ids)

    # Getting release data from all repos
    gitdata                 =   []
    for repo in repos:
      my_url                =  f'https://api.github.com/repositories/{repo}/releases'
      res                   =  http.request('GET',my_url,headers=git_headers)
      myres                 =  json.loads(res.data)
      gitdata.append(myres)
      uploads   = bytes(json.dumps(gitdata, indent=4, sort_keys=True, default=str).encode('UTF-8'))

      # Uploading JSON file to s3 bucket
      s3.put_object(Bucket=bucket, Key=fileName, Body=uploads)

    print("JSON file succesfully created and uploaded to S3")
