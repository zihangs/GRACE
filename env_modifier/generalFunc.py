import os
import shutil
from tarski.io import PDDLReader

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


def setGoal(problemFile, hypsFile, index=0):
    f = open(hypsFile, "r")
    goals = f.read().split("\n")
    # selectedGoal = goals[index]
    selectedGoal = "(and )"
    f.close()
    f = open(problemFile, "r")
    template = f.read()
    templateWithGoal = template.replace("<HYPOTHESIS>", selectedGoal)
    f.close()
    f = open("tmp_template.pddl", "w")
    f.write(templateWithGoal)
    f.close()
    return selectedGoal, "tmp_template.pddl"  # return the tmp file name

def restoreTemplate(tmpFile, newTemplateFile, selectedGoal):
    f = open(tmpFile, "r")
    tmpTemplate = f.read()
    newTemplate = tmpTemplate.replace(selectedGoal, "<HYPOTHESIS>")
    f.close()
    print()
    f = open(tmpFile, "w")
    f.write(newTemplate)
    f.close()
    os.rename(tmpFile, newTemplateFile)