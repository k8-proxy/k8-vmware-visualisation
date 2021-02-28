import boto3
import json
import os
import requests
import pandas as pd
import warnings

from pandas import json_normalize
from github import Github

warnings.filterwarnings('ignore')

class Get_GW_Releases:
  def __init__(self):
    git_token                                       = os.getenv('GIT_TOKEN')
    self.git_headers                                = {'Authorization': f'token {git_token}'}
    g                                               = Github(os.getenv('GIT_TOKEN'))
    org                                             = g.get_organization("k8-proxy")
    self.all_repos                                  = org.get_repos()
    self.onerepo                                    = ['GW-Releases']

  def get_all(self):
    allrepos                                        = []
    for repo in self.all_repos:
      myrepo                                        = repo.id, repo.name, repo.html_url
      allrepos.append(myrepo)
    k8repos                                         = pd.DataFrame(allrepos)
    k8repos.columns                                 = ['id', 'name', 'repo_url']
    return k8repos

  # Get content function
  def get_content(self,repos):
    data                                            = []
    for repo in repos:
      url                                           = f'https://api.github.com/repos/k8-proxy/{repo}/contents'
      req                                           = requests.get(url, headers=self.git_headers).json()
      temp_data                                     = json_normalize(req, max_level=1)
      temp_df                                       = pd.DataFrame(temp_data)
      data.append(temp_df )
      content                                       = pd.concat(data, ignore_index=True)
    # Matching repos in the content with the known k8-proxy repos to filter out garbage
    content                                         = content[['path','sha', 'html_url', 'url']]
    content['repo_url']                             = content.path.map(self.get_all().set_index('name')['repo_url'])
    content                                         = content.dropna()
    content.reset_index(drop                        = True, inplace=True)
    return content

  #Get releases function
  def get_releases(self,repos):
    rdata                                           = []
    for repo in repos:
      url                                           = f'https://api.github.com/repos/k8-proxy/{repo}/releases'
      req                                           = requests.get(url, headers=self.git_headers).json()
      temp_data                                     = json_normalize(req, max_level=1)
      temp_df                                       = pd.DataFrame(temp_data)
      rdata.append(temp_df)
    releases                                        = pd.concat(rdata, ignore_index=True)
    releases                                        = releases[['html_url','tag_name', 'published_at','body', 'zipball_url']]
    return releases

  #Get commits function
  def get_commits(self,repos):
    cdata                                           = []
    for repo in repos:
      url                                           = f'https://api.github.com/repos/k8-proxy/{repo}/commits'
      req                                           = requests.get(url, headers=self.git_headers).json()
      temp_data                                     = json_normalize(req, max_level=2)
      temp_df                                       = pd.DataFrame(temp_data)
      cdata.append(temp_data)
    commits                                         = pd.concat(cdata, ignore_index=True)
    commits                                         = commits[['sha', 'commit.message']]
    commits                                         = commits .rename({'commit.message':'message'}, axis=1)
    return commits

  #Get tags function
  def get_tags(self,repos):
    tdata                                           = []
    for repo in repos:
      url                                           = f'https://api.github.com/repos/k8-proxy/{repo}/tags'
      req                                           = requests.get(url, headers=self.git_headers).json()
      temp_data                                     = json_normalize(req, max_level=2)
      temp_df                                       = pd.DataFrame(temp_data)
      tdata.append(temp_data)

    tags                                            = pd.concat(tdata, ignore_index=True)
    tags                                            = tags.rename({'commit.sha':'hash'}, axis=1)
    tags                                            = tags.rename({'commit.url':'commit_url'}, axis=1)
    tags                                            = tags.rename({'name':'version'}, axis=1)
    tags['repo_name']                               = 'GW-Releases'
    tags['repo_url']                                = 'https://github.com/k8-proxy/GW-Releases'
    tags['hash_short']                              = tags['hash'].str[:7]
    tags                                            = tags[['repo_name','hash', 'commit_url','repo_url', 'hash_short']]
    tags                                            = tags.drop_duplicates(subset='repo_name')
    return tags

  #Get content function
  def create_json(self):
    gw_cont                                         = self.get_content(self.onerepo)
    gw_cont                                         = gw_cont[['path','sha','repo_url', 'html_url']]
    gw_cont                                         = gw_cont.rename({'path':'repo_name'}, axis=1)
    gw_cont                                         = gw_cont.rename({'sha':'hash'}, axis=1)
    gw_cont                                         = gw_cont.rename({'html_url':'commit_url'}, axis=1)
    gw_cont['hash_short']                           = gw_cont['hash'].str[:7]
    # Extracting only the repo names to create a list
    content_repos                                   = gw_cont['repo_name'].tolist()
    repos                                           = content_repos + self.onerepo
    g_com                                           = self.get_tags(self.onerepo)
    # Add GW-releases df to the wanted repos
    gw_cont                                         = pd.concat([gw_cont, g_com], ignore_index=True)
    gw_cont                                         = gw_cont[['repo_name','hash', 'commit_url','repo_url', 'hash_short']]
    releases                                        = self.get_releases(repos)
    # Select out only the required repos
    gw_cont['join']                                 = 1
    releases['join']                                = 1
    wanted_rel                                      = gw_cont.merge(releases, on='join').drop('join', axis=1)
    releases.drop('join', axis                      = 1, inplace=True)
    wanted_rel['match']                             = [x[0] in x[1] for x in zip(wanted_rel['repo_name'], wanted_rel['html_url'])]
    wanted_rel                                      = wanted_rel.loc[wanted_rel['match'] == True]
    wanted_rel.reset_index(drop                     = True, inplace=True)
    wanted_rel                                      = wanted_rel[['repo_name','repo_url','tag_name','body', 'published_at','hash','hash_short','commit_url']]
    wanted_rel                                      = wanted_rel.rename({'tag_name':'version'}, axis=1)
    wanted_rel                                      = wanted_rel.rename({'published_at':'release_date'}, axis=1)
    # Pick the lates release
    wanted_rel                                      = wanted_rel.drop_duplicates(subset='repo_name')
    wanted_rel.reset_index(drop                     =  True, inplace=True)
    commits                                         = self.get_commits(repos)
    commits                                         = commits.rename({'sha':'hash'}, axis=1)
    main_releases                                   = pd.merge(wanted_rel, commits, on='hash' , how="left")
    # Combining release notes with commit messages
    main_releases                                   = main_releases.fillna('')
    main_releases['join']                           = ' '
    main_releases['release_notes']                  =  main_releases["message"]+ main_releases['join'] + main_releases["body"]

    main_releases.drop(['body', 'message', 'join'], axis=1, inplace=True)

    subdata                                         = self.get_content(content_repos)
    subdata                                         = subdata.rename({'path':'sub_repo_name'}, axis=1)
    subdata                                         = subdata.rename({'sha':'sub_hash'}, axis=1)
    subdata                                         = subdata.rename({'html_url':'sub_commit_url'}, axis=1)
    subdata                                         = subdata.rename({'repo_url':'sub_repo_url'}, axis=1)
    subdata['sub_hash_short']                       = subdata['sub_hash'].str[:7]
    sub_repos                                       = subdata['sub_repo_name'].tolist()
    releases                                        = self.get_releases(sub_repos)
    # Select out only the required repos
    subdata['join']                                 = 1
    releases['join']                                = 1
    wanted_rel                                      = subdata.merge(releases, on='join').drop('join', axis=1)
    releases.drop('join', axis                      = 1, inplace=True)
    wanted_rel['match']                             = [x[0] in x[1] for x in zip(wanted_rel['sub_repo_name'], wanted_rel['html_url'])]
    wanted_rel                                      = wanted_rel.loc[wanted_rel['match'] == True]
    wanted_rel.reset_index(drop                     = True, inplace=True)
    wanted_rel                                      = wanted_rel[['sub_repo_name','sub_repo_url','tag_name','body', 'published_at','sub_hash','sub_hash_short','sub_commit_url','url']]
    wanted_rel                                      = wanted_rel.rename({'tag_name':'sub_version'}, axis=1)
    wanted_rel                                      = wanted_rel.rename({'published_at':'sub_release_date'}, axis=1)
    commits                                         = self.get_commits(sub_repos)
    commits                                         = commits.rename({'sha':'sub_hash'}, axis=1)
    sub_releases                                    = pd.merge(wanted_rel, commits, on='sub_hash' , how="left")
    sub_releases                                    = sub_releases.drop_duplicates(subset='sub_repo_name')
    sub_releases.reset_index(drop                   = True, inplace=True)
    # Combining release notes with commit messages
    sub_releases                                    = sub_releases.fillna('')
    sub_releases['join']                            = ' '
    sub_releases['sub_release_notes']               = sub_releases["message"]+ sub_releases['join'] + sub_releases["body"]

    sub_releases.drop(['body', 'message', 'join'], axis=1, inplace=True)

    nurepo                                          = gw_cont[['repo_name']]
    nurepo['join']                                  = 1
    sub_releases['join']                            = 1
    jo                                              = nurepo.merge(sub_releases, on='join').drop('join', axis=1)
    sub_releases.drop('join', axis                  = 1, inplace=True)
    jo['match']                                     = [x[0] in x[1] for x in zip(jo['repo_name'], jo['url'])]
    jo                                              = jo.loc[jo['match'] == True]
    jo.reset_index(drop                             = True, inplace=True)
    jo                                              = jo[['repo_name','sub_repo_name','sub_repo_url','sub_version','sub_hash','sub_hash_short','sub_release_date', 'sub_commit_url', 'sub_release_notes']]
    final                                           = pd.merge(jo, main_releases, on='repo_name', how='right')

    #Creating a JSON file
    myjson                                          = final.to_dict(orient ='records')
    uploads                                         = bytes(json.dumps(myjson, indent=4, sort_keys=True, default=str).encode('UTF-8'))

    # Uploading JSON file to s3 bucket
    bucket                                          = 'wmwaredata'
    fileName                                        = 'gw_releases.json'
    s3                                              = boto3.client('s3')

    s3.put_object(Bucket=bucket, Key=fileName, Body=uploads)
