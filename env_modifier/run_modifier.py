import os
import shutil
import sys


def safeCreateDir(dirName):
    # Check whether the specified path exists or not
    isExist = os.path.exists(dirName)
    if isExist:
        # delete
        shutil.rmtree(dirName)
    
    os.makedirs(dirName)



if __name__ == "__main__":

    method = sys.argv[1]  # "-agent" or "-object"
    script = ""

    # python3 run_modifier.py [outputDir = ]
    # problem = "../original"
    problem = sys.argv[2]
    numEnv = sys.argv[3]
    # agent: number of steps; object: percentage of remove
    param = sys.argv[4]

    if method == "-agent":
        script = "agentRW.py"

    if method == "-object":
        script = "object.py"


    cwd = os.getcwd()
    # don't config this
    outputDir = "./changed"

    #delete output
    os.system("rm -rf %s" % outputDir)

    # copy from the original problem
    os.system("cp -r %s %s" % (problem, outputDir))

    # copy the modifier to working dir
    os.system("cp %s %s" % (script, outputDir))

    # change to working dir
    os.chdir(outputDir)

    f_hyps = open("hyps.dat", "r")
    hypList = f_hyps.readlines()

    goalCount = 0
    for hyp in hypList:
        # copy a template
        os.system("cp template.pddl template_with_goal.pddl")
        f = open("template_with_goal.pddl", "r")
        string = f.read()

        # formalize hyp, replace , with space
        hyp = hyp.replace(",", " ")
        probWithGoal = string.replace("<HYPOTHESIS>", hyp)
        f.close()

        f = open("template_with_goal.pddl", "w")
        f.write(probWithGoal)
        f.close()

        # run the modifier
        os.system("python3 %s domain.pddl template_with_goal.pddl %s %s %s ./" % (script, str(goalCount), numEnv, param))


        goalCount += 1

    f_hyps.close()

    # delete all files
    for item in os.listdir():
        if os.path.isfile(item) and item[0] != ".":
            os.system("rm %s" % item)

    os.chdir(cwd)