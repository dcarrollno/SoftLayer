
''' This file is part of the SL API package 
    and contains classes and methods called by
    other programs we use to manage our SoftLayer
    presence. '''

import os
import SoftLayer
import config
import pprint


pp = pprint.PrettyPrinter(indent=4)


class ImageConnector(object):
    ''' This class sets up the SoftLayer connection '''

    def __init__(self):

        self.client = config.client
        self.mgr  = SoftLayer.ImageManager(self.client)


class GetImgList(ImageConnector):
    ''' This class gets the image list '''

    def __init__(self):
        ImageConnector.__init__(self)


    def getPriImgList(self):

        result = self.mgr.list_private_images()
        pp.pprint(result)


    def getPubImgList(self):
        ''' This is a list of OS images by SL '''
   
        result = self.mgr.list_public_images()
        pp.pprint(result)


class GetImageInfo(ImageConnector):
    ''' Expects an image id to be passed in '''

    def __init__(self,id):

        ImageConnector.__init__(self) 

        if isinstance(id, int):
            self.id = id
            self.getImageInfo()
        if isinstance(id, str):
            self.name = id
            self.getIdFromName()

 
    def getImageInfo(self):

        result = self.mgr.get_image(self.id)
        print("ID: %s   Name: %s" % (result['id'],result['name']))


    def getIdFromName(self):
        
        result = self.mgr._get_ids_from_name_private(self.name)
        pp.pprint(result) 


if __name__ == '__main__':


    # Examples
   
    # Get Private Image List
    #res = GetImgList().getPriImgList()
   
    # Get Public Image List - OS images by SL
    #res = GetImgList().getPubImgList()

    # Get Image Info on Specific Image by id
    #res = GetImageInfo(1343957)    # or res = GetImageInfo('vm-demo')


