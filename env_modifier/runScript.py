## this script will try to generate valid environments for all domains and problems
import os
import re
import random
import shutil
from env_modifier import iterativeModify

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


##############################################
data = "minidata"
output = "miniout"

args = ["env_modifier.py", "original", "-InitRW", "10"]

safeCreateDir(output)
domains = listAllSubDir(data)
for domain in domains:
    problems = listAllSubDir(domain)
    outputDomain = domain.replace(data, output)
    safeCreateDir(outputDomain)

    count = 0
    for problem in problems:
        print(problem)
        args[1] = problem
        # exec
        status = iterativeModify(args)
        # move modified into
        if status:
            count += 1
            # shutil.move("modified/", outputDomain + "/problem_" + str(count))
            outputProblem = problem.replace(data, output)
            shutil.move("modified/", outputProblem)





