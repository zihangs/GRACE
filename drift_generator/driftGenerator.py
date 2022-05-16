import os
import random
import re
import shutil
import copy
import pandas as pd

'''
flag: 1. default: list all dir (dir doesn't need end with number)
      2. sorted: the dir must have common prefix and end with number
      3. shuffled: dir doesn't need end with number
'''

def listAllSubDir(path, flag="default"):
    pathList = []
    for item in os.listdir(path):
        if os.path.isdir(path + "/" + item) and item[0] != ".":
            pathList.append(path + "/" + item)
            
    if flag == "default":
        pass
    if flag == "sorted":
        pathList = sortByLastNumber(pathList)
    if flag == "shuffled":
        pathList = random.shuffle(pathList)
    return pathList


def listAllSubFile(path, flag="default"):
    fileList = []
    for item in os.listdir(path):
        if os.path.isfile(path + "/" + item) and item[0] != ".":
            fileList.append(path + "/" + item)
            
    if flag == "default":
        pass
    if flag == "sorted":
        fileList = sortByLastNumber(fileList)
    if flag == "shuffled":
        fileList = random.shuffle(fileList)
    return fileList


def sortByLastNumber(lst):
    tupleList = []
    for item in lst:
        numbers = re.findall(r'[\d]+', item)
        tupleList.append((int(numbers[-1]), item))  # sort by the last number
    tupleList.sort()
    
    stringList = []
    for item in tupleList:
        stringList.append(item[1])
    return stringList

def safeCreateDir(dirName):
    # Check whether the specified path exists or not
    isExist = os.path.exists(dirName)
    if isExist:
        # delete
        shutil.rmtree(dirName)
    
    os.makedirs(dirName)


# create problem structure
# problemStructure[envId][goalId][caseId]

def createProblemStructure(rootPath):
    problemStructure = []
    numberOfEnv = 0
    numberOfGoal = 0
    numberOfCase = 0

    envList = listAllSubDir(rootPath, "sorted")
    numberOfEnv = len(envList)
    for env in envList:
        tmpList = []
        goalList = listAllSubDir(env, "sorted")
        numberOfGoal = len(goalList)
        for goal in goalList:
            caseList = listAllSubFile(goal, "sorted")
            numberOfCase = len(caseList)
            tmpList.append(caseList)

        problemStructure.append(tmpList)
        
    return numberOfEnv, numberOfGoal, numberOfCase, problemStructure



class DriftGenerator:
    def __init__(self, numberOfEnv, numberOfGoal, numberOfCase, problemStructure):
        self.numberOfEnv = numberOfEnv
        self.numberOfGoal = numberOfGoal
        self.numberOfCase = numberOfCase
        self.problemStructure = problemStructure
        
    # eg: numberPerCase = 200
    # sudden drift: drift happen when each goal have selected "numberPerCase" of cases
    def sudden(self, numberPerCase):
        dstDir = "sudden"
        safeCreateDir(dstDir)
        
        caseID = []
        env = []
        
        caseCount = 0
        envId = 0
        while envId < self.numberOfEnv:
            currCollected = 0
            while currCollected < numberPerCase:
                for goalId in range(self.numberOfGoal):
                    case = problemStructure[envId][goalId][currCollected]
                    # print(case)
                    
                    caseCount += 1
                    caseID.append(caseCount)
                    env.append(envId)
                    
                    copyName = "sas_plan.%s" % str(caseCount)
                    shutil.copyfile(case, dstDir + "/" + copyName)        
                currCollected += 1
            envId += 1
            
        d = {"caseID": caseID, "env": env}
        df = pd.DataFrame(data=d)
        # print(df)
        return df
        
        
            
    # numberPerCase = 200, reoccurTimes = 3, 
    def reoccuring(self, numberPerCase, reoccurTimes):
        dstDir = "reoccuring"
        safeCreateDir(dstDir)
               
        caseCount = 0
        copyStructure = copy.deepcopy(self.problemStructure)
        reoccurCount = 0
        while reoccurCount < reoccurTimes:
            envId = 0
            while envId < self.numberOfEnv:
                currCollected = 0
                while currCollected < numberPerCase:
                    for goalId in range(numberOfGoal):
                        # need pop out the first item
                        case = copyStructure[envId][goalId].pop(0)
                        print(case)
                        caseCount += 1
                        copyName = "sas_plan.%s" % str(caseCount)
                        shutil.copyfile(case, dstDir + "/" + copyName) 
                    currCollected += 1
                envId += 1
            reoccurCount += 1
            
        
     
    # numberPerCase = 200, graduateChangeCases = 100
    def gradual(self, numberPerCase, graduateChangeCases, periodList = ["normal", "gradual", "normal"]):
        dstDir = "gradual"
        safeCreateDir(dstDir)
        
        caseCount = 0
        copyStructure = copy.deepcopy(self.problemStructure)
        envIdList = [0, 1]
        increasingProbStep = 100/graduateChangeCases
        probEnv0 = 100
        probEnv1 = 0

        for period in periodList:

            # normal period:
            if period == "normal":
                currCollected = 0
                while currCollected < numberPerCase:
                    envId = random.choices(envIdList, weights=(probEnv0, probEnv1), k=1)[0] # only one item in the list
                    for goalId in range(self.numberOfGoal):
                        case = copyStructure[envId][goalId].pop(0)
                        print(case)
                        caseCount += 1
                        copyName = "sas_plan.%s" % str(caseCount)
                        shutil.copyfile(case, dstDir + "/" + copyName) 
                    currCollected += 1

            # gradual period
            if period == "gradual":
                currCollected = 0
                while currCollected < graduateChangeCases:

                    probEnv0 -= increasingProbStep
                    probEnv1 += increasingProbStep
                    envId = random.choices(envIdList, weights=(probEnv0, probEnv1), k=1)[0]

                    for goalId in range(self.numberOfGoal):
                        case = copyStructure[envId][goalId].pop(0)
                        print(case)
                        caseCount += 1
                        copyName = "sas_plan.%s" % str(caseCount)
                        shutil.copyfile(case, dstDir + "/" + copyName) 
                    currCollected += 1
    
    # probOutlier = 0.05, numberPerCase = 300
    def outlier(self, numberPerCase, probOutlier):
        dstDir = "outlier"
        safeCreateDir(dstDir)
        
        caseCount = 0
        copyStructure = copy.deepcopy(self.problemStructure)
        probNormal = 1 - probOutlier
        envIdList = [0, 1]
        currCollected = 0
        while currCollected < numberPerCase:
            envId = random.choices(envIdList, weights=(probNormal, probOutlier), k=1)[0] # only one item in the list
            for goalId in range(self.numberOfGoal):
                case = copyStructure[envId][goalId].pop(0)
                print(case)
                caseCount += 1
                copyName = "sas_plan.%s" % str(caseCount)
                shutil.copyfile(case, dstDir + "/" + copyName)
            currCollected += 1
        


# main
numberOfEnv, numberOfGoal, numberOfCase, problemStructure = createProblemStructure("a_problem")
        
dg = DriftGenerator(numberOfEnv, numberOfGoal, numberOfCase, problemStructure)