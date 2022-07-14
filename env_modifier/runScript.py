## this script will try to generate valid environments for all domains and problems
import os
import re
import random
import sys
import shutil
from math import ceil
from env_modifier import iterativeModify
from generalFunc import templateFillGoals
from lapkt_check import validate_steps_goals

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
# args_script = ["runScript.py", "source_data", "-InitRW", "10", lapktTimeout, lapktAttempts]
args_script = sys.argv
lapktTimeout = int(sys.argv[-2])
lapktAttempts = int(sys.argv[-1])

src_data = args_script[1]
output_templates = src_data + "_output_templates"
output_plan_problems = src_data + "_output_problems"


# args[1] will be replaced
# args_env_modifier = ["env_modifier.py", "dirOfDomainTemplateHyps", "-InitRW", "10"]

safeCreateDir(output_templates)
safeCreateDir(output_plan_problems)

# record the number of goals:
f_goal_count = open("goal_count.csv", "w")

# create dir for each domain in src_data (store problem/template format)
domains = listAllSubDir(src_data)
for domain in domains:
    problems = listAllSubDir(domain)
    a_domain_template = domain.replace(src_data, output_templates)
    a_domain_problem = domain.replace(src_data, output_plan_problems)
    safeCreateDir(a_domain_template)
    safeCreateDir(a_domain_problem)

    # modifier env for each problem in the domain (a problem: domain, template, hyps)
    for problem_dir in problems:
        args_env_modifier = args_script
        args_env_modifier[0] = "env_modifier.py"
        args_env_modifier[1] = problem_dir





        # check steps: (check the original problem only once):   for random walk:
        valid_flag, steps, _ = validate_steps_goals(lapktTimeout, problem_dir+"/domain.pddl", problem_dir+"/template.pddl", problem_dir+"/hyps.dat")
        if valid_flag:     # then modify environment next
            # replace args[3] with real step number
            stepsNum = ceil( float(args_env_modifier[3]) * steps ) 
            args_env_modifier[3] = str( stepsNum )

            print( "steps = " + str(steps) )  # this is average of steps
        else:
            continue   # the original problem is invalid, go to next problem






        # exec
        status, goals = iterativeModify(args_env_modifier, timeout=lapktTimeout, attempts=lapktAttempts)

        if status:
            f_goal_count.write(problem_dir + "," + str(goals) + "\n")

            problem_dir_output = problem_dir.replace(src_data, output_plan_problems)

            # env0: copy and fill original template, generate env0
            templateFillGoals(problem_dir, problem_dir_output + "/env0")
            # env1: copy and fill modified template, generate env1
            templateFillGoals("modified", problem_dir_output + "/env1")

            # move modified/ to output_templates/ (this is in template format)
            template_dir_output = problem_dir.replace(src_data, output_templates)
            # move and rename
            shutil.move("modified/", template_dir_output)


f_goal_count.close()