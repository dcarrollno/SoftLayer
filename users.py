#!/usr/bin/env python


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
        user operations '''

    itTeam = { 'SL12345'         : 12345,
               'employee1'       : 123456,
               'employee2'       : 123445,
               'employee3'       : 123445,
               'employee4'       : 123457
               }


    def __init__(self,username='None',email='None',
                 firstname='None', lastname='None',
                 password='None', sluid='None'):

        self.client     = config.client
        self.username   = username
        self.email      = email
        self.firstname  = firstname
        self.lastname   = lastname
        self.sluid      = str(sluid)
        self.password   = password



    def _url(self,path):
        ''' Helper function. We do not pass POST requests
            thru here with json data payloads '''

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
                    "address1": "123 Example St.",
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
                "P@s$w0rRd!?",
                "P@s$w0rRd!?"
            ]
        }

        restreq = self._url('SoftLayer_User_Customer/createObject.json')
        #print(restreq+"""',"""+' json=hwlist')
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
                    "userStatusId": 1002
                }
            ]
        } 

        restreq = self._url('SoftLayer_User_Customer/'+self.sluid+'/editObject.json')
        #print(restreq+"""',"""+' json=hwlist')
        r = requests.post(restreq, json=delete_template)
        pp(r)
        pp(r.json())



    def find_user_by_email(self):
        ''' This method locates a user by email address.

        /* Example
        myInst = UserManager(email='dave@nanigans.com')
        test = myInst.find_user_by_email()
        print(test)     # api return code
        pp(test.json())
        */ '''

        return requests.get(self._url('SoftLayer_Account/Users.json?objectMask=mask[username,firstName,lastName,id,email]&objectFilter={"users":{"email":{"operation":"'+self.email+'"}}}'))



    def find_user_by_username(self):
        ''' This method locates a user by their username 

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
        result = r.json()

        if 'SoftLayer_Exception_Public' in result['code']:
            print("Exception found - checking error")
        else:
            print("Unknown error.")
            return()
        if 'OpenIdConnect' in result['error']:
            print("OpenIdConnect error - the SL API will not work with blueid")
            return()



    def set_user_vpn_password(self,myPass='P@s$w0Rrd!?'):
        ''' method to set a user's vpn password. We can burn in a default
            or pass a password parameter to set one.

        /* Example:
        myInst = UserManager(sluid='136924')
        setpw = myInst.set_user_vpn_password(myPass='P@s$w0Rrd!?')
        */ '''

        self.myPass = myPass

        myPass = {
            "parameters" : [self.myPass]
        }

        restreq = self._url('SoftLayer_User_Customer/'+self.sluid+'/updateVpnPassword.json')
        #print(restreq+"""',"""+' json=hwlist')
        r = requests.post(restreq, json=myPass)
        pp(r)
        pp(r.json())



    def set_user_vpn_status(self,ssl='None',pptp='None'):
        ''' Enable/disable SSLVpn or PPTPVpn.  We expect bool True or
            False to be passed in accordingly. We might call this method
            during a user set up function. 

        /* Example:
        myInst = UserManager(sluid='632554')
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
        #print(restreq+"""',"""+' json=hwlist')
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
        myInst = UserManager(sluid='1369424')
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
        #print(restreq+"""',"""+' json=myHwlist')
        r = requests.post(restreq, json=myHwlist) 



    def bulk_add_device_access(self):
        ''' This method adds user access to specified hardware devices. 

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
                [ "125015","101912" ]
             ]
           }
        */ '''

        myHwlist = { "parameters" : [ hwList ] }      # add all
        self.slUsers = self.get_all_sluids()	
        #self.slUsers = ['334759','136654']

        for eachUser in self.slUsers:
            restreq = self._url('SoftLayer_User_Customer/'+eachUser+'/addBulkHardwareAccess.json')
            #print(restreq+"""',"""+' json=myHwlist')
            r = requests.post(restreq, json=myHwlist)



    def get_all_portal_perms(self):
        ''' Portal permissions allow viewing of devices in portal or use of API. This method
            pulls a list of all possible portal perms so we can build access rules and apply 
            them later.  We typically call this method from another method. '''

        g = requests.get(self._url('SoftLayer_User_Customer_CustomerPermission_Permission/getAllObjects.json'))
        #pp(g)
        perms = g.json()
        return(perms)



    def get_user_portal_perms(self):
        ''' Method to get user's portal perms '''

        g = requests.get(self._url('SoftLayer_User_Customer/'+self.sluid+'/getPermissions.json'))
        pp(g) 
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
        ''' If we remove portal perms for users, we don't really need 
            to use this method but it is here for reference. We call this 
            method by uid and remove all hardware access by that uid.

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
           [ "125015","101912" ]
         ]
        }  
        */ '''

        myHwlist = { "parameters" : [ hwList ] }	# remove all

        restreq = self._url('SoftLayer_User_Customer/'+self.sluid+'/removeBulkHardwareAccess.json')
        #print(restreq+"""',"""+' json=myHwlist')
        r = requests.post(restreq, json=myHwlist)	



    def set_default_portal_perms(self):
        ''' Here we set default user perms in the portal.
            We disable all perms as we do not want this user
            to have any perms unless they are IT. '''

        self.perms = self.get_all_portal_perms()

        ''' No longer used
        sslperms = []
        for d in self.perms:
            for k,v in d.items():
                if 'SSL_VPN_ENABLED' in d.values():
                    #print("Key is %s and VAL is %s" % (k,v))
                    if d not in sslperms:
                        sslperms.append(d)
                        print sslperms
        '''


        default_perms = {
            "parameters": [
                self.perms
            ]
        }

        sslvpn_perms = {
            "parameters": [ { "keyName" : "SSL_VPN_ENABLED" } ]
        }


        restreq = self._url('SoftLayer_User_Customer/'+self.sluid+'/removeBulkPortalPermission.json')
        #print(restreq)
        r = requests.post(restreq, json=default_perms)

        restreq2 = self._url('SoftLayer_User_Customer/'+self.sluid+'/addPortalPermission.json')
        r2 = requests.post(restreq2, json=sslvpn_perms)


    def bulk_remove_portal_perms_for_all(self):
        ''' This method applies our default portal permissions to users.
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

        sslvpn_perms = {
            "parameters": [ { "keyName" : "SSL_VPN_ENABLED" } ]
        }


        for eachUser in self.slUsers:
            if eachUser not in self.itTeam.values():
                #restreq = self._url('SoftLayer_User_Customer/'+eachUser+'/removeBulkPortalPermission.json')
                #print(restreq)
                #r = requests.post(restreq, json=default_perms)
                #restreq2 = self._url('SoftLayer_User_Customer/'+self.sluid+'/addPortalPermission.json')
                #r2 = requests.post(restreq2, json=sslvpn_perms)
                #pp(r2)
                #pp(r2.json())
                print("User %s not in ITGroup" % eachUser)
            if eachUser in self.itTeam.values():
                print("Ignoring perms changes for %s" % eachUser)
                next


    def get_timezone(self):

        return requests.get(self._url('SoftLayer_Locale_Timezone/getAllObjects.json'))



if __name__ == '__main__':

    '''  This area for testing '''
    pass

