from weakref import WeakValueDictionary
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
    
    def __init__(self, entType, entName, entId, attrTypes=[]):
        self.type = entType
        self.name = entName
        self.group = None
        self.attributes = {}
        for item in attrTypes:
            self.attributes[item] = []
    
    
    def joinGroup(self):
        pass
    
    
    def linkTo(self, ontherEntity):
        ''' Linking creates an edge'''
        pass
    
    
    def listLinks(self):
        ''' Print the list of entities directly linked.'''


class Edge:
    
    def __init__(self, entOne, entTwo):
        idList = sorted([entOne.id, entTwo.id])
        self.id = '{}.{}'.format(idList[0], idList[1]) 
        pass
    
    
    def getLinked(self, sourceEnt):
        pass


class Group:
    
    def __init__(self):
        pass
