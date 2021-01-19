#! /usr/bin/env python
from pyVim.connect import SmartConnect, SmartConnectNoSSL, Disconnect
from pyVmomi import vim
import json

from pyVim.connect import SmartConnect
from pyVmomi import vim
import ssl


s=ssl.SSLContext(ssl.PROTOCOL_TLSv1)
s.verify_mode=ssl.CERT_NONE
si= SmartConnectNoSSL(host="HOST", user="USER", pwd="PASSWORD")
content=si.content

# Method that populates objects of type vimtype
def get_all_objs(content, vimtype):
        obj = {}
        container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
        for managed_object_ref in container.view:
                obj.update({managed_object_ref: managed_object_ref.name})
        return obj

#Calling above method
getAllVms=get_all_objs(content, [vim.VirtualMachine])

print('[')
#Iterating each vm object and printing its name
for vm in getAllVms:
        print('{')
        print (' "Name":', '"{}",'.format(vm.summary.config.name))
        print (' "PowerState":', '"{}",'.format(vm.summary.runtime.powerState))
        print (' "Notes":', '"{}",'.format(vm.summary.config.annotation))
        print (' "Guest":', '"{}"' .format(vm.summary.config.guestFullName))
        print (' "NumCpu":', '"{}",'.format(vm.summary.config.numCpu))
        #print (' "CoresPerSocket":', '"{}",'.format(vm.summary.))
        print (' "MemoryMB":', '"{}",'.format(vm.summary.config.memorySizeMB))
        #print (' "MemoryGB":', '"{}",'.format(vm.summary.config.memorySizeGB))
        #print (' "VMHostId":', '"{}",'.format(vm.summary.runtime.VMHostId))
        print (' "VMHost":', '"{}",'.format(vm.summary.runtime.host))
        #print (' "VApp":', '"{}",'.format(vm.summary.))
        #print (' "FolderId":', '"{}",'.format(vm.summary.))
        print (' "Folder":', '"{}",'.format(vm.summary.config.vmPathName))
        #print (' "ResourcePoolId":', '"{}",'.format(vm.summary.))
        #print (' "ResourcePool":', '"{}",'.format(vm.summary.))
        #print (' "HARestartPriority":', '"{}",'.format(vm.summary.))
        #print (' "HAIsolationResponse":', '"{}",'.format(vm.summary.))
        #print (' "DrsAutomationLevel":', '"{}",'.format(vm.summary.))
        #print (' "VMSwapfilePolicy":', '"{}",'.format(vm.summary.))
        #print (' "VMResourceConfiguration":', '"{}",'.format(vm.summary.))
        #print (' "Version":', '"{}",'.format(vm.summary.config.Version))
        print (' "HardwareVersion":', '"{}",'.format(vm.summary.config.hwVersion))
        #print (' "PersistentId":', '"{}",'.format(vm.summary.))
        print (' "GuestId":', '"{}",'.format(vm.summary.config.guestId))
        print (' "CommitedSpace":', '"{}",'.format(vm.summary.storage.uncommitted))
        print (' "UNCommitedSpace":', '"{}",'.format(vm.summary.storage.committed))
        #print (' "DatastoreIdList":', '"{}",'.format(vm.summary.))
        print (' "CreateDate":', '"{}",'.format(vm.summary.storage.timestamp))
        #print (' "SEVEnabled":', '"{}",'.format(vm.summary.))
        #print (' "ExtensionData":', '"{}",'.format(vm.summary.))
        #print (' "CustomFields":', '"{}",'.format(vm.CustomFieldsManager.Value))
        print (' "Id":', '"{}",'.format(vm.summary.config.uuid))
        print (' "Uid":', '"{}",'.format(vm.summary.config.instanceUuid))
        print (' "BootTime":', '"{}",'.format(vm.summary.runtime.bootTime))
        print (' "NumVirtualDisks":', '"{}",'.format(vm.summary.config.numVirtualDisks))
        print (' "IPAddress":', '"{}",'.format(vm.summary.guest.ipAddress))
        print (' "MaxCpuUsage":', '"{}",'.format(vm.summary.runtime.maxCpuUsage))
        print (' "MaxMemoryUsage":', '"{}",'.format(vm.summary.runtime.maxMemoryUsage))
        print (' "ConnectionState":', '"{}"'.format(vm.summary.runtime.connectionState))
        print('},')
        
print(']')
