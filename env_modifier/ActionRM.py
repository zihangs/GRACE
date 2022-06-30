import shutil
import random

from generalFunc import loadPDDLProblem, restoreTemplate, reCreateDir, setHyps
from tarski.grounding.lp_grounding import ground_problem_schemas_into_plain_operators
from tarski.search.model import GroundForwardSearchModel
from tarski.io import FstripsWriter

from tarski.syntax import CompoundFormula, Atom
from tarski.fstrips import AddEffect, DelEffect


def delete_random_elems(input_list, n):
    to_delete = set(random.sample(range(len(input_list)), n))
    return [x for i,x in enumerate(input_list) if not i in to_delete]



if __name__ == "__main__":
    ########################## parameters ###########################
    percentageToRemove = 0.5
    oriDomainFile = "original/domain.pddl"
    oriTemplateFile = "original/template.pddl"
    oriHypsFile = "original/hyps.dat"

    ##################################################################
    # load the problem
    selectedGoal, tmpFile = setHyps(oriTemplateFile, oriHypsFile)
    problem = loadPDDLProblem(oriDomainFile, tmpFile)

    # ground the model
    gfs_model = GroundForwardSearchModel(problem, ground_problem_schemas_into_plain_operators(problem))

    # store the ground actions and remove some
    g_actions = gfs_model.operators
    # the number of actions want to remove
    numToRemove = int(len(g_actions) * percentageToRemove)
    g_actions = delete_random_elems(g_actions, numToRemove) 

    # remove all action schemas
    problem.actions.clear()

    # add ground actions to string (types to handle: Atom, CompoundFormula)
    actionStr = ""
    for action in g_actions:
        actionStr += "(:action " + str(action) + "\n"

        actionStr += ":precondition ("
        if isinstance(action.precondition, CompoundFormula):
            actionStr += str(action.precondition.connective) + "\n"
            for subform in action.precondition.subformulas:
                actionStr += str(subform) + "\n"
        else:
            actionStr += str(action.precondition) + "\n"
        actionStr += ")\n"

        actionStr += ":effect (and\n"
        for eff in action.effects:
            if isinstance(eff, AddEffect):
                actionStr += str(eff.atom) + "\n"
            else:  # DeleteEffect
                actionStr += "(not " + str(eff.atom) + ")\n"
        actionStr += ")\n"
        actionStr += ")\n"

    # print(actionStr)

##############################################################
    # output domainFile
    outputDomain = "newDomain.pddl"
    outputTemplete = tmpFile  # overwrite the previous tmpFile

    # how to write the ground problem:
    # 1. list all constants and write into domain.pddl (the objects will be automatically removed from the problem.pddl)
    # 2. delete all action schemas and write the ground actions
    
    # load the problem into the writer
    writer = FstripsWriter(problem) # this problem includes domain and problem
    
    # create a list of all constants
    cons = problem.language._constants
    constantsList = list(cons.values())
    
    domainStr = writer.print_domain(constantsList)  # a str
    domainStrModified = domainStr[0:-1] + actionStr + "\n)"

    with open(outputDomain, 'w') as file:
        file.write(domainStrModified)

    with open(outputTemplete, 'w') as file:
        file.write(writer.print_instance(constantsList))

    
    restoreTemplate(tmpFile, "newTemplate.pddl", selectedGoal)

    reCreateDir("modified")
    shutil.move("newDomain.pddl", "modified/domain.pddl")
    shutil.move("newTemplate.pddl", "modified/template.pddl")
    shutil.copyfile(oriHypsFile, "modified/hyps.dat")

