#! /usr/bin/env python
from pyVim.connect import SmartConnect, SmartConnectNoSSL, Disconnect
from pyVmomi import vim
import json
import boto3

from pyVim.connect import SmartConnect
from pyVmomi import vim
import ssl


s                   =   ssl.SSLContext(ssl.PROTOCOL_TLSv1)
s.verify_mode       =   ssl.CERT_NONE
si                  =   SmartConnectNoSSL(host="HOST", user="USER", pwd="PASSWORD")
content             =   si.content

# Method that populates objects of type vimtype
def get_all_objs(content, vimtype):
        obj         = {}
        container   = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)

        for managed_object_ref in container.view:
                obj.update({managed_object_ref: managed_object_ref.name})
        return obj

#Calling above method
getAllVms           =   get_all_objs(content, [vim.VirtualMachine])

fileName            =   'machines' + '.json'
data                =   []
s3 = boto3.client('s3')
bucket ='wmware-data-visualisation'

#Iterating each vm object and printing its name
for vm in getAllVms:
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

        data.append(VMData)

# Writing the data to a JSON file
with open(fileName, 'w') as json_file:
    makejson = json.dump(data, json_file, indent=4, sort_keys=True, default=str)

s3.put_object(Bucket=bucket, Key=fileName, Body=makejson)

print('JSON file Created Successfully')
