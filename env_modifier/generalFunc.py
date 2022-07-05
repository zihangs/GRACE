import os
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

