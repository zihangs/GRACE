import os
import sys
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
        random.shuffle(pathList)
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
        random.shuffle(fileList)
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
    numberOfCaseLeast = float('inf')  # set an infinity number

    envList = listAllSubDir(rootPath, "sorted")
    numberOfEnv = len(envList)
    for env in envList:
        tmpList = []
        goalList = listAllSubDir(env, "sorted")
        numberOfGoal = len(goalList)
        for goal in goalList:
            caseList = listAllSubFile(goal, "shuffled")    ###################
            if len(caseList) < numberOfCaseLeast:
                numberOfCaseLeast = len(caseList)
            tmpList.append(caseList)

        problemStructure.append(tmpList)
        
    return numberOfEnv, numberOfGoal, numberOfCaseLeast, problemStructure



class DriftGenerator:
    def __init__(self, numberOfEnv, numberOfGoal, numberOfCaseLeast, problemStructure):
        self.numberOfEnv = numberOfEnv
        self.numberOfGoal = numberOfGoal
        self.numberOfCaseLeast = numberOfCaseLeast
        self.problemStructure = problemStructure
        self.outputDir = "outputDrift"

        print(numberOfCaseLeast)
        
    # eg: numberPerCase = 200
    # sudden drift: drift happen when each goal have selected "numberPerCase" of cases
    def sudden(self, numberPerCase):
        dstDir = self.outputDir
        safeCreateDir(dstDir)
        
        caseID = []
        env = []
        goal = []
        
        caseCount = 0
        envId = 0
        while envId < self.numberOfEnv:
            currCollected = 0
            while currCollected < numberPerCase:
                goalId = random.randint(0, self.numberOfGoal-1)
                case = problemStructure[envId][goalId][currCollected]
                # print(case)

                caseCount += 1
                caseID.append(caseCount)
                env.append(envId)
                goal.append(goalId+1)

                copyName = "sas_plan.%s" % str(caseCount)
                shutil.copyfile(case, dstDir + "/" + copyName)        
                currCollected += 1
            envId += 1
            
        d = {"caseID": caseID, "env": env, "goal": goal}
        df = pd.DataFrame(data=d)
        return df
        
        
            
    # numberPerCase = 200, reoccurTimes = 3, 
    def reoccuring(self, numberPerCase, reoccurTimes):
        dstDir = self.outputDir
        safeCreateDir(dstDir)
        
        caseID = []
        env = []
        goal = []
               
        caseCount = 0
        copyStructure = copy.deepcopy(self.problemStructure)
        reoccurCount = 0
        while reoccurCount < reoccurTimes:
            envId = 0
            while envId < self.numberOfEnv:
                currCollected = 0
                while currCollected < numberPerCase:
                    goalId = random.randint(0, self.numberOfGoal-1)
                    # need pop out the first item
                    case = copyStructure[envId][goalId].pop(0)

                    caseCount += 1
                    caseID.append(caseCount)
                    env.append(envId)
                    goal.append(goalId+1)

                    copyName = "sas_plan.%s" % str(caseCount)
                    shutil.copyfile(case, dstDir + "/" + copyName) 
                    currCollected += 1
                envId += 1
            reoccurCount += 1
            
        d = {"caseID": caseID, "env": env, "goal": goal}
        df = pd.DataFrame(data=d)
        return df
            
        
     
    # numberPerCase = 200, graduateChangeCases = 100
    def gradual(self, numberPerCase, graduateChangeCases, periodList = ["normal", "gradual", "normal"]):
        dstDir = self.outputDir
        safeCreateDir(dstDir)
        
        caseCount = 0
        copyStructure = copy.deepcopy(self.problemStructure)
        envIdList = [0, 1]
        increasingProbStep = 100/graduateChangeCases
        probEnv0 = 100
        probEnv1 = 0
        
        caseID = []
        env = []
        goal = []

        for period in periodList:

            # normal period:
            if period == "normal":
                currCollected = 0
                while currCollected < numberPerCase:
                    envId = random.choices(envIdList, weights=(probEnv0, probEnv1), k=1)[0] # only one item in the list
                    goalId = random.randint(0, self.numberOfGoal-1)
                    case = copyStructure[envId][goalId].pop(0)

                    caseCount += 1
                    caseID.append(caseCount)
                    env.append(envId)
                    goal.append(goalId+1)

                    copyName = "sas_plan.%s" % str(caseCount)
                    shutil.copyfile(case, dstDir + "/" + copyName) 
                    currCollected += 1

            # gradual period
            if period == "gradual":
                currCollected = 0
                while currCollected < graduateChangeCases:

                    
                    envId = random.choices(envIdList, weights=(probEnv0, probEnv1), k=1)[0]
                    probEnv0 -= increasingProbStep
                    probEnv1 += increasingProbStep
                    
                    goalId = random.randint(0, self.numberOfGoal-1)

                    case = copyStructure[envId][goalId].pop(0)

                    caseCount += 1
                    caseID.append(caseCount)
                    env.append(envId)
                    goal.append(goalId+1)

                    copyName = "sas_plan.%s" % str(caseCount)
                    shutil.copyfile(case, dstDir + "/" + copyName)
                        
                    currCollected += 1
                    
        d = {"caseID": caseID, "env": env, "goal": goal}
        df = pd.DataFrame(data=d)
        return df
    
    # probOutlier = 0.05, numberPerCase = 300
    def outlier(self, numberPerCase, probOutlier):
        dstDir = self.outputDir
        safeCreateDir(dstDir)
        
        caseCount = 0
        copyStructure = copy.deepcopy(self.problemStructure)
        probNormal = 1 - probOutlier
        envIdList = [0, 1]
        currCollected = 0
        
        caseID = []
        env = []
        goal = []
        
        while currCollected < numberPerCase:
            envId = random.choices(envIdList, weights=(probNormal, probOutlier), k=1)[0] # only one item in the list
            goalId = random.randint(0, self.numberOfGoal-1)
            case = copyStructure[envId][goalId].pop(0)

            caseCount += 1
            caseID.append(caseCount)
            env.append(envId)
            goal.append(goalId+1)

            copyName = "sas_plan.%s" % str(caseCount)
            shutil.copyfile(case, dstDir + "/" + copyName)
            currCollected += 1
            
        d = {"caseID": caseID, "env": env, "goal": goal}
        df = pd.DataFrame(data=d)
        return df

    def incremental(self, numberPerCase, numEnv):
        dstDir = self.outputDir
        safeCreateDir(dstDir)
        
        caseID = []
        env = []
        goal = []
        
        caseCount = 0
        envId = 0
        
        not_intermediate = True
        
        while envId < self.numberOfEnv:
            if not_intermediate:
                currCollected = 0
                while currCollected < numberPerCase:
                    goalId = random.randint(0, self.numberOfGoal-1)
                    case = problemStructure[envId][goalId][currCollected]
                    # print(case)

                    caseCount += 1
                    caseID.append(caseCount)
                    env.append(envId/numEnv)
                    goal.append(goalId+1)

                    copyName = "sas_plan.%s" % str(caseCount)
                    shutil.copyfile(case, dstDir + "/" + copyName)        
                    currCollected += 1
                envId += 1
                not_intermediate = False
            else:
                currCollected = 0
                goalId = random.randint(0, self.numberOfGoal-1)
                case = problemStructure[envId][goalId][currCollected]
                # print(case)

                caseCount += 1
                caseID.append(caseCount)
                env.append(envId/numEnv)
                goal.append(goalId+1)

                copyName = "sas_plan.%s" % str(caseCount)
                shutil.copyfile(case, dstDir + "/" + copyName)        
                currCollected += 1
                
                envId += 1
                if envId == numEnv:
                    not_intermediate = True
                    

        d = {"caseID": caseID, "env": env, "goal": goal}
        df = pd.DataFrame(data=d)
        return df
        


if __name__ == "__main__":
    # python3 driftGenerator.py block-words_p01 -Gradual 50 50
    # plan_pool = "block-words_p01"
    # option = "-Gradual"

    plan_pool = sys.argv[1]
    option = sys.argv[2]
    
    # create the structure of cases and a generator instance
    numberOfEnv, numberOfGoal, numberOfCase, problemStructure = createProblemStructure(plan_pool)
    dg = DriftGenerator(numberOfEnv, numberOfGoal, numberOfCase, problemStructure)
    if option == "-Sudden":
        cases_per_env = int(sys.argv[3])
        dg.sudden(cases_per_env)

    if option == "-Gradual":
        stable_period = int(sys.argv[3])
        changing_period = int(sys.argv[4])
        dg.gradual(stable_period, changing_period)

