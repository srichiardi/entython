from weakref import WeakValueDictionary, ref
from datetime import datetime
import csv
import sys
import re


class Field:

    def __init__(self):
        __mainEntityType = '' # setting the main entity type
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
    
    
    def importFromFile(self, csvFilePath):
        pass
    
    
    def exportToFile(self):
        pass
    
    
    def setMainEntity(self):
        ''' Main entity type is used to define which entity type is more relevant
        in relation to the current Field. It is also used to organize the export
        output'''
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
        
        
        