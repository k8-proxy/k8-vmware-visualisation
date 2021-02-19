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
fileName                                        = 'gw_releases.json'
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
        url                                     = f'https://api.github.com/repos/k8-proxy/GW-Releases/contents'
        res                                     = requests.get(url, headers=git_headers).json()
        data1                                   = json_normalize(res, max_level=1)
        dft                                     = pd.DataFrame(data1)
        dft                                     = dft[['path','sha', 'html_url']]


        dft['repo_url']                         = dft.path.map(df1.set_index('name')['repo_url'])
        dft                                     = dft.dropna()
        dft.reset_index(drop                    = True, inplace=True)
        dft                                     = dft.rename({'path':'repo_name'}, axis=1)
        dft                                     = dft.rename({'sha':'hash'}, axis=1)
        dft                                     = dft.rename({'html_url':'commit_url'}, axis=1)
        dft['hash_short']                       = dft['hash'].str[:7]

        myrepos                                 = dft['repo_name']
        nurepo                                  = dft[['repo_name']]
        repos                                   = myrepos.tolist()

        rdata                                   =   []
        for repo in repos:
          rurl                                  = f'https://api.github.com/repos/k8-proxy/{repo}/releases'
          resn                                  = requests.get(rurl, headers=git_headers).json()
          data2                                 = json_normalize(resn, max_level=1)
          temp_dfs                              = pd.DataFrame(data2)
          rdata.append(temp_dfs )
          df3                                   = pd.concat(rdata, ignore_index=True)

        df3                                     = df3[['html_url','tag_name', 'published_at','body', 'zipball_url']]
        df1['join']                             = 1
        df3['join']                             = 1
        df                                      = df1.merge(df3, on='join').drop('join', axis=1)

        df3.drop('join', axis=1, inplace=True)

        df['match']                             = [x[0] in x[1] for x in zip(df['name'], df['html_url'])]
        df                                      = df.loc[df['match'] == True]

        df.reset_index(drop=True, inplace=True)

        df                                      = df[['name','repo_url','body','tag_name', 'published_at','zipball_url']]
        df                                      = df.rename({'name':'repo_name'}, axis=1)
        df                                      = df.rename({'body':'release_name'}, axis=1)
        df                                      = df.rename({'tag_name':'release_tag'}, axis=1)
        df                                      = df.rename({'published_at':'release_date'}, axis=1)

        # tags
        tdata                                   =   []
        for repo in repos:
          tag_url                               = f'https://api.github.com/repos/k8-proxy/{repo}/tags'
          t_url                                 = requests.get(tag_url, headers=git_headers).json()
          t_data                                = json_normalize(t_url, max_level=1)
          temp_tdf                              = pd.DataFrame(t_data)
          tdata.append(temp_tdf )

          tdf                                   = pd.concat(tdata, ignore_index=True)

        tdf                                     = tdf[['name','commit.sha','zipball_url']]
        df['hash']                              = df.zipball_url.map(tdf.set_index('zipball_url')['commit.sha'])
        df                                      = df.dropna()

        df.reset_index(drop=True, inplace=True)

        df                                      = df.drop('zipball_url', 1)
        dft                                     = dft[['hash','hash_short', 'commit_url']]
        nudf                                    = pd.merge(df, dft, on='hash')
        nudf                                    = nudf.drop_duplicates(subset='repo_name')

        data                                    = []
        for repo in repos:
          myurl                                 = f'https://api.github.com/repos/k8-proxy/{repo}/contents'
          req                                   = requests.get(myurl, headers=git_headers).json()
          data1                                 = json_normalize(req, max_level=1)
          temp_df                               = pd.DataFrame(data1)
          data.append(temp_df )

          dfg                                   = pd.concat(data, ignore_index=True)

        dfg                                     = dfg[['path','sha', 'html_url', 'url']]
        dfg['repo_url']                         = dfg.path.map(df1.set_index('name')['repo_url'])
        dfg                                     = dfg.dropna()
        dfg.reset_index(drop  = True)

        nurepo['join']                          = 1
        dfg['join']                             = 1
        jo                                      = nurepo.merge(dfg, on='join').drop('join', axis=1)

        dfg.drop('join', axis=1, inplace=True)

        jo['match']                             = [x[0] in x[1] for x in zip(jo['repo_name'], jo['url'])]
        jo                                      = jo.loc[jo['match'] == True]
        jo.reset_index(drop=True, inplace=True)

        jo                                      = jo.rename({'sha':'sub_hash'}, axis=1)
        jo                                      = jo.rename({'path':'sub_name'}, axis=1)
        jo                                      = jo.rename({'html_url':'sub_commit_url'}, axis=1)
        jo                                      = jo.rename({'repo_url':'sub_repo_commit_url'}, axis=1)
        jo                                      = jo[['repo_name','sub_name','sub_hash','sub_commit_url', 'sub_repo_commit_url']]
        jo['sub_hash_short']                    = jo['sub_hash'].str[:7]

        final                                   = pd.merge(jo, nudf, on='repo_name', how='right')

        # Creating a JSON file
        myjson                                  = final.to_dict(orient ='records')
        uploads                                 = bytes(json.dumps(myjson, indent=4, sort_keys=True, default=str).encode('UTF-8'))

        # Uploading JSON file to s3 bucket

        s3.put_object(Bucket=bucket, Key=fileName, Body=uploads)
