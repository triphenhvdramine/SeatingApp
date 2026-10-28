import numpy as np
import random
import math
import copy
from numba import njit, prange, types
from numba.typed import Dict, List

@njit
def randomSelect(idxDict):
    keysArr = np.asarray(List(idxDict.keys()))
    swaps = np.random.choice(keysArr, size=2, replace=False)
    p1R,p1C = idxDict[swaps[0]]
    p2R,p2C = idxDict[swaps[1]]
    return p1R,p1C,p2R,p2C

@njit
def guidedSelect(curArrangement, neighbourDict, idxDict, studentAffinity, friendsNum):
    keysArr = np.asarray(List(idxDict.keys()))
    targetGuest = np.random.choice(keysArr, size=1, replace=False)[0]
    targetGuestIdx = idxDict[targetGuest]

    validSwaps = List()
    for i in range(len(neighbourDict[(targetGuestIdx[0], targetGuestIdx[1])])):
        arr = neighbourDict[(targetGuestIdx[0], targetGuestIdx[1])][i]
        r,c= arr[0], arr[1]
        if(max(studentAffinity[targetGuest][curArrangement[r][c]-1], studentAffinity[curArrangement[r][c]-1][targetGuest])!=1):
            validSwaps.append(arr)

    if(len(validSwaps)>0):
        randIdx = np.random.choice(len(validSwaps), size=1, replace=False)[0]
        p1R = validSwaps[randIdx][0]
        p1C = validSwaps[randIdx][1]

        friendsTuple = friendsNum[targetGuest]
        targetFriend = np.random.choice(friendsTuple, size=1, replace=False)[0]

        p2R,p2C = idxDict[targetFriend-1]
    else:
        p1R,p1C,p2R,p2C = randomSelect(idxDict)

    return p1R,p1C,p2R,p2C
    
@njit
def fitnessScore(arrangement, studentAffinity):
    score = 0

    for i in range(arrangement.shape[0]):
        for j in range(arrangement.shape[1]):
            if(arrangement[i][j] != 0):
                if(j+1 < arrangement.shape[1]):
                    newRow = i
                    newCol = j+1
                elif(i+1 < arrangement.shape[0]):
                    newRow = i+1
                    newCol = 0
                else:
                    return score

                for k in range(newRow, arrangement.shape[0]):
                    for l in range(newCol, arrangement.shape[1]):
                        if(arrangement[k][l] != 0):
                            scoreFwd = studentAffinity[arrangement[i][j]-1,arrangement[k][l]-1]
                            scoreRev = studentAffinity[arrangement[k][l]-1,arrangement[i][j]-1]
                            scoreRaw = max(scoreFwd, scoreRev)

                            distanceRaw = math.sqrt((k-i)**2 + (l-j)**2)
                            distanceFactor = np.exp(-distanceRaw)
                            score += scoreRaw * distanceFactor  

                    newCol = 0
    return score

@njit
def localSearch(arrangement, score, studentAffinity):
    bestArrangement = arrangement
    neighbours: list[tuple] = []
    bestScore = score

    for i in range(arrangement.shape[0]):
        for j in range(arrangement.shape[1]):
            val1 = arrangement[i][j]

            if(j+1 < arrangement.shape[1]):
                newRow = i
                newCol = j+1
            elif(i+1 < arrangement.shape[0]):
                newRow = i+1
                newCol = 0
            else:
                return bestArrangement,bestScore,False

            for k in range(newRow, bestArrangement.shape[0]):
                for l in range(newCol, bestArrangement.shape[1]):
                    val2 = bestArrangement[k][l]

                    bestArrangement[i][j] = val2
                    bestArrangement[k][l] = val1

                    newScore = fitnessScore(bestArrangement, studentAffinity)
                    if(newScore > bestScore):
                        delta = newScore - bestScore
                        bestScore = newScore
                        neighbours.insert(0, (bestArrangement,delta,bestScore))

                        bestArrangement[i][j] = val1
                        bestArrangement[k][l] = val2
                    else:
                        bestArrangement[i][j] = val1
                        bestArrangement[k][l] = val2

    bestLocalArrangement = neighbours[0][0]
    bestLocalScore = neighbours[0][2]
    bestDelta = neighbours[0][1]

    if(bestDelta > 0):
        return bestLocalArrangement,bestLocalScore,True
    else:
        return bestArrangement,bestScore,False

def minEx(exValue, value):
    if(value<exValue):
        return value+1
    else:
        return exValue
        
class SeatingPlan:
    def __init__(self, numStudents, rows, cols, affinityMatrix, friendsNum, numAnneals):
        self.numAnneals = numAnneals
        self.rows = rows
        self.cols = cols
        self.studentAffinity = affinityMatrix
        self.numStudents = numStudents
        self.friendsNum = friendsNum
        self.population = []

    def randomizeBoard(self):
        arrangement = np.zeros((self.rows, self.cols), dtype=int)

        students = []
        for i in range(1, self.numStudents+1):
            students.append(i)

        for _ in range(len(students)):
            chosenPerson = random.choice(students)

            chosenRow = random.randrange(0,arrangement.shape[0])
            chosenCol = random.randrange(0,arrangement.shape[1])

            while(arrangement[chosenRow][chosenCol] != 0):
                chosenRow = random.randrange(0,arrangement.shape[0])
                chosenCol = random.randrange(0,arrangement.shape[1])

            arrangement[chosenRow][chosenCol] = chosenPerson
            students.remove(chosenPerson)

        return arrangement

    def anneal(self):
        tempDecay = 0.99999
        currentTemp = 1.0        
        curArrangement = self.randomizeBoard()
        bestArrangement = copy.deepcopy(curArrangement)
        bestScore = fitnessScore(bestArrangement, self.studentAffinity)
        neighbourDict = Dict()

        #Precompute the neighbours of every cell
        for r in range(curArrangement.shape[0]):
            for c in range(curArrangement.shape[1]):
                neighbourList = List()
                for rn in range(max(0, r-1), minEx(curArrangement.shape[0],r+1)):
                    for cn in range(max(0, c-1), minEx(curArrangement.shape[1],c+1)):
                        if((r,c) != (rn, cn)):
                            idxArr = np.asarray((rn,cn))
                            neighbourList.append(idxArr)
                neighbourDict[(r,c)] = neighbourList

        #Generate a dictionary with the location of every guest
        idxDict = Dict()

        for r in range(curArrangement.shape[0]):
            for c in range(curArrangement.shape[1]):
                guestKey = curArrangement[r][c]-1
                if(guestKey != -1):
                    idxArr = np.asarray((r,c))
                    idxDict[guestKey] = idxArr
            
        while currentTemp > 0.0001:
            if(np.random.rand() >= 0.0):
                p1R,p1C,p2R,p2C = guidedSelect(curArrangement, neighbourDict, idxDict, self.studentAffinity, self.friendsNum)

            else:    
                p1R,p1C,p2R,p2C = randomSelect(idxDict)

            val1 = curArrangement[p1R][p1C]
            val2 = curArrangement[p2R][p2C]

            curArrangement[p1R][p1C] = val2
            curArrangement[p2R][p2C] = val1

            newScore = fitnessScore(curArrangement, self.studentAffinity)
            if(newScore >= bestScore or np.random.rand() < np.exp((newScore - bestScore) / currentTemp)):
                bestArrangement = copy.deepcopy(curArrangement)
                bestScore = newScore

                idxDict[val2-1] = np.asarray((p1R,p1C))
                idxDict[val1-1] = np.asarray((p2R,p2C))
            else:
                curArrangement[p1R][p1C] = val1
                curArrangement[p2R][p2C] = val2

            currentTemp *= tempDecay

        #return bestArrangement, bestScore
        bestAnnealArrangement = bestArrangement
        bestAnnealScore = bestScore
        improvement = True

        
        while(improvement == True):
            bestLSArrangement, bestLSScore, improvement = localSearch(bestAnnealArrangement, bestAnnealScore, self.studentAffinity)
        return bestLSArrangement, bestLSScore
        
    def annealRep(self):
        bestScore = -99999999
        totalScore = 0
        bestBoard = np.empty((self.rows,self.cols), dtype=int)

        for _ in range(self.numAnneals):
            currentBoard, currentScore = self.anneal()

            if(currentScore > bestScore):
                bestScore = currentScore
                bestBoard = currentBoard

            totalScore += currentScore

            print("After " + str(_+1) + " anneals the best found board was:")
            print(bestBoard)
            print("With a score of " + str(bestScore))

        mean = totalScore / self.numAnneals

        print("After " + str(self.numAnneals) + " anneals the best found board was:")
        print(bestBoard)
        print("With a score of " + str(bestScore))
        print("The mean score was " + str(mean))
        return bestBoard