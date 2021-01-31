#! /usr/bin/env python

from pyVim.connect import SmartConnect, SmartConnectNoSSL, Disconnect
from pyVmomi import vim
import json
import boto3
import os

from pyVim.connect import SmartConnect
from pyVmomi import vim
import ssl



# Declaring variables

HOST                  = os.getenv('MYHOST')
USER                  = os.getenv('MYUSER')
PASSWORD              = os.getenv('MYPASSWORD')
SECRET                = os.getenv('WEBHOOK_TOKEN')
bucket                = 'wmware-data-visualisation'
fileName              = 'machines.json'
s3                    = boto3.client('s3')
s                     = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
s.verify_mode         = ssl.CERT_NONE
si                    = SmartConnectNoSSL(host=HOST, user=USER, pwd=PASSWORD)
content               = si.content


def handler(event, context):
    datacenter = content.rootFolder.childEntity[0]
    vms = datacenter.vmFolder.childEntity
    data               =   []
    #Iterating each vm object and printing its name
    for vm in vms:
        VMData  = {}
        VMData['Name']                  = vm.summary.config.name
        VMData['PowerState']            = vm.summary.runtime.powerState
        VMData['Notes']                 = vm.summary.config.annotation
        VMData['Guest']                 = vm.summary.config.name
        VMData['NumCpu']                = vm.summary.config.numCpu
        VMData['MemoryMB']              = vm.summary.config.memorySizeMB
        VMData['VMHost']               = vm.summary.runtime.host
        VMData['Folder']                = vm.summary.config.vmPathName
        VMData['HardwareVersion']       = vm.summary.config.hwVersion
        VMData['GuestId']               = vm.summary.config.guestId
        VMData['CommitedSpace']         = vm.summary.storage.committed
        VMData['UNCommitedSpace']       = vm.summary.storage.committed
        VMData['CreateDate']            = vm.summary.storage.timestamp
        VMData['Id']                    = vm.summary.config.uuid
        VMData['Uid']                   = vm.summary.config.instanceUuid
        VMData['BootTime']              = vm.summary.runtime.bootTime
        VMData['NumVirtualDisks']       = vm.summary.config.numVirtualDisks
        VMData['IPAddress']             = vm.summary.guest.ipAddress
        VMData['MaxCpuUsage']           = vm.summary.runtime.maxCpuUsage
        VMData['MaxMemoryUsage']        = vm.summary.runtime.maxMemoryUsage
        VMData['ConnectionState']       = vm.summary.runtime.connectionState
        VMData['Version']               = vm.config.version
        
        data.append(VMData)

        uploads   = bytes(json.dumps(data, indent=4, sort_keys=True, default=str).encode('UTF-8'))

        # Uploading JSON file to s3 bucket
        s3.put_object(Bucket=bucket, Key=fileName, Body=uploads)

    message = {
      'message': 'JSON file succesfully created and uploaded to S3'
       }

    return {
       'statusCode': 200,
       'headers': {'event-Type': 'application/json'},
       'body': json.dumps(message)
       }
