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