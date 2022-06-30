import shutil
import random

from tarski.io import FstripsWriter
from tarski.search.model import GroundForwardSearchModel
from tarski.grounding.lp_grounding import ground_problem_schemas_into_plain_operators
from generalFunc import loadPDDLProblem, restoreTemplate, reCreateDir, setHyps



# random walk for n steps
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


if __name__ == "__main__":
    #############################################################
    # steps of random walk:
    steps = 50

    # original files:
    oriDomainFile = "original/domain.pddl"
    oriTemplateFile = "original/template.pddl"
    oriHypsFile = "original/hyps.dat"
    #############################################################

    randomWalkInit(steps, oriDomainFile, oriTemplateFile, oriHypsFile)

