import shutil
import random

from tarski.io import FstripsWriter
from tarski.search.model import GroundForwardSearchModel
from tarski.grounding.lp_grounding import ground_problem_schemas_into_plain_operators
from generalFunc import loadPDDLProblem, restoreTemplate, reCreateDir, setHyps, top1Plans, editDistanceMatrix


# random walk for n steps (not go back)
def randomWalk(problem, steps):
    # create a gfs_model
    gfs_model = GroundForwardSearchModel(problem, ground_problem_schemas_into_plain_operators(problem))
    prevState = ""
    currState = problem.init

    stepCount = 0
    while stepCount < steps:
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
        stepCount += 1

    problem.init = currState
    return problem


def randomWalkInit(steps, oriDomainFile, oriTemplateFile, oriHypsFile):
    selectedGoal, tmpFile = setHyps(oriTemplateFile, oriHypsFile)
    
    problem = loadPDDLProblem(oriDomainFile, tmpFile)
    problem = randomWalk(problem, steps)

    writer = FstripsWriter(problem)
    writer.write("newDomain.pddl", tmpFile)
    restoreTemplate(tmpFile, "newTemplate.pddl", selectedGoal)

    reCreateDir("modified")
    shutil.move("newDomain.pddl", "modified/domain.pddl")
    shutil.move("newTemplate.pddl", "modified/template.pddl")
    shutil.copyfile(oriHypsFile, "modified/hyps.dat")


############################# need put to another place ##################



if __name__ == "__main__":
    #############################################################
    # steps of random walk:
    steps = 50

    # original files:
    oriDomainFile = "original/domain.pddl"
    oriTemplateFile = "original/template.pddl"
    oriHypsFile = "original/hyps.dat"
    #############################################################

    # generates a folder that contains domain.pddl, template.pddl, and hyps.dat
    randomWalkInit(steps, oriDomainFile, oriTemplateFile, oriHypsFile)

    

    ################## added codes for trial #########################
    # check if valid:
    tfFlag1, steps_collection_modified, _ = top1Plans("modified", 100)
    tfFlag2, steps_collection_original, _ = top1Plans("original", 100)
    if tfFlag1 and tfFlag2:
        tf, matrix = editDistanceMatrix(steps_collection_modified, steps_collection_original)
        print(tf)
        print(matrix)

