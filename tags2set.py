#!/usr/bin/python

import sys, os, shelve, logging,string
from ConfigParser import *
import flickr

existingSets = None
user = None
configdict = ConfigParser()
configdict.read('uploadr.ini')
onlySubs = configdict.defaults()['only_sub_sets'] #set to true if Sets should be called only by the name of the last subfolder

def  creatSet(photoSet, setName):
    setName = setName.replace('\\',' ')
    setName = setName.replace('/',' ')
    setName = string.strip(setName)
    photos = [] #real photo objects
    for p in photoSet:
            photos.append(flickr.Photo(id = p))

    fset = None
    #check if set with the name exists already 
    for s in existingSets:
            if(s.title == setName):
                    fset= s
                    logging.debug('tags2set: Found existing set %s' % setName)
                   # return
                    break
    try:                  
        if(fset == None):
                print photos[0]
                print setName
                fset = flickr.Photoset.create(photos[0], setName, 'auto generated by folders2flickr')
                logging.debug('tags2set: Creating new set %s' % setName)
    except:
        logging.error('tags2set: Cannot create set %s' % setName)
        logging.error(sys.exc_info()[0])

    try:    
        fset.editPhotos(photos)
    except:
        logging.error('tags2set: Cannot edit set %s' % setName)
        logging.error(sys.exc_info()[0])

        
    logging.debug('tags2set: ...added %d photos' % len(photos)  )
    return fset


def createSets( historyFile):
     global existingSets
     global user
    
     logging.debug('tags2set: Started tags2set')
     try:
         user = flickr.test_login()
         logging.debug(user.id)
         existingSets=user.getPhotosets()
     except:
         logging.error(sys.exc_info()[0])
         return None
     
     uploaded = shelve.open( historyFile )
     keys = uploaded.keys()
     keys.sort()
     lastSetName =''
     photoSet =[]
     setName = ''
     for image in keys:
        if(image.startswith('\\') or image.startswith('/')): #filter out photoid keys
            if(onlySubs.startswith('true')):
                head, setName = os.path.split(os.path.dirname(image))
            else:
                setName = os.path.dirname(image) #set name is realy a directory
                    
            if(not lastSetName == setName and not lastSetName == ''):
                #new set is starting so save last
                #logging.debug( "Creating set %s with %d pictures" % (lastSetName, len(photoSet)) )
                creatSet(photoSet, lastSetName)
                photoSet = []
            logging.debug("tags2set: Adding image %s" % image)
            photoSet.append(uploaded.get(image))
            lastSetName = setName
          
                
     #dont forget to create last set
     #logging.debug( "Creating set %s with %d pictures" % (setName, len(photoSet)) )
     creatSet(photoSet, setName)
     

