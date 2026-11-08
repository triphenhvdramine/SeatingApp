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
    def __init__(self, seatingMap, affinityMatrix, friendsList, sizeList, numAnneals):
        self.seatingMap = seatingMap
        self.affinityMatrix = affinityMatrix
        self.friendsList = friendsList
        self.sizeList = sizeList
        self.numAnneals = numAnneals
    
    def createTables(self):
        tablesArr = np.array(self.seatingMap.shape[0],self.seatingMap.shape[1])
        tableCounter = 0
        for i in range(self.seatingMap.shape[0]):
            for j in range(self.seatingMap.shape[1]):
                if(self.seatingMap[i][j]!=0):
                    tablesArr[i][j] = table(12, list, tableCounter)
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
