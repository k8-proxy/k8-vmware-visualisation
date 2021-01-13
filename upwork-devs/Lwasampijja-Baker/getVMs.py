#!/usr/bin/env python

"""
Python program for listing the vms on an ESX / vCenter host
"""
import re
import atexit

from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim

import tools.cli as cli


def get_args():
    parser = cli.build_arg_parser()
    parser.add_argument('-f', '--find',
                        required=False,
                        action='store',
                        help='String to match VM names')
    args = parser.parse_args()

    return cli.prompt_for_password(args)


def print_vm_info(virtual_machine):
    """
    Print information for a particular virtual machine or recurse into a
    folder with depth protection
    """
    summary = virtual_machine.summary
    print("Name                 : ", summary.config.name)
    print("Template             : ", summary.config.template)
    print("Path                 : ", summary.config.vmPathName)
    print("Guest                : ", summary.config.guestFullName)
    print("UUID                 : ", summary.config.instanceUuid)
    print("Boot_Time            : ", summary.runtime.bootTime)
    print("Connection_State     : ", summary.runtime.connectionState)
    print("Guest_ID             : ", summary.config.guestId)
    print("Host                 : ", summary.runtime.host)
    print("Host_Name            : ", summary.guest.hostName)
    print("Memory_Size_MB       : ", summary.config.memorySizeMB)
    print("Max_Cpu_Usage        : ", summary.runtime.maxCpuUsage)
    print("Max_Memory_Usage     : ", summary.runtime.maxMemoryUsage)
    print("Cpu_No               : ", summary.config.numCpu)
    print("Virtual_Disk_No      : ", summary.config.numVirtualDisks)
    print("Commited_Space_Bytes : ", summary.storage.committed)
    print("Uncommited_Space_Bytes: ", summary.storage.uncommitted)
    print("UUID                 : ", summary.config.uuid)
    annotation = summary.config.annotation
    if annotation:
        print("Annotation : ", annotation)
    print("State      : ", summary.runtime.powerState)
    if summary.guest is not None:
        ip_address = summary.guest.ipAddress
        tools_version = summary.guest.toolsStatus
        if tools_version is not None:
            print("VMware-tools: ", tools_version)
        else:
            print("Vmware-tools: None")
        if ip_address:
            print("IP         : ", ip_address)
        else:
            print("IP         : None")
    if summary.runtime.question is not None:
        print("Question  : ", summary.runtime.question.text)
    print("")


def main():
    """
    Simple command-line program for listing the virtual machines on a system.
    """

    args = get_args()

    try:
        if args.disable_ssl_verification:
            service_instance = connect.SmartConnectNoSSL(host=args.host,
                                                         user=args.user,
                                                         pwd=args.password,
                                                         port=int(args.port))
        else:
            service_instance = connect.SmartConnect(host=args.host,
                                                    user=args.user,
                                                    pwd=args.password,
                                                    port=int(args.port))

        atexit.register(connect.Disconnect, service_instance)

        content = service_instance.RetrieveContent()

        container = content.rootFolder  # starting point to look into
        viewType = [vim.VirtualMachine]  # object types to look for
        recursive = True  # whether we should look into it recursively
        containerView = content.viewManager.CreateContainerView(
            container, viewType, recursive)

        children = containerView.view
        if args.find is not None:
            pat = re.compile(args.find, re.IGNORECASE)
        for child in children:
            if args.find is None:
                print_vm_info(child)
            else:
                if pat.search(child.summary.config.name) is not None:
                    print_vm_info(child)

    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)
        return -1

    return 0


# Start program
if __name__ == "__main__":
    main()
