import numpy as np
from operator import itemgetter
import random
import math
import copy

class SeatingPlan:
    def __init__(self, numStudents, rows, cols, affinityMatrix, popSize, numGen):
        self.popSize = popSize
        self.numGen = numGen
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
    
    def initializePopulation(self):
        for _ in range(self.popSize):
            self.population.append(self.randomizeBoard())

    def fitnessScore(self, arrangement):
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
                                scoreFwd = self.studentAffinity[arrangement[i][j]-1,arrangement[k][l]-1]
                                scoreRev = self.studentAffinity[arrangement[k][l]-1,arrangement[i][j]-1]
                                scoreRaw = max(scoreFwd, scoreRev)

                                distanceRaw = math.sqrt((k-i)**2 + (l-j)**2)
                                distanceFactor = np.exp(-distanceRaw)
                                score += scoreRaw * distanceFactor  

                        newCol = 0
        return score

    def selection(self, sortedPop):
        population = copy.deepcopy(sortedPop)
        popPoolFitnessAdj = []
        selectedParents = []

        for i in range(len(population)):
            repeats = np.clip(population[i][0], 0, 99)

            for j in range(math.ceil(repeats)):
                popPoolFitnessAdj.append(population[j][1])

        parent1 = popPoolFitnessAdj[random.randint(0,len(popPoolFitnessAdj)-1)]
        parent2 = popPoolFitnessAdj[random.randint(0,len(popPoolFitnessAdj)-1)]

        selectedParents.append(parent1)
        selectedParents.append(parent2)

        return parent1, parent2

    def crossover(self, parent1, parent2):
        crParent1 = copy.deepcopy(parent1)
        crParent2 = copy.deepcopy(parent2)

        crParent1 = np.ravel(parent1)
        crParent2 = np.ravel(parent2)

        crSplit1 = random.randint(0, len(crParent1)-1)
        crSplit2 = random.randint(0, len(crParent1))

        while(crSplit1 >= crSplit2):
            crSplit2 = random.randint(0, len(crParent1))

        crParent2[crSplit1:crSplit2] = crParent1[crSplit1:crSplit2]
        crParent1[crSplit1:crSplit2] = crParent2[crSplit1:crSplit2]

        child1 = crParent1.reshape(self.rows,self.cols)
        child2 = crParent2.reshape(self.rows,self.cols)

        return child1, child2 


    def mutate(self, arrangement):
        arr = copy.deepcopy(arrangement)

        mutRow1 = random.randint(0, arr.shape[0]-1)
        mutCol1 = random.randint(0, arr.shape[1]-1)
        mutRow2 = random.randint(0, arr.shape[0]-1)
        mutCol2 = random.randint(0, arr.shape[1]-1)

        while(mutRow1 == mutRow2):
            mutRow2 = random.randint(0, arr.shape[0]-1)

        while(mutCol1 == mutCol2):
            mutCol2 = random.randint(0, arr.shape[1]-1)

        val1 = arr[mutRow1][mutCol1]
        val2 = arr[mutRow2][mutCol2]

        arr[mutRow1][mutCol1] = val2
        arr[mutRow2][mutCol2] = val1

    def legalArrangement(self, arrangement):
        vals, counts = np.unique(arrangement, return_counts=True)

        for i in range(len(vals)):
            if(vals[i] != 0 and counts[i] > 1):
                return False

        if(len(vals) < (self.numStudents+1)):
            return False
        else:
            return True

    def runGA(self):  
        n=0
        while(n < 100):
            self.initializePopulation()
            print(n)

            best = -5
            bestBoard = np.zeros((self.rows,self.cols))

            for pop in range(len(self.population)):
                if(self.fitnessScore(self.population[pop]) > best):
                    best = self.fitnessScore(self.population[pop])
                    bestBoard = self.population[pop]

            self.population = []
            n += 1

        print(bestBoard)
        print(best)

    def runGA1(self):
            bestFit = -1000
            bestBoard = np.zeros((self.rows,self.cols))
            MUT_RATE = 70
        
            for gen in range(self.numGen):
                self.initializePopulation()
        
                TBSPopulation = []
        
                for pop in self.population:
                    fitness = self.fitnessScore(pop)
                    boardCopy = copy.deepcopy(pop)
                    TBSPopulation.append((fitness, boardCopy))
        
                sortedPopulation = sorted(TBSPopulation, key=itemgetter(0), reverse=True)

                self.population.clear()
        
                for i in range(math.floor(0.1 * self.popSize)):
                    goodBoardCopy = copy.deepcopy(sortedPopulation[i][1])
                    self.population.append(goodBoardCopy)
        
                while(len(self.population) < self.popSize):
                    parent1, parent2 = self.selection(sortedPopulation)
                    child1, child2 = self.crossover(parent1, parent2)  

                    mutRoll = random.randint(0,100)
                    if(mutRoll <= MUT_RATE):
                         self.mutate(child1)
                         self.mutate(child2)

                    if(self.legalArrangement(child1)):
                        child1Copy = copy.deepcopy(child1)
                        self.population.append(child1Copy)

                    if(self.legalArrangement(child2)):
                        child2Copy = copy.deepcopy(child2)
                        self.population.append(child2Copy)

                bestFitInN = sortedPopulation[0][0]
                bestBoardInN = sortedPopulation[0][1]

                print("In generation " + str(gen) + ":")
                print("Best board: ")
                print(bestBoardInN)
                print("With a score of: " + str(bestFitInN))

                if(bestFitInN>bestFit):
                    bestFit = bestFitInN
                    bestBoard = bestBoardInN

            print("After " + str(self.numGen) + " generations")
            print("The best found solution was: ")
            print(bestBoard)
            print("With a score of " + str(bestFit))

    def anneal(self):
        tempDecay = 0.999
        curArrangement = self.randomizeBoard()
        bestArrangement = copy.deepcopy(curArrangement)
        bestScore = self.fitnessScore(bestArrangement)

        currentTemp = 1.0
        while currentTemp > 0.001:
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

            newScore = self.fitnessScore(curArrangement)
            if(newScore >= bestScore or np.random.rand() < np.exp((newScore - bestScore) / currentTemp)):
                bestArrangement = copy.deepcopy(curArrangement)
                bestScore = newScore
            else:
                curArrangement[p1R][p1C] = val1
                curArrangement[p2R][p2C] = val2

            currentTemp *= tempDecay

        print(bestArrangement)
        print(bestScore)
        return bestArrangement, bestScore

        