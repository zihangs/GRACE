import os
import sys
import shutil
import random

from tarski.io import PDDLReader, FstripsWriter
from tarski.search.model import GroundForwardSearchModel
from tarski.grounding.lp_grounding import ground_problem_schemas_into_plain_operators

def reCreateDir(dirName):
    # Check whether the specified path exists or not
    isExist = os.path.exists(dirName)
    if isExist:
        # delete
        shutil.rmtree(dirName)
    
    os.makedirs(dirName)

def addDirIfNotExist(dirName):
    # Check whether the specified path exists or not
    isExist = os.path.exists(dirName)
    if isExist:
        pass
    else:
        os.makedirs(dirName)

# load the domain and problem from PDDL files
def loadPDDLProblem(domainFile, problemFile):
    reader = PDDLReader(raise_on_error=True)
    reader.parse_domain(domainFile)
    problem = reader.parse_instance(problemFile)
    return problem
    # lang = problem.language


# def a random walk: find a state after 30 steps
def pickStates(problem, totalStep, stoppingPoints, stepList = [3,4,5]):
    # create a gfs_model
    gfs_model = GroundForwardSearchModel(problem, ground_problem_schemas_into_plain_operators(problem))
    prevState = ""
    currState = problem.init
    states = []

    if totalStep != 0 and stoppingPoints != 0:
        iterSteps = totalStep/stoppingPoints
        for i in range(stoppingPoints):
            prevState, currState = randomWalk(gfs_model, prevState, currState, iterSteps)
            states.append(currState)
    
    # another way to identify iterSteps
    else: 
        for iterSteps in stepList:
            prevState, currState = randomWalk(gfs_model, prevState, currState, iterSteps)
            states.append(currState)

    return states

def randomWalk(gfs_model, prevState, currState, iterSteps):
    step = 0
    while step < iterSteps:
        nonBackSuccList = []
        succ = gfs_model.successors(currState)
        for s in succ:
            # usually not allow to prevState
            if s[1] != prevState:
                nonBackSuccList.append(s[1])

        # when reach to a dead end, allow back to prevState
        if len(nonBackSuccList) == 0:
            nonBackSuccList.append(prevState)
        prevState = currState
        currState = random.choice(nonBackSuccList)
        step += 1

    return prevState, currState


if __name__ == "__main__":

    # sys.argv[domainFile, problemFile, goalNum, stoppingPoints, totalStep, outputDir]
    domainFile = sys.argv[1]
    problemFile = sys.argv[2]
    goal = sys.argv[3]
    stoppingPoints = int(sys.argv[4])
    totalStep = int(sys.argv[5])
    outputDir = sys.argv[6]

    """
    domainFile = "domain.pddl"
    problemFile = "template.pddl"
    goal = "0"
    stoppingPoints = 5
    totalStep = 50
    outputDir = "changed"
    """

    problem = loadPDDLProblem(domainFile, problemFile)
    states = pickStates(problem, totalStep, stoppingPoints)

    # change init state
    addDirIfNotExist(outputDir)

    envCount = 0

    # origin to env 0
    writer = FstripsWriter(problem)
    envPath = outputDir + "/" + "env%s" % str(envCount)
    addDirIfNotExist(envPath)
    goalPath = envPath + "/" + "goal%s" % goal
    addDirIfNotExist(goalPath)
    writer.write(goalPath + "/" + "domain.pddl", goalPath + "/" + "problem.pddl")

    for s in states:
        envCount += 1
        problem.init = s
        writer = FstripsWriter(problem)
        
        # this is diff env, same goal
        envPath = outputDir + "/" + "env%s" % str(envCount)
        addDirIfNotExist(envPath)

        goalPath = envPath + "/" + "goal%s" % goal
        addDirIfNotExist(goalPath)
        writer.write(goalPath + "/" + "domain.pddl", goalPath + "/" + "problem.pddl")







