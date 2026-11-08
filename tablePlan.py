import numpy as np
from ortools.sat.python import cp_model
import table
import math

def fitnessScore(arrangement, visitorPrefs, knownPositions):
    score = 0

    for i in range(arrangement.shape[0]):
        for j in range(arrangement.shape[1]):
            table = arrangement[i][j]

            for k in range(len(table.members)):
                for l in range(len(visitorPrefs[k])):
                    friend = visitorPrefs[k][l]
                    if(np.any(friend) == table.members):
                        score += 1
                    else:
                        i1,j1 = knownPositions[friend]
                        distanceRaw = math.sqrt((i-i1)**2 + (j-j1)**2)
                        distanceFactor = np.exp(-distanceRaw)
                        score += 1 * distanceFactor  

    return score

class tablePlan:
    def __init__(self, seatingMap, friendsDict, sizeDict, numAnneals):
        self.seatingMap = seatingMap
        self.friendsDict = friendsDict
        self.sizeDict = sizeDict
        self.numAnneals = numAnneals
    
    def createTables(self):
        tablesArr = np.array(self.seatingMap.shape[0],self.seatingMap.shape[1])
        tableCounter = 0
        for i in range(self.seatingMap.shape[0]):
            for j in range(self.seatingMap.shape[1]):
                if(self.seatingMap[i][j]!=0):
                    tablesArr[i][j] = table(12, list, 12, tableCounter)
                    tableCounter+=1
                
        return tablesArr

    def createKnownPositions(self, arrangement):
        knownPositions = {}

        for i in range(arrangement.shape[0]):
            for j in range(arrangement.shape[1]):
                table = arrangement[i][j]

                for k in range(len(table)):
                    knownPositions[table[k]] = ((i, j))

        return knownPositions

    def randomizeTables(self):
        sortedSizeDict = dict(sorted(self.sizeDict.items(), key=lambda item: item[1]))
        sizes = np.array(list(sortedSizeDict.values()))
        boundaryIdx, uniqueSizes = np.unique(sizes, return_index=True)

        splitSizeDict = {}
        for i in range(len(uniqueSizes)):
            splitSizeDict[uniqueSizes[i]] = np.split([sizes, boundaryIdx[1:]])

        uniqueSizesDesc = uniqueSizes[::-1]
        arrangement = self.createTables()

        for i in range(arrangement.shape[0]):
            for j in range(arrangement.shape[1]):
                canFitMore = True
                while(canFitMore==True):
                    for k in range(len(uniqueSizes)):
                        size = arrangement[i][j].sizeCur
                        adjUniqueSizes = size - uniqueSizesDesc
                        if(adjUniqueSizes[k]>=0 and splitSizeDict[k].shape[0]>0):
                            validMembers = splitSizeDict[k]
                            member = np.random.choice(validMembers, size=1, replace=True)
                            arrangement[i][j].members.append(member)
                            arrangement[i][j].sizeCur -= uniqueSizes[k]
                            break
                        canFitMore = False






        


