import numpy as np
from operator import itemgetter
import random
import math
import copy
from numba import njit, prange

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
                    return score;

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

class SeatingPlan:
    def __init__(self, numStudents, rows, cols, affinityMatrix, numAnneals):
        self.numAnneals = numAnneals
        self.rows = rows
        self.cols = cols
        self.studentAffinity = affinityMatrix
        self.numStudents = numStudents
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
        curArrangement = self.randomizeBoard()
        bestArrangement = copy.deepcopy(curArrangement)
        bestScore = fitnessScore(bestArrangement, self.studentAffinity)

        currentTemp = 1.0
        while currentTemp > 0.00001:
            p1C = random.randrange(0, curArrangement.shape[1])
            p2C = random.randrange(0, curArrangement.shape[1])
            p1R = random.randrange(0, curArrangement.shape[0])
            p2R = random.randrange(0, curArrangement.shape[0])

            while((curArrangement[p1R][p1C] == 0) and (curArrangement[p2R][p2C] == 0)):
                p2C = random.randrange(0, curArrangement.shape[1])
                p2R = random.randrange(0, curArrangement.shape[0])

            while((p1R==p2R) and (p1C==p2C)):
                 p2C = random.randrange(0, curArrangement.shape[1])

            val1 = curArrangement[p1R][p1C]
            val2 = curArrangement[p2R][p2C]

            curArrangement[p1R][p1C] = val2
            curArrangement[p2R][p2C] = val1

            newScore = fitnessScore(curArrangement, self.studentAffinity)
            if(newScore >= bestScore or np.random.rand() < np.exp((newScore - bestScore) / currentTemp)):
                bestArrangement = copy.deepcopy(curArrangement)
                bestScore = newScore
            else:
                curArrangement[p1R][p1C] = val1
                curArrangement[p2R][p2C] = val2

            currentTemp *= tempDecay

        bestAnnealArrangement = bestArrangement
        bestAnnealScore = bestScore
        improvement = True

        
        while(improvement == True):
            bestLSArrangement, bestLSScore, improvement = localSearch(bestAnnealArrangement, bestAnnealScore, self.studentAffinity)

        return bestLSArrangement, bestLSScore
        
        #return bestArrangement,bestScore

    def annealRep(self):
        bestScore = -99999999
        bestBoard = np.empty((self.rows,self.cols), dtype=int)

        for _ in range(self.numAnneals):
            currentBoard, currentScore = self.anneal()

            if(currentScore > bestScore):
                bestScore = currentScore
                bestBoard = currentBoard

            print("After " + str(_+1) + " anneals the best found board was:")
            print(bestBoard)
            print("With a score of " + str(bestScore))

        print("After " + str(self.numAnneals) + " anneals the best found board was:")
        print(bestBoard)
        print("With a score of " + str(bestScore))

        return bestBoard