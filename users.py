'''
 /*  This file is part of the SL_API package
 /*
 /* Dave Carroll 2016
 /*                                               

This class uses the SoftLayer Rest API vs. Service Mgr.

https://[username]:[apiKey]@api.[service.]softlayer.com/rest/v3/
[serviceName]/[initializationParameter].[returnDatatype]

https://sldn.softlayer.com/article/REST

'''

import os
import sys
import requests
import json
import config
from hw_info import GetHardware
from pprint import pprint as pp


class UserManager(object):
    ''' This class is responsible for managing SoftLayer
        user operations and is part of a collection of 
	SoftLayer API code ''' 

    # The following are IT-Ops team members and 
    # have special privs.

    itTeam = { 'SLxxxxx'     : 123456,
               'userxxx'     : 123456,
               'userxxx'     : 123456,
               'userxxx'     : 123345,
               'userxxx'     : 123451
             }


    def __init__(self,username='None',email='None',
                firstname='None', lastname='None',
                password='None', sluid='None'):

        self.client = config.client
        self.username = username
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.sluid = sluid
        self.password = password



    def _url(self,path):
        ''' Helper function.  '''

        #print('https://'+config.nanuser+':'+config.nankey+'@api.softlayer.com/rest/v3/'+path)
        return('https://'+config.nanuser+':'+config.nankey+'@api.softlayer.com/rest/v3/'+path)


    def create_user(self):
        ''' This method allows for the creation of a new 
	    SL user.  

        /* TimeZone IDs:  108=PST, 120=EST, 
        */ '''

	user_template = {
  	      "parameters": [
                 {
                    "address1": "123 Your Address Here",
                    "city": "Boston",
                    "companyName": "ACME Inc.",
                    "state": "MA",
                    "country": "US",
                    "postalCode": "02109",
                    "firstName": self.firstname,
                    "lastName": self.lastname,
                    "email": self.email,
                    "permissionSystemVersion": "1",
                    "timezoneId": "120",
                    "username": self.username,
                    "userStatusId": 1001
                 },
                "P@s$w0rd!?",
                "P@s$w0rd!?"
               ]
             }

        restreq = self._url('SoftLayer_User_Customer/createObject.json')
        r = requests.post(restreq, json=user_template)
        pp(r)
        pp(r.json()) 



    def disable_user(self):
        '''  Here we can flag a user for disable.

        /* Possible status id's include
	1001 = Active;
	1002 = Disabled; 
	1003 = Inactive; 
	1021 = cancel_pending;
	1022 = VPN Only 
	*/ '''

	delete_template = {
       	   "parameters": [
            {
             "userStatusId": 1021
            }
          ]
        } 
 
        restreq = self._url('SoftLayer_User_Customer/'+self.sluid+'editObject.json')
        r = requests.post(restreq, json=delete_template)
        pp(r)
        pp(r.json())



    def find_user_by_email(self):
	''' This method locates a user by email address.

        /* Example
        myInst = UserManager(email='user@acme.com')
        test = myInst.find_user_by_email()
        print(test)     # api return code
        pp(test.json())
        */ '''
	
        return requests.get(self._url('SoftLayer_Account/Users.json?objectMask=mask[username,firstName,lastName,id,email]&objectFilter={"users":{"email":{"operation":"'+self.email+'"}}}'))



    def find_user_by_username(self):
	''' This method locates a user by their username within SoftLayer

        /* Example:
        myInst = UserManager(username='myuser')
        test = myInst.find_user_by_username()
        print(test)     # api return code
        pp(test.json())
        */ '''

        return requests.get(self._url('SoftLayer_Account/Users.json?objectMask=mask[username,firstName,lastName,id,email]&objectFilter={"users":{"username":{"operation":"'+self.username+'"}}}'))



    def get_all_user_info(self):
	''' This method returns all info related to a supplied uid. We typically
	    would call this method from another method once we obtain a uid by
	    username or email. 

	/* Example: 
	myInst = UserManager(sluid='12344')
	getInfo = myInst.get_all_user_info()
	*/ '''

	return requests.get(self._url('SoftLayer_User_Customer/'+self.sluid+'.json'))



    def set_user_password(self):
	''' This method initiates a portal password reset process. Pass in a 
	    SL username. 

 	/* Example:
	myInst = UserManager(username='smith')
        setpw = myInst.set_user_password()
	*/ '''

        myUser = {
	   "parameters" : [self.username]
        }

        restreq = self._url('SoftLayer_User_Customer/initiatePortalPasswordChange.json')
        r = requests.post(restreq, json=myUser)
        pp(r)
        pp(r.json())



    def set_user_vpn_password(self,myPass='Z@h$e0rc!?'):
	''' method to set a user's vpn password. We can burn in a default
	    or pass a password parameter to set one.
 
        /* Example:
	myInst = UserManager(sluid='123456')
    	setpw = myInst.set_user_vpn_password(myPass='Z@h$e0rc!?')
	*/ '''

        self.myPass = myPass

        myPass = {
 	    "parameters" : [self.myPass]
        }

        restreq = self._url('SoftLayer_User_Customer/'+self.sluid+'/updateVpnPassword.json')
        r = requests.post(restreq, json=myPass)
        pp(r)
        pp(r.json())



    def set_user_vpn_status(self,ssl='None',pptp='None'):
	''' Enable/disable SSLVpn or PPTPVpn.  We expect bool True or
            False to be passed in accordingly. We might call this method
	    during a user set up function. 

	/* Example:
    	myInst = UserManager(sluid='12345')
    	setpw = myInst.set_user_vpn_status(ssl=True,pptp=False)
    	pp(setpw)
    	pp(setpw.json()) 
	*/ '''

        self.ssl = ssl
        self.pptp = pptp

        templateObject = {
                   "parameters" :  [
	            { "id" : self.sluid,
		      "sslVpnAllowedFlag" : self.ssl,
		      "pptpVpnAllowedFlag" : self.pptp }
                   ]
                 }

        restreq = self._url('SoftLayer_User_Customer/'+self.sluid+'/editObject.json')
        r = requests.post(restreq, json=templateObject)
        pp(r)
	pp(r.json())



    def get_user_status(self):
	''' Method to determine user status at SoftLayer. This returns
	    a status code to suggest whether a user account is enabled and
 	    active or disabled.  We call this by uid. '''

        return requests.get(self._url('SoftLayer_User_Customer/'+self.sluid+'/getUserStatus'))



    def get_user_hardware(self):
	''' Get all hardware devices user has perms to access in portal. This 
            should be none most times other than for IT admins. We don't need
            users viewing hardware details, OS passwords etc.. 

        /* Example:
    	myInst = UserManager(sluid='12345')
        gethw = myInst.get_user_hardware()
        pp(gethw)
        pp(gethw.json()) 
 	*/ '''

        return requests.get(self._url('SoftLayer_User_Customer/'+self.sluid+'/getHardware.json'))


    def set_default_device_access(self):
        ''' Here we set the default device access for the user
            which is basically allow-all.  '''

        hwList = []
        myHwList = GetHardware()
        hwlist = myHwList.get_hardware()
        pp(hwlist)  # status code
        hwids = hwlist.json()
        for i in hwids:
            hwList.append(i.values())
        hwList = [item for sublist in hwList for item in sublist]
        myHwlist = { "parameters" : [ hwList ] }   
        restreq = self._url('SoftLayer_User_Customer/'+self.sluid+'/addBulkHardwareAccess.json')
        r = requests.post(restreq, json=myHwlist) 

	

    def bulk_add_device_access(self):
        ''' This method adds user access to specified hardware devices. We use this to
            move through our entire user list and set default device access. This method
            is mainly a clean up function.   

        /* Example call:
        myInst = UserManager()
        addhw = myInst.bulk_add_device_access()
        pp(addhw)       # get status code
        gethw = myInst.get_user_hardware()      # Check hw access has been removed
        pp(gethw)
        pp(gethw.json())
        */ '''

        hwList = []
        myHwList = GetHardware()
        hwlist = myHwList.get_hardware()
        pp(hwlist)  # status code
        hwids = hwlist.json()
        for i in hwids:
            hwList.append(i.values())
        hwList = [item for sublist in hwList for item in sublist]

        ''' /* Example of adding access to two systems
        hwlist = {
          "parameters": [
           [ "12315","12912" ]
         ]
        }
        */ '''

        myHwlist = { "parameters" : [ hwList ] }      # add all
	self.slUsers = self.get_all_sluids()	

        for eachUser in self.slUsers:
            restreq = self._url('SoftLayer_User_Customer/'+eachUser+'/addBulkHardwareAccess.json')
            r = requests.post(restreq, json=myHwlist)



    def get_all_portal_perms(self):
        ''' Portal permissions allow viewing of devices in portal or use of API. This method
	    pulls a list of all possible portal perms so we can build access rules and apply 
            them later.  We typically call this method from another method as part of a setup
            process. '''

        g = requests.get(self._url('SoftLayer_User_Customer_CustomerPermission_Permission/getAllObjects.json'))
        perms = g.json()
	return(perms)



    def get_all_sluids(self):
        ''' We get a list of all SL uids so we can run opertions on them later. We use this
	    method to build lists of users to work off in other methods. '''
   
        slUsers = []
        g = requests.get(self._url('SoftLayer_Account/Users.json?objectMask=mask[id]'))
        pp(g)
        uids = g.json()
        for i in uids:
            slUsers.append(i.values())
 	slUsers = [item for sublist in slUsers for item in sublist]
	return(slUsers)

	         

    def bulk_remove_device_access(self):
        ''' This method allow us to mass apply a policy to remove all
            device access for a set of users or all users other than our
            IT group. '''


        /* Example call:
        myInst = UserManager(sluid='12345')
        remhw = myInst.bulk_remove_device_access()
        pp(remhw)	# get status code
        gethw = myInst.get_user_hardware()	# Check hw access has been removed
        pp(gethw)
        pp(gethw.json())
	*/ ''' 

        hwList = []
        myHwList = GetHardware() 
        hwlist = myHwList.get_hardware()
	pp(hwlist)  # status code
	hwids = hwlist.json()
	for i in hwids:
	    hwList.append(i.values())
	hwList = [item for sublist in hwList for item in sublist]

	''' /* Example of removing access to two systems
        hwlist = {
          "parameters": [
           [ "12235","21912" ]
         ]
        }  
        */ '''

	myHwlist = { "parameters" : [ hwList ] }	# remove all

        restreq = self._url('SoftLayer_User_Customer/'+self.sluid+'/removeBulkHardwareAccess.json')
        r = requests.post(restreq, json=myHwlist)	



    def set_default_portal_perms(self):
        ''' Here we set default user perms in the portal.
            We disable all perms as we do not want this user
            to have any perms unless they are IT. '''

        self.perms = self.get_all_portal_perms()

        default_perms = {
            "parameters": [
                self.perms
               ]
            }

        restreq = self._url('SoftLayer_User_Customer/'+self.sluid+'/removeBulkPortalPermission.json')
        return requests.post(restreq, json=default_perms)


    def bulk_remove_portal_perms_for_all(self):
        ''' This method applies our default portal permissions to all users.
            We apply this to all users to deny ability to view details in portal. 

        /* Example:
            #Bulk apply zero portal perms to all users other than IT
    	    myInst = UserManager()
            setperms = myInst.bulk_remove_portal_perms()
            pp(setperms)           

        */ '''

        self.perms = self.get_all_portal_perms()
        self.slUsers = self.get_all_sluids()      
 
	# Set default perms to the perms json blob obtained from above and then apply remove all

	default_perms = {
  	    "parameters": [
                self.perms
               ]
             }  

        for eachUser in self.slUsers:
            if eachUser not in self.itTeam.values():
                restreq = self._url('SoftLayer_User_Customer/'+eachUser+'/removeBulkPortalPermission.json')
                r = requests.post(restreq, json=default_perms)
		print("User %s not in ITGroup" % eachUser)
            if eachUser in self.itTeam.values():
		print("Ignoring perms changes for %s" % eachUser)
		next

