from datetime import datetime
import csv
import sys
import re


class Field:
    

    def __init__(self):
        __entityRegistry = {} # all entities are kept in this dictionary, searchable by type and name
        __entityIndex = 0 # increments by 1 every time a new entity is created
        __entityTypes = []
        __groupRegistry = {}
        __groupIndex = 0
        
    
    def getEntity(self, eType, eValue):
        eName = re.sub(r'\s', '_', eValue.lower())
        
        try:
            # check if entity already exists
            entity = self.__entityRegistry[eType][eName]
        except KeyError:
            # create entity
            eId = self.__entityIndex
            entity = Entity(eType, eName, eValue, eId)
            
            self.__entityIndex += 1
            self.__entityRegistry[eType][eName] = entity
        finally:
            return entity
    
    
    def getGroup(self, gName):
        if gName in self.__groupRegistry.keys():
            return self.__groupRegistry(gName)
        else:
            print('Group {} is not in this field.'.format(gName))
    
    
    def mergeGroups(self, gOne, gTwo):

        if gOne.size > gTwo.size:
            # first group wins
            gLooser = self.__groupRegistry.pop(gTwo.name)
            gOne.annexMembers(gLooser)
        else:
            # second group wins
            gLooser = self.__groupRegistry.pop(gOne.name)
            gTwo.annexMembers(gLooser)
        # field loses a group
        self.__groupIndex -= 1
    
    
    def linkEntities(self, eOne, eTwo):
        eOne.linkTo(eTwo)
        # case when the first entity's group is not set
        if eOne.group is None:
            # assuming the second entity has already a group assigned
            try:
                eTwo.group.addMember(eOne)
            # except the second entity has no group
            except AttributeError:
                gName = "G-{}".format(self.__groupIndex)
                newGroup = Group(gName)
                newGroup.addMember(eOne)
                newGroup.addMember(eTwo)
                self.__groupIndex += 1 # field gains a group
                self.__groupRegistry[gName] = newGroup
        # case when the first entity's group is set, but the second entity's is not
        elif eTwo.group is None:
            eOne.group.addMember(eTwo)
        # case when both entities have groups set and they are different groups
        elif eOne.group.name != eTwo.group.name:
            self.mergeGroups(eOne.group, eTwo.group)
    
    
    def listGroups(self, maxNr = 10):
        ''' Print the list of the clusters identified, decreasing ordered by size.
        Top ten by default if not otherwise specified.'''
        for group in self.self.__groupRegistry.values():
            pass            
    
    
    def importFromFile(self, csvFilePath, met = None):
        fileToRead = open(csvFilePath, 'r', newline='')
        csvReader = csv.reader(fileToRead, delimiter=',', dialect='excel',
                               quotechar='"')
        
        # fetch headers, replace spaces with single underscores for naming consistency
        headers =  [ re.sub(r'\s+', '_', hdr.upper()) for hdr in next(csvReader) ]
        
        # quit the process if file contains less than 2 columns
        if len(headers) < 2:
            sys.exit('Import error: not enough columns in the imported file!')
        
        # map headers to columns with dictionary comprehension
        headerDict = { value : idx for idx, value in enumerate(headers) }
        
        # assign main entity type if not already declared
        if met:
            met = re.sub(r'\s+', '_', met.upper())
            try:
                mei = headerDict.pop(met) # main entity type index
                oei = headerDict.values() # other entity types index list
            # if the main entity type provided is not in the file headers
            except KeyError:
                sys.exit('Import error: missing main entity column!')
        else:
            # assume the first column is the main entity type
            print('...setting main entity type to {}'.format(headers[0]))
            mei = 0
            oei = headerDict.values()[1:] # strip first col

        
        # update the class var listing all attribute types, including new from later imports
        for eType in headers:
            if eType not in self.__entityTypes:
                self.__entityTypes.append(eType)
            if eType not in self.__entityRegistry.keys():
                self.__entityRegistry[eType] = {}

        prevNrOfEntities = self.__entityIndex
        prevNrOfGroups = self.__groupIndex

        # main import loop begins
        for line in csvReader:
            # skip line if main entity is empty
            if line[mei] == "":
                continue
            
            mainEnt = self.getEntity(headers[mei], line[mei])
            
            for idx in oei:
                # skip if attribute is empty
                if line[idx] == "":
                    continue
                
                attribute = self.getEntity(headers[idx], line[idx])
                # add attributes to the entity, and join same group
                self.linkEntities(mainEnt, attribute)
                    
        fileToRead.close()
        
        importedEntities = self.__entityIndex - prevNrOfEntities
        importedGroups = self.__groupIndex - prevNrOfGroups
        print('Import completed. Imported {} new entities, \
        and {} group(s) created.'.format(importedEntities, importedGroups))
    
    
    def exportToFile(self, mainEntityType = None, outputFilePath = None):
        ''' '''
        pass
    
    
    def removeSingles(self):
        ''' Removing entities that are not linked to any other entity.'''
        pass
    
    
    def removeGroupsBySize(self,gSize):
        ''' Removing groups equal or smaller than specified size.'''
        pass
    

class Entity:
    
    
    def __init__(self, entType, entName, entValue, entId):
        self.type = entType
        self.name = entName
        self.value = entValue
        self.id = entId
        self.group = None
        self.linkedEnt = [] # list of linked entities
    
    
    def linkTo(self, otherEntity):
        ''' Linking operation is bi-directional, affects both entities equally.'''
        if otherEntity not in self.linkedEnt:
            # creating weak references to linked entities
            self.linkedEnt.append(otherEntity)
            otherEntity.linkedEnt(self)
    
    
    def listLinks(self):
        ''' Print the list of entities directly linked.'''
        pass


class Group:
    
    
    def __init__(self, gName):
        self.members = []
        self.name = gName
        self.size = 0
    
    
    def addMember(self, newMember):
        ''' add new group member entities to the group list '''
        if newMember not in self.members:
            self.members.append(newMember)
            self.size += 1
            newMember.group = self
    
    
    def annexMembers(self, otherGroup):
        ''' transfer members from one group to another and update members' group membership '''
        for member in otherGroup.members:
            self.addMember(member)
            member.group = self
        # remove empty group
        del otherGroup
        
        
        