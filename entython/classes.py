from weakref import WeakValueDictionary
from datetime import datetime
import csv
import sys
import re


class Field:
    

    def __init__(self):
        self._entityRegistry = {} # all entities are kept in this dictionary, searchable by type and name
        self._entityIndex = 0
        self._groupRegistry = {}
        self._edgeRegistry = {}
        
    
    def getEntity(self, eType, eValue):
        eType = re.sub(r'\s+', '_', type.upper())
        eName = re.sub(r'\s+', '_', eValue.lower())
        try:
            # check if entity already exists
            entity = self._entityRegistry[eType][eName]
        except KeyError:
            # create entity linked to this field
            entity = Entity(eType, eName, self)
        finally:
            return entity
        
        
    def registerEntity(self, entity):
        self._entityIndex += 1
        self._entityRegistry[entity.type][entity.name] = entity
    
    
    def registerEdge(self, edge):
        self._edgeRegistry[edge.id] = edge
        
        
    def eliminateEdge(self, edgeId):
        del self._edgeRegistry[edgeId]
        
        
    def registerGroup(self, group):
        self._groupRegistry[group.name] = group
        
        
    def eliminateGroup(self, group):
        del self._groupRegistry[group.name]
    
    
    def getGroup(self, gName):
        if gName in self._groupRegistry.keys():
            return self._groupRegistry(gName)
        else:
            print('Group {} is not in this field.'.format(gName))

        
    def listGroups(self, maxNr = 10):
        ''' Print the list of the clusters identified, decreasing ordered by size.
        Top ten by default if not otherwise specified.'''
        pass
        
        
    def countLinksByType(self):
        ''' Return a dictionary with counts of nr of links broken down by entity type.'''
        linksDistribution = {}
        for edge in self.__edgeRegistry:
            eOne, eTwo = edge.couple
            # repeat the loop twice, once for each entity
            for i in range(2):
                # first entity type never seen before
                if eOne.type not in linksDistribution.keys():
                    linksDistribution[eOne.type] = { eTwo.type : { 'listOfUniq' : [eTwo.value],
                                                                'count' : 1 }
                                                    }
                # first entity type already present, but not second entity type
                elif eTwo.type not in linksDistribution[eOne.type].keys():
                    linksDistribution[eOne.type][eTwo.type] = { 'listOfUniq' : [eTwo.value],
                                                                'count' : 1 }
                # linked entity name not yet counted
                elif eTwo.value not in linksDistribution[eOne.type][eTwo.type]['listOfUniq']:
                    linksDistribution[eOne.type][eTwo.type]['count'] += 1
                # invert values and repeat loop
                eTwo, eOne = edge.couple
        
        # summary dictionary
        sumDict = {}
        for typeOne in linksDistribution.keys():
            sumDict[typeOne] = { 'link_total' : 0,
                                'link_types' : 0 }
            for typeTwo in linksDistribution[typeOne].keys():
                sumDict[typeOne]['link_total'] += linksDistribution[typeOne][typeTwo]['count']
                sumDict[typeOne]['link_types'] += 1
        
        return sumDict
        
    
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
        
        # assign main entity type if not already declared, assign mei and oei for main loop
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
            if eType not in self.__entityTypes.keys():
                self.__entityTypes[eType] = {}

        prevNrOfEntities = self.__entityIndex
        prevNrOfGroups = len(self.__groupRegistry.keys())

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
                mainEnt.linkTo(attribute)
                    
        fileToRead.close()
        
        importedEntities = self.__entityIndex - prevNrOfEntities
        importedGroups = len(self.__groupRegistry.keys()) - prevNrOfGroups
        print('Import completed. Imported {} new entities, \
        and {} group(s) created.'.format(importedEntities, importedGroups))
    
    
    def exportToFile(self, mainEntityType = None, outputFilePath = None):
        ''' Save the most linked entity to a csv file.'''
        # request output file path if not passed as argument
        
        # if not determine the most linked entity type if not passed as argument
        if mainEntityType is None:
            pass
        
        # loop through the data and save in file
        pass
    
    
    def removeSingles(self):
        ''' Removing entities that are not linked to any other entity.'''
        pass
    
    
    def removeGroupsBySize(self,gSize):
        ''' Removing groups equal or smaller than specified size.'''
        pass
    

class Entity:
    
    
    def __init__(self, entType, entValue, entField):
        if isinstance(entField, Field):
            self.type = entType
            self.value = entValue
            self.field = entField
            self.group = None
            self.links = WeakValueDictionary() # dict of linked entities
            self.field.registerEntity(self) # update the entity registry
        else:
            raise TypeError("Invalid field argument, field instance expected!")
    
    
    def linkTo(self, eTwo):
        ''' Linking operation is bi-directional, affects both entities equally.'''
        # check if entities not already linked
        if Edge.linkId(self, eTwo) not in self.links.keys():
            # update both entities' list of links
            # create a new edge
            newlink = Edge(self, eTwo, self.field)
            self.links[newlink.id] = eTwo
            eTwo.links[newlink.id] = self
            # case when the first entity's group is not set
            if self.group is None:
                # assuming the second entity has already a group assigned
                try:
                    eTwo.group.addMember(self)
                # except the second entity has no group
                except AttributeError:
                    newGroup = Group(self.field)
                    newGroup.addMember(self)
                    newGroup.addMember(eTwo)
                    
            # case when the first entity's group is set, but the second entity's is not
            elif eTwo.group is None:
                self.group.addMember(eTwo)
            
            # case when both entities have groups set and they are different groups
            elif self.group.name != eTwo.group.name:
                if self.group.size > eTwo.group.size:
                    # first group wins
                    self.group.annexMembers(eTwo.group)
                else:
                    # second group wins
                    eTwo.group.annexMembers(self.group)
    
    
    def getLinks(self):
        ''' Print the list of entities directly linked.'''
        return self.links.values()
    
    
    def removeLink(self, eTwo):
        ''' Remove linked entity.'''
        linkId = Edge.linkId(self, eTwo)
        self.links.pop(linkId)
    
    
    def __repr__(self):
        return repr(self.value)
    
    
    def __del__(self):
        ''' Delete itself from linked entities, and delete links.'''
        # remove link from linked entity necessary? no because it's a weaklink
        for linkId in self.links.keys():
            self.field.eliminateEdge(linkId)
            
        del self
    

class Edge:
    
    
    def __init__(self, eOne, eTwo, field):
        self.couple = (eOne, eTwo)
        self.field = field
        self.id = Edge.linkId(eOne, eTwo)
        self.field.registerEdge(self)
    
    
    def __repr__(self):
        return repr(self.id)
    
    
    @classmethod
    def linkId(cls, eOne, eTwo):
        ''' Generating a string with the two entity names sorted.'''
        firstEntity, secondEntity = sorted([eOne.value, eTwo.value])
        return '{}-{}'.format(firstEntity, secondEntity)


class Group:
    
    __groupIndex = 0 # naming purpose only
    
    
    def __init__(self, gField):
        self.members = []
        self.name = "G-{}".format(Group.__groupIndex)
        self.field = gField
        self.size = 0
        self.field.registerGroup(self)
        Group._groupIndex += 1
    
    
    def __repr__(self):
        return repr(self.name)
    
    
    def __del__(self):
        for entity in self.members:
            del entity
        self.field.eliminateGroup(self)
        del self
    
    
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
        self.field.eliminateGroup(otherGroup)
        del otherGroup
        
        
