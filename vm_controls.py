#!/usr/bin/env python

''' This module contains classes involved with the control of VM
    powerstates and details. It was written for QA automation
    as part of the Nanigans IT Dev-Ops work.

    Dave C. 2016

    See examples within each class below.
  
    The idea behind this would be to potentially allow QA or others 
    some manual control over VM power state, without giving away
    the keys to the kingdom and having them hang the company.  

'''

import os
import sys
import time
import SoftLayer
import config
from pprint import pprint as pp


class VmConnector(object):
    ''' This class is responsible for building the 
        client connection to SoftLayer '''

    def __init__(self):
    
        self.client = config.client
        self.mgr = SoftLayer.VSManager(self.client)


class VmPowerOn(VmConnector):
    ''' This class powers on a designated VM passed in

    /* Example

    vm = 'vm-demo'
    toggle_vm = VmPowerOn(vm)
    vm_status = toggle_vm.vm_poweron()
    */ ''' 


    def __init__(self,virtualGuestName):

        VmConnector.__init__(self)
        self.virtualGuestName = virtualGuestName


    def vm_poweron(self):

        try:
            # Get all virtual guests that the account has:
            virtualGuests = self.client['SoftLayer_Account'].getVirtualGuests()

        except SoftLayer.SoftLayerAPIError as e:
            print("Unable to retrieve virtual list")


        # Looking for the virtual guest
        self.virtualGuestId = ''
        for virtualGuest in virtualGuests:
            if virtualGuest['hostname'] == self.virtualGuestName:
                self.virtualGuestId = virtualGuest['id']
                print("VM name is %s and id is %s" % (self.virtualGuestName,self.virtualGuestId))

        try:
            # Power on the virtual guest
            virtualMachines = self.client['SoftLayer_Virtual_Guest'].powerOn(id=self.virtualGuestId)
            print ("%s powered on" % self.virtualGuestName)

        except SoftLayer.SoftLayerAPIError as e:
            print("Unable to power on %s" % self.virtualGuestName)



class VmPowerOff(VmConnector):
    ''' This class powers down a designated VM passed in

    /* Example

    vm = 'vm-demo'
    toggle_vm = VmPowerOff(vm)
    vm_status = toggle_vm.vm_poweroff()
    */ ''' 


    def __init__(self,virtualGuestName):

        VmConnector.__init__(self)
        self.virtualGuestName = virtualGuestName


    def vm_poweroff(self):

 	try:
    	    # Get all virtual guests that the account has:
    	    virtualGuests = self.client['SoftLayer_Account'].getVirtualGuests()

	except SoftLayer.SoftLayerAPIError as e:
	    print("Unable to retrieve virtual list")


	# Looking for the virtual guest
	self.virtualGuestId = ''
	for virtualGuest in virtualGuests:
    	    if virtualGuest['hostname'] == self.virtualGuestName:
                self.virtualGuestId = virtualGuest['id']
		print("VM name is %s and id is %s" % (self.virtualGuestName,self.virtualGuestId))

        try:
            # Power off the virtual guest
            virtualMachines = self.client['SoftLayer_Virtual_Guest'].powerOff(id=self.virtualGuestId)
    	    print ("%s powered off" % self.virtualGuestName)

	except SoftLayer.SoftLayerAPIError as e:
	    print("unable to power off %s" % self.virtualGuestName)


class VmReboot(VmConnector):
    ''' This class reboots a designated VM passed in.

    /*  Example
    vm = 'vm-demo'
    toggle_vm = VmReboot(vm)
    vm_status = toggle_vm.vm_reboot()
    */'''


    def __init__(self,virtualGuestName):

        VmConnector.__init__(self)
	self.virtualGuestName = virtualGuestName


    def vm_reboot(self):

        try:
            # Getting all virtual guest that the account has:
            virtualGuests = self.client['SoftLayer_Account'].getVirtualGuests()

        except SoftLayer.SoftLayerAPIError as e:
            print("Unable to retrieve virtual guest list.")


        # Looking for the virtual guest
        virtualGuestId = ''
        for virtualGuest in virtualGuests:
            if virtualGuest['hostname'] == self.virtualGuestName:
                self.virtualGuestId = virtualGuest['id']


        # Reboot the Virtual Guest
	try:

            result = self.client['Virtual_Guest'].rebootDefault(id=self.virtualGuestId)
            pp(result)

        except SoftLayer.SoftLayerAPIError as e:
            print("Unable to reboot %s" % self.virtualGuestName)



class VmList(VmConnector):
    ''' This class returns a list of all VM's currently in use by Nanigans

    /* Example:

    vm = 'vm-demo'
    toggle_vm = VmPowerOn(vm)
    vm_status = toggle_vm.vm_poweron()
    */ '''


    def __init__(self):

        VmConnector.__init__(self)
        self.mgr = SoftLayer.VSManager(self.client)


    def vm_list(self):

        result =  self.mgr.list_instances()
        pp(result)


class VmStatus(VmConnector):

    ''' This class returns the details for a specified VM passed in.

    /* Example:
    vm = 'vm-demo'
    toggle_vm = VmStatus(vm)
    vm_status = toggle_vm.vm_status()
    */  '''

    def __init__(self,virtualGuestName):

        VmConnector.__init__(self)
        self.virtualGuestName = virtualGuestName


    def vm_status(self):

        try:
            # Getting all virtual guest that the account has:
            virtualGuests = self.client['SoftLayer_Account'].getVirtualGuests()

        except SoftLayer.SoftLayerAPIError as e:
            print("Unable to retrieve virtual guest list.")


        # Looking for the virtual guest
        self.virtualGuestId = ''
        for self.virtualGuest in virtualGuests:
            if self.virtualGuest['hostname'] == self.virtualGuestName:
                self.virtualGuestId = self.virtualGuest['id']
                parse_virtualGuestStatus(self.virtualGuest)

                return(self.virtualGuestId)

    def vm_monitor(self,vmId):
        ''' Check current pending status at SL for VM
            undergoing operations '''

        self.vmId = vmId
     
        while True:
            if self.mgr.wait_for_transaction(self.vmId, 30) == True:
                print("Server with ID %s is ready" % self.vmId)
                break
            else:
                print("Waiting for operation to complete \r")
                sys.stdout.flush()
                time.sleep(10)

        return()


def parse_virtualGuestStatus(virtualGuest):
    ''' This function can be modified to print 
        elements passed back from SL in a neater format
        or perhaps we can filter   '''

    prettyResults = {}

    for k,v in virtualGuest.items():
        print("%s => %s" % (k,v))


class VmOrderVerify(VmConnector):
    ''' class to simulate a VM order to check whether it will
        pass syntax and actually order.  Identical to class VmOrder
        but calls a verify method instead. 

        Example:
        myOrder = VmOrderVerify('vm-demo','webapp')   # test creation without ordering 
        '''

    def __init__(self,vmName,vmType):
        
        VmConnector.__init__(self)
        self.mgr = SoftLayer.VSManager(self.client)
        self.vmName = vmName
        self.vmType = vmType

        self.webapp_vsi = {
                'domain': 'nanigans.com',
                'hostname': self.vmName,
                'datacenter': 'dal10',
                'dedicated': False,
                'private': True,
                'cpus': 1,
                'os_code' : 'CentOS_6_64',
                'hourly': True,
                'ssh_keys': [1234],
                'disks': ('100','25'),
                'local_disk': True,
                'memory': 4096,
                'tags': 'demo VM'
            }

        self.minimal_vsi = {
                'domain': 'nanigans.com',
                'hostname': self.vmName,
                'datacenter': 'dal10',
                'dedicated': False,
                'private': True,
                'cpus': 1,
                'os_code' : 'CentOS_6_64',
                'hourly': True,
                'ssh_keys': [1234],
                'disks': ('100','25'),
                'local_disk': True,
                'memory': 1024,
                'tags': 'Minimal VM for demo'
            }

        if self.vmType == 'webapp':
            myVsi = self.mgr.verify_create_instance(**self.webapp_vsi)
        if self.vmType == 'minimal':
            myVsi = self.mgr.verify_create_instance(**self.minimal_vsi)

        print myVsi



class VmOrder(VmConnector):
    ''' class to handle ordering and creating vm's

        Example:
        myOrder = VmOrder(vm-demo,webapp)  # Caution will result in a charge 
        where: vm-demo is the hostname you want to set
               webapp is the VM config we want to use '''

    def __init__(self,vmName,vmType):

        VmConnector.__init__(self)
        self.mgr = SoftLayer.VSManager(self.client)
        self.vmName = vmName
        self.vmType = vmType

        self.webapp_vsi = {
                'domain': 'nanigans.com',
                'hostname': vmName,
                'datacenter': 'dal10',
                'dedicated': False,
                'private': True,
                'cpus': 1,
                'os_code' : 'CentOS_6_64',
                'hourly': True,
                'ssh_keys': [1234],
                'disks': ('100','25'),
                'local_disk': True,
                'memory': 4096,
                'tags': 'Nanigans WebApp VM'
            }

        self.minimal_vsi = {
                'domain': 'nanigans.com',
                'hostname': vmName,
                'datacenter': 'dal10',
                'dedicated': False,
                'private': True,
                'cpus': 1,
                'os_code' : 'CentOS_6_64',
                'hourly': True,
                'ssh_keys': [1234],
                'disks': ('100','25'),
                'local_disk': True,
                'memory': 1024,
                'tags': 'Nanigans Minimal VM'
            }


        if self.vmType == 'webapp':
            myVsi = self.mgr.create_instance(**self.webapp_vsi)
        if self.vmType == 'minimal':
            myVsi = self.mgr.create_instance(**self.minimal_vsi)

        # Future VM configs can go here 

        print myVsi


class VmCancel(VmConnector):
    ''' class to cancel a VM 

        Example:
        myCancel = VmCancel()	# instantiate 
        myResult = myCancel.cancelVm('vm-demo')     # cancel vm-demo
        A ticket will be created at SL if no errors '''
    

    def __init__(self):
        VmConnector.__init__(self)
        self.mgr = SoftLayer.VSManager(self.client)


    def cancelVm(self,vmname):
        ''' pass in vmname, we'll look it up, get the id
            and cancel by id '''

        self.vmname = vmname
   
        myVm = VmStatus(self.vmname)
        myVmId = myVm.vm_status()
        print("The SL ID is %s" % myVmId)
        myVmId = int(myVmId)        
        self.mgr.cancel_instance(myVmId) 

class VmReload(VmConnector):
    ''' Class to reload an instance with OS 
        Example:

    '''
    
    def __init__(self,vmName):

        self.vmName = vmName
        VmConnector.__init__(self)
        self.mgr = SoftLayer.VSManager(self.client)

    def vmReload(self):
        ''' here we take the vmname, find the SL id
            and reload by id '''

        myVm = VmStatus(self.vmName)
        myVmId = myVm.vm_status() 
        myVmId = int(myVmId)
        vsi = self.mgr.reload_instance(myVmId)     
        
        myVm.vm_monitor(myVmId)


if __name__ == '__main__':

    ''' This area for testing the module classes '''
