## this script will try to generate valid environments for all domains and problems
import os
import re
import random
import shutil
from env_modifier import iterativeModify
from generalFunc import templateFillGoals

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
output_templates = "miniout_templates"
output_plan_problems = "miniout_problems"

# args[1] will be replaced
args = ["env_modifier.py", "original", "-InitRW", "5"]

safeCreateDir(output_templates)
safeCreateDir(output_plan_problems)

domains = listAllSubDir(data)
for domain in domains:
    problems = listAllSubDir(domain)
    outputDomain_templates = domain.replace(data, output_templates)
    outputDomain_problems = domain.replace(data, output_plan_problems)
    safeCreateDir(outputDomain_templates)
    safeCreateDir(outputDomain_problems)

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
            
            outputProblems = problem.replace(data, output_plan_problems)
            # env0
            templateFillGoals(args[1], outputProblems + "/env0")
            # env1
            templateFillGoals("modified", outputProblems + "/env1")



            outputTemplates = problem.replace(data, output_templates)
            shutil.move("modified/", outputTemplates)








