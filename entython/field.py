from weakref import WeakValueDictionary, ref
from datetime import datetime
import csv
import sys
import re


class Field:

    def __init__(self):
        __entityRegistry = {} # all entities are kept in this dictionary, searchable by type and name
        __entityIndex = 0 # increments by 1 every time a new entity is created
        __entityTypes = []
        
    
    def getEntity(self, eType, eValue):
        eName = re.sub(r'\s', '', eValue.strip().lower())
        
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
        pass
    
    
    def listGroups(self, maxNr = 10):
        ''' Print the list of the clusters identified, decreasing ordered by size.
        Top ten by default if not otherwise specified.'''
    
    
    def importFromFile(self, csvFilePath, met = None):
        fileToRead = open(csvFilePath, 'r', newline='')
        csvReader = csv.reader(fileToRead, delimiter=',', dialect='excel',
                               quotechar='"')
        
        # fetch headers and cleaning them up
        headers = [ re.sub(r'\s', '', hdr.strip().upper()) for hdr in next(csvReader) ]
        
        # quit the process if file contains less than 2 columns
        if len(headers) < 2:
            sys.exit('Import error: not enough columns in the imported file!')
        
        # map headers to columns with dictionary comprehension
        headerDict = { value : idx for idx, value in enumerate(headers) }
        
        # assign main entity type if not already created
        if met:
            try:
                mei = headerDict[met]
                headerDict.pop(met)
            # if the main entity type provided is not in the file headers
            except KeyError:
                sys.exit('Import error: missing main entity column!')
        else:
            # assume the first column is the main entity type
            met = headers[0]
            print('...setting main entity type to {}'.format(met))
            mei = headerDict[met] # main entity index in the headers
            headerDict.pop(met)

        
        # update the class var listing all attribute types, including new from later imports
        for eType in headers:
            if eType not in self.__entityTypes:
                self.__entityTypes.append(eType)
            if eType not in self.__entityRegistry.keys():
                self.__entityRegistry[eType] = {}
                
        # Main Entity Count
        mec = 0

        # main import loop begins
        for line in csvReader:
            # skip line if main entity is empty
            if line[mei] == "":
                continue
            
            mainEnt = self.getEntity(met, line[mei])
            mec += 1
            # assign new group (or confirm current)
            # only main entities create groups, attributes receive them and transfer them
            mainEnt.joinGroup()
            
            for attrType in aTypes:
                idx = headerDict[attrType]
                # skip if attribute is empty
                if line[idx] == "":
                    continue
                
                attribute = self.getEntity(attrType, line[idx])
                # add attributes to the entity, and join same group
                mainEnt.linkTo(attribute)
                    
        fileToRead.close()
        
        gn = len(Group._Group__groupInstances)
        
        print('Import completed. Imported {} new entities type "{}", in {} group(s).'.format(mec, met, gn))
    
    
    def exportToFile(self):
        pass
    
    
    def setMainEntity(self, mainEnType):
        ''' Main entity type is used to define which entity type is more relevant
        in relation to the current Field. It is also used to organize the export
        output.'''
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
    
    
    def joinGroup(self, otherEntity):
        # case when the native entity's group is not set
        if self.group is None:
            # assuming the other entity has already a group assigned
            try:
                otherEntity.group.addMember(self)
            # except the other entity has no group
            except AttributeError:
                newGroup = Group()
                newGroup.addMember(self)
                newGroup.addMember(otherEntity)
        # case when the native entity's group is set
        else:
            thisSize = self.group.size
            # assuming the other entity has a group already assigned
            try:
                otherSize = otherEntity.group.size
            # except the other entity has no group
            except AttributeError:
                self.group.addMember(otherEntity)
            else:
                if otherSize > thisSize:
                    # alien entity wins
                    otherEntity.group.annexMembers(self.group)
                else:
                    # native entity wins
                    self.group.annexMembers(otherEntity.group)
    
    
    def linkTo(self, otherEntity):
        ''' Linking operation is bi-directional, affects both entities equally.'''
        if ref(otherEntity) not in self.linkedEnt:
            # creating weak references to linked entities
            self.linkedEnt.append(ref(otherEntity))
            otherEntity.linkedEnt(ref(self))
            self.joinGroup(otherEntity)
    
    
    def listLinks(self):
        ''' Print the list of entities directly linked.'''
        pass


class Group:
    __groupCount = 0 # for naming purpose only
    __groupInstances = WeakValueDictionary()
    
    
    def __init__(self):
        Group.__groupCount += 1
        self.members = []
        self.name = "G-%d" % Group.__groupCount
        self.size = 0
        Group.__groupInstances[self.name] = self
    
    
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
        
        
        