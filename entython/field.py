from weakref import WeakValueDictionary, ref
from datetime import datetime
import csv
import sys
import re


class Field:

    def __init__(self):
        __mainEntityType = None # setting the main entity type
        __entityRegistry = {} # all entities are kept in this dictionary, searchable by type and name
        __entityIndex = 0 # increments by 1 every time a new entity is created   
    
    
    def addEntity(self, eType, eName):
        
        if not self.__entityRegistry[eType][eName]:
            newEntity = Entity(eType, eName, [], self.__entityIndex)
            self.__entityRegistry[eType][eName] = newEntity
        
        self.__entityIndex += 1
        
    
    def getEntity(self, eType, eName):
        pass
    
    
    def getGroup(self, gName):
        pass
    
    
    def listGroups(self, maxNr = 10):
        ''' Print the list of the clusters identified, decreasing ordered by size.
        Top ten by default if not otherwise specified.'''
    
    
    def importFromFile(self, csvFilePath, mainEnt = None):
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
        
        # assign main entity if not already created
        
        # if main entity already set, check location of main entity in the new file
        # throw error if main not in second import? import anyway?
        
        met = headers[0] # Main Entity Type, "met" for short, is always the first column
        print('...setting main entity type to {}'.format(met))
        
        
        # remove main entity from dictionary for iteration through attributes only 
        headerDict.pop(met)
        
        # remove group type from dictionary: ignoring old groups to avoid them be considered attributes
        if self.__passportHeaders[0] in headerDict.keys():
            headerDict.pop(self.__passportHeaders[0])

        aTypes = headerDict.keys()
        
        # update the class var listing all attribute types, including new from later imports
        for attrType in aTypes:
            if attrType not in self.__attributeTypes:
                self.__attributeTypes.append(attrType)
                
        # Main Entity Count
        mec = 0

        # main import loop begins
        for line in csvReader:
            # skip line if main entity is empty
            if line[0] == "":
                continue
            
            men = re.sub(r'\s', '', line[0].strip().lower()) # Main Entity Name cleaned from spaces
            mainEnt = self.getEntity(met, men, aTypes)
            mec += 1
            # assign new group (or confirm current)
            # only main entities create groups, attributes receive them and transfer them
            mainEnt.joinGroup()
            
            for attrType in aTypes:
                idx = headerDict[attrType]
                aen = re.sub(r'\s', '', line[idx].strip().lower()) # Attribute Entity Name cleaned
                # skip if attribute is empty
                if aen == "":
                    continue
                
                attribute = self.getEntity(attrType, aen, [met])
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
    
    def __init__(self, entType, entName, entId):
        self.type = entType
        self.name = entName
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
        
        
        