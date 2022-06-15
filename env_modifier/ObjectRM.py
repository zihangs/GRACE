import shutil
import random
from tarski.io import FstripsWriter
from generalFunc import loadPDDLProblem, setGoal, restoreTemplate, reCreateDir

def removeObj(problem, obj):
    lang = problem.language
    # remove all predicates related to the object
    for atom in problem.init.as_atoms():
        p = atom.symbol
        arguments = atom.subterms
        lst = []
        toRemove = False
        for a in arguments:
            lst.append(lang.get(str(a)))
            if str(obj) == str(a):
                # print("Remove: ")
                # print(arguments)
                toRemove = True
        if toRemove:
            problem.init.remove(p, *lst)
    
    del lang._constants[str(obj)]
    return problem


def randomRemoveObj(numRemove, oriDomainFile, oriTemplateFile, oriHypsFile):
    selectedGoal, tmpFile = setGoal(oriTemplateFile, oriHypsFile)

    problem = loadPDDLProblem(oriDomainFile, tmpFile)
    lang = problem.language

    allConstantObj = lang.constants() # all objects
    randomIndex = random.sample(range(0, len(allConstantObj)), numRemove)

    for i in randomIndex:
        problem = removeObj(problem, allConstantObj[i])
        print(allConstantObj[i])

    writer = FstripsWriter(problem)
    writer.write("newDomain.pddl", tmpFile)

    restoreTemplate(tmpFile, "newTemplate.pddl", selectedGoal)

    reCreateDir("modified")
    shutil.move("newDomain.pddl", "modified/domain.pddl")
    shutil.move("newTemplate.pddl", "modified/template.pddl")
    shutil.copyfile(oriHypsFile, "modified/hyps.dat")


if __name__ == "__main__":
    # number of object to remove:
    numRemove = 5

    # original files:
    oriDomainFile = "original/domain.pddl"
    oriTemplateFile = "original/template.pddl"
    oriHypsFile = "original/hyps.dat"

    seed = random.randint(0,10000)
    random.seed(seed)  #to replicate the result of paper
    randomRemoveObj(numRemove, oriDomainFile, oriTemplateFile, oriHypsFile)
    print(seed)

