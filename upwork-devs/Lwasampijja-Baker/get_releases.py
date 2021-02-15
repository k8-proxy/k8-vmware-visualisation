import boto3
import json
import os
import requests
import pandas as pd
import warnings

from pandas import json_normalize
from github import Github

warnings.filterwarnings('ignore')


bucket                                          = 'wmwaredata'
fileName                                        = 'releases.json'
s3                                              = boto3.client('s3')
git_token                                       = os.getenv('GIT_TOKEN')
git_headers                                     = {'Authorization': f'token {git_token}'}
g                                               = Github(os.getenv('GIT_TOKEN'))

class GetRelease():

    def releases(self):

        # Listing repos

        org                                     = g.get_organization("k8-proxy")
        all_repos                               = org.get_repos()
        repos                                   = []

        for repo in all_repos:
          myrepo                                = repo.id, repo.name, repo.html_url
          repos.append(myrepo)

          df1                                   = pd.DataFrame(repos)
          df1.columns                           = ['id', 'name', 'repo_url']

        # Getting release data

        data                                    = []
        for repo in repos:
          url                                   = f'https://api.github.com/repositories/{repo[0]}/releases'
          res                                   = requests.get(url, headers=git_headers).json()
          data1                                 = json_normalize(res, max_level=1)
          temp_df                               = pd.DataFrame(data1)
          data.append(temp_df )

          df2                                   = pd.concat(data, ignore_index=True)
        df2                                     = df2[['html_url','tag_name', 'published_at','body', 'zipball_url']]

        # Merging release and repo data

        df1['join']                             = 1
        df2['join']                             = 1
        df                                      = df1.merge(df2, on='join').drop('join', axis=1)

        df2.drop('join', axis=1, inplace=True)

        # Finding a matching name in the url

        df['match']                             = [x[0] in x[1] for x in zip(df['name'], df['html_url'])]
        df                                      = df.loc[df['match'] == True]

        df.reset_index(drop=True, inplace=True)

        # Polising results
        df                                      = df[['name','repo_url','body','tag_name', 'published_at','zipball_url']]
        df                                      = df.rename({'name':'repo_name'}, axis=1)
        df                                      = df.rename({'body':'release_name'}, axis=1)
        df                                      = df.rename({'tag_name':'release_tag'}, axis=1)
        df                                      = df.rename({'published_at':'release_date'}, axis=1)

         # retrieving tag information

        tdata                                   =   []
        for repo in repos:
          tag_url                               = f'https://api.github.com/repositories/{repo[0]}/tags'
          t_url                                 = requests.get(tag_url, headers=git_headers).json()
          t_data                                = json_normalize(t_url, max_level=1)
          temp_tdf                              = pd.DataFrame(t_data)
          tdata.append(temp_tdf )

          tdf                                   = pd.concat(tdata, ignore_index=True)
        tdf                                     = tdf[['name','commit.sha','zipball_url']]

        # Merging the releases and tag dataframes on columns with similar information

        df['hash']                              = df.zipball_url.map(tdf.set_index('zipball_url')['commit.sha'])
        df                                      = df.dropna()

        df.reset_index(drop=True, inplace=True)

        df['hash_short']                        = df['hash'].str[:7]
        df                                      = df.drop('zipball_url', 1)

        # Creating a JSON file

        df                                      = df.to_dict(orient ='records')

        uploads                                 = bytes(json.dumps(df, indent=4, sort_keys=True, default=str).encode('UTF-8'))

        # Uploading JSON file to s3 bucket

        s3.put_object(Bucket=bucket, Key=fileName, Body=uploads)
