import os
import shutil
import random
import sys
from tarski.io import PDDLReader, FstripsWriter

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


def loadPDDLProblem(domainFile, problemFile):
    reader = PDDLReader(raise_on_error=True)
    reader.parse_domain(domainFile)
    problem = reader.parse_instance(problemFile)
    return problem

def removeConstantObj(problem, aConstant):
    # remove all predicates related to the constant
    for atom in problem.init.as_atoms():
        p = atom.symbol
        arguments = atom.subterms
        lst = []
        toRemove = False
        for a in arguments:
            lst.append(lang.get(str(a)))
            if str(aConstant) == str(a):
                # print("Remove: ")
                # print(arguments)
                toRemove = True
        if toRemove:
            problem.init.remove(p, *lst)

    return problem


if __name__ == "__main__":
    # sys.argv[domainFile, problemFile, goalNum, numNewEnv, percentage, outputDir]
    # python object.py domain.pddl problem.pddl 0 5 0.1 constant_change
    
    # domainFile = "domain.pddl"
    # problemFile = "problem.pddl"
    # goalNum = "0"
    # numNewEnv = 5
    # # total percent of remove
    # percentage = 0.1
    # outputDir = "constant_change"
    
    domainFile = sys.argv[1]
    problemFile = sys.argv[2]
    goalNum = sys.argv[3]
    # total percent of remove
    numNewEnv = int(sys.argv[4])
    percentage = float(sys.argv[5])
    outputDir = sys.argv[6]
    
    problem = loadPDDLProblem(domainFile, problemFile)
    lang = problem.language

    # all objects
    allConstantObj = lang.constants()
    numRemove = int(len(allConstantObj)*percentage)

    savePoint = []
    for i in range(numNewEnv):
        savePoint.append( int( numRemove/5*(i+1) ) )

    random.shuffle(allConstantObj)
    addDirIfNotExist(outputDir)

    envCount = 0


    # write original as env 0
    envPath = outputDir + "/" + "env%s" % str(envCount)
    addDirIfNotExist(envPath)
    goalPath = envPath + "/" + "goal%s" % goalNum
    addDirIfNotExist(goalPath)
    writer = FstripsWriter(problem)
    writer.write(goalPath + "/" + "domain.pddl", goalPath + "/" + "problem.pddl")


    for j in range(numRemove):

        aConstant = allConstantObj[j]
        print(aConstant)
        problem = removeConstantObj(problem, aConstant)
        if j+1 in savePoint:
            print("save it")
            envCount += 1
            envPath = outputDir + "/" + "env%s" % str(envCount)
            addDirIfNotExist(envPath)

            goalPath = envPath + "/" + "goal%s" % goalNum
            addDirIfNotExist(goalPath)

            writer = FstripsWriter(problem)
            writer.write(goalPath + "/" + "domain.pddl", goalPath + "/" + "problem.pddl")



