### 1. Get VM Ware data
The following scripts extracts vmware informatation into a JSON file as an AWS Lambda function in to an S3 Bucket.

- getVMs.py
- getVMs_lambda.py

### 2. Get All Github Organisation Release Data
The following scripts extracts all release data from all repos into a JSON file as an AWS Lambda function in to an S3 Bucket.

- get_releases.py
- lambda_function.py

### 3. Get Latest Github release data from the GW-Releases 
The following scripts extracts all release data from the GW-Releases repo into a JSON file as an AWS Lambda function in to an S3 Bucket.

- get_recent_releases.py
- gw_release_lambda_function.py

### 4. Packaging python packages for AWS Lambda 
##### Step 1. Start a Cloud9 Linux instance in AWS
- Search for Cloud9 in the AWS Services
- Click Create Environment
- Create a name for your environment and click next step
- Keep the environment default settings (Create a new EC2 instance) and click next step
- Click ‘Create Environment’ and you’re ready to go

##### Step 2. Creating layers in the cloud9 terminal

Type the following code in the terminal, I am using pandas as an example but you can install any other packages. Its creating a directory, virtual environment and installing pandas.

```sh
$ mkdir mypackages  && cd mypackages
$ virtualenv myenv  && source ./myenv/bin/activate
$ pip install pandas
$ deactivate
```
This second pard creates a directory, copies the packages, zip it and create a lambda layer.

```sh
$ mkdir python && cd python
$ cp -r ../myenv/lib/python3.6/site-packages/* .
$ cd ..
$ zip -r python_packages.zip python
$ aws lambda publish-layer-version --layer-name visualisation --zip-file fileb://python_packages.zip --compatible-runtimes python3.6
```

##### Step 3. Create lambda function and add layer
Note: Choose python 3.6 when creating a new lambda function.
