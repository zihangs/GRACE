import os
import numpy as np
import shutil
from tarski.io import PDDLReader


def safeRemoveFile(file):
    # Check whether the specified path exists or not
    isExist = os.path.exists(file)
    if isExist:
        # delete
        os.remove(file)

def safeRemoveDir(dirName):
    # Check whether the specified path exists or not
    isExist = os.path.exists(dirName)
    if isExist:
        # delete
        shutil.rmtree(dirName)


def reCreateDir(dirName):
    # Check whether the specified path exists or not
    isExist = os.path.exists(dirName)
    if isExist:
        # delete
        shutil.rmtree(dirName)
    
    os.makedirs(dirName)


def loadPDDLProblem(domainFile, problemFile):
    reader = PDDLReader(raise_on_error=True)
    reader.parse_domain(domainFile)
    problem = reader.parse_instance(problemFile)
    return problem


def setHyps(problemFile, hypsFile, index=0):
    f = open(hypsFile, "r")
    hyps = f.read().replace(",", "").split("\n")
    selectedHyps = hyps[index]
    f.close()
    f = open(problemFile, "r")
    template = f.read()
    templateWithGoal = template.replace("<HYPOTHESIS>", selectedHyps)
    f.close()
    f = open("tmp_template.pddl", "w")
    f.write(templateWithGoal)
    f.close()
    return selectedHyps, "tmp_template.pddl"  # return the tmp file name


def restoreTemplate(tmpFile, newTemplateFile, selectedHyps):
    f = open(tmpFile, "r")
    newTemplate = ""
    inGoal = False
    lines = f.readlines()
    for line in lines:
        if ":goal" in line:
            inGoal = True

        if not inGoal:
            newTemplate += line
        else:
            newTemplate += line.replace(selectedHyps, "<HYPOTHESIS>")
    f.close()
    f = open(tmpFile, "w")
    f.write(newTemplate)
    f.close()
    os.rename(tmpFile, newTemplateFile)


# input: a env with template, output: a env have multiple subdir (template filled with goals in hyps.dat)
def templateFillGoals(inputDir, outputDir):
    reCreateDir(outputDir)

    f_template = open(inputDir + "/template.pddl", "r")
    strTemplate = f_template.read()
    f_template.close()

    f_hyps = open(inputDir + "/hyps.dat", "r")
    hyps = f_hyps.readlines() # get goals
    f_hyps.close()

    goal = 0
    for h in hyps:
        if h:  # if it's not an empty line
            goalDir = outputDir + "/goal_" + str(goal)
            reCreateDir(goalDir)
            shutil.copyfile(inputDir + "/domain.pddl", goalDir + "/domain.pddl")
            
            #remove comma
            h = h.replace(",", " ")
            strWithHyp = strTemplate.replace("<HYPOTHESIS>", h)
            f_write_to = open(goalDir + "/problem.pddl", "w")
            f_write_to.write(strWithHyp)
            f_write_to.close()

            # goal
            goal += 1


def levenshteinDistance(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2+1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]


def editDistanceMatrix(planSet1, planSet2):
    goals = len(planSet1)
    tf_list = []
    dis_matrix = np.zeros((goals, goals))
    for i in range(goals):
        d_i_i = levenshteinDistance(planSet1[i], planSet2[i])
        dis_matrix[i][i] = d_i_i
        j = 0
        is_greater_than_other = "false"
        while j < goals:
            if j != i:
                d_i_j = levenshteinDistance(planSet1[i], planSet2[j])
                dis_matrix[i][j] = d_i_j
                if d_i_i > d_i_j:
                    is_greater_than_other = "true"
                    break
            j += 1

        # tf_list: if there is another non-diagonal value larger than the diagonal?
        tf_list.append(is_greater_than_other)

    return tf_list, dis_matrix


# check if a planning problem in the fold is valid or not
# return: 1. if we can find a plan for each goal candidate?
#         2. the number of steps for each optimal plan or empty set if 1 is false
#         3. the number of goals
def top1Plans(dir, timelimit):  # just input folder name
    dir_probs_name = dir + "_probs"
    templateFillGoals(dir, dir_probs_name)
    safeRemoveDir("../planner/symk/" + dir_probs_name + "/")
    shutil.move("./"+dir_probs_name+"/", "../planner/symk/" + dir_probs_name + "/")
    
    os.chdir("../planner/symk/")

    lstOfGoals = os.listdir(dir_probs_name)
    numOfGoals = len(lstOfGoals)
    number_of_plan = 1   # only need to find 1 optimal plan
    steps_collection = []

    for i in range(numOfGoals):
        domain = "%s/goal_%s/domain.pddl"%(dir_probs_name, str(i))
        problem = "%s/goal_%s/problem.pddl"%(dir_probs_name, str(i))

        os.system('timeout %s ./fast-downward.py %s %s --search "symk-bd(plan_selection=top_k(num_plans=%s))"'%(str(timelimit), domain, problem, str(number_of_plan))  )

        # if empty
        if os.listdir("found_plans/") == []:
            os.chdir("../../env_modifier")
            return False, steps_collection, len(steps_collection)
        f = open("found_plans/sas_plan.1", "r")
        steps = (f.readlines())[0:-1]
        steps_collection.append(steps)

    os.chdir("../../env_modifier")
    
    return True, steps_collection, len(steps_collection)


