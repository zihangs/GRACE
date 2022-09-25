import os
import shutil
import random
from env_modifier.generalFunc import reCreateDir, safeRemoveDir, safeRemoveFile


# lapkt check: to configure in 
lapktTimeout = 100   # in seconds
lapktAttempts = 20  
## training set
trainingPlanPerGoal = 10

############################### parameters ###############################
# env_modifier: mandatory
src_envs = "ori_env"
env_change_option = "-InitRW"

# env_modifier: associated
# initRW_step = 10
step_percentage = 0.5



# planner: mandatory
planner_option = "-Topk"
numPlans = 1000
timeLimit = 600 # in seconds


# drift_generator: mandatory
# "-Sudden"; "-Gradual"
# drift_option = "-Gradual"
drift_option = "-Reoccurring"

# drift_generator: associated
sudden_cases_per_env = 50

gradual_stable_period = 50
gradual_changing_period = 50


casePerEnv = 50
reoccurTimes = 2


def env_modifier(src_envs):
    safeRemoveDir("./env_modifier/" + src_envs)
    shutil.copytree("./" + src_envs, "./env_modifier/" + src_envs)
    
    # change dir to modifier and run 
    os.chdir("./env_modifier")

    if env_change_option == "-InitRW":
        os.system("python3 runScript.py %s %s %s %s %s" % (src_envs, env_change_option, str(step_percentage), str(lapktTimeout), str(lapktAttempts)) )

    # change dir back
    os.chdir("../")
    safeRemoveDir(src_envs + "_output_problems")
    shutil.move("./env_modifier/" + src_envs + "_output_problems" , "./")
    safeRemoveDir(src_envs + "_output_templates")
    shutil.move("./env_modifier/" + src_envs + "_output_templates" , "./")
    safeRemoveFile("goal_count.csv")
    shutil.move("./env_modifier/goal_count.csv", "./")

    # the output dirName will be used by planner (next)
    output_fill_goals = src_envs + "_output_problems"

    return output_fill_goals


def planner1(src_problems):
    # src_problems = output_fill_goals

    if planner_option == "-Topk":
        # move the output_fill_goals to planner
        safeRemoveDir("./planner/symk/" + src_problems)
        shutil.copytree("./" + src_problems, "./planner/symk/" + src_problems)
        # shutil.move("./env_modifier/" + src_problems, "./planner/symk/")
        # change dir to symk planner
        os.chdir("./planner/symk/")
        os.system("python3 genePlans.py %s %s %s" % (src_problems, str(numPlans), str(timeLimit)) )

    # change dir back
    os.chdir("../../")

    src_plans = src_envs + "_output_problems_src_plans"
    safeRemoveDir(src_plans)
    shutil.move("./planner/symk/" + src_envs + "_output_problems" , "./" +  src_plans)

    return src_plans


def trainingSetPartition(src_plans):
    # copy the src plans
    cpplans = src_envs + "_output_problems_plans"
    safeRemoveDir(cpplans)
    shutil.copytree(src_plans , cpplans)

    # the plans are directly added into "src_problems"
    # move some plans out to *** training set ***
    reCreateDir("training")
    for domain in os.listdir(cpplans):
        if str(domain)[0] == ".":
            continue
        pathOfDomain = cpplans + "/" + str(domain)
        pathOfDomain_training = "training/" + str(domain)
        reCreateDir(pathOfDomain_training)

        for a_problem in os.listdir(pathOfDomain):
            if str(a_problem)[0] == ".":
                continue
            pathOfProblem = pathOfDomain + "/" + str(a_problem)
            pathOfProblem_training = pathOfDomain_training + "/" + str(a_problem)
            reCreateDir(pathOfProblem_training)

            for an_env in os.listdir(pathOfProblem):
                if an_env == "env0":
                    for a_goal in os.listdir(pathOfProblem +"/env0"):
                        if str(a_goal)[0] == ".":
                            continue
                        pathOfGoal = pathOfProblem + "/env0/" + str(a_goal)
                        pathOfGoal_training = pathOfProblem_training + "/" + str(a_goal)
                        reCreateDir(pathOfGoal_training)

                        planList = os.listdir(pathOfGoal)
                        random.shuffle(planList)
                        for i in range(trainingPlanPerGoal):
                            a_plan = planList[i]
                            shutil.move(pathOfGoal+"/"+a_plan, pathOfGoal_training)

    return cpplans



def planner(src_problems):
    # src_problems = output_fill_goals

    if planner_option == "-Topk":
        # move the output_fill_goals to planner
        safeRemoveDir("./planner/symk/" + src_problems)
        shutil.copytree("./" + src_problems, "./planner/symk/" + src_problems)
        # change dir to symk planner
        os.chdir("./planner/symk/")
        os.system("python3 genePlans.py %s %s %s" % (src_problems, str(numPlans), str(timeLimit)) )


    # the plans are directly added into "src_problems"
    # move some plans out to *** training set ***
    reCreateDir("training")
    for domain in os.listdir(src_problems):
        if str(domain)[0] == ".":
            continue
        pathOfDomain = src_problems + "/" + str(domain)
        pathOfDomain_training = "training/" + str(domain)
        reCreateDir(pathOfDomain_training)

        for a_problem in os.listdir(pathOfDomain):
            if str(a_problem)[0] == ".":
                continue
            pathOfProblem = pathOfDomain + "/" + str(a_problem)
            pathOfProblem_training = pathOfDomain_training + "/" + str(a_problem)
            reCreateDir(pathOfProblem_training)

            for an_env in os.listdir(pathOfProblem):
                if an_env == "env0":
                    for a_goal in os.listdir(pathOfProblem +"/env0"):
                        if str(a_goal)[0] == ".":
                            continue
                        pathOfGoal = pathOfProblem + "/env0/" + str(a_goal)
                        pathOfGoal_training = pathOfProblem_training + "/" + str(a_goal)
                        reCreateDir(pathOfGoal_training)

                        for a_plan in os.listdir(pathOfGoal):
                            # move
                            nameList = a_plan.split(".")
                            if int(nameList[1]) <= trainingPlanPerGoal:
                                shutil.move(pathOfGoal + "/" + a_plan, pathOfGoal_training)

    # the plans are directly added into "src_problems"
    output_plans = src_problems
    # change dir back
    os.chdir("../../")

    safeRemoveDir("training")
    shutil.move("./planner/symk/training" , "./")
    safeRemoveDir(src_envs + "_output_problems_plans")
    shutil.move("./planner/symk/" + src_envs + "_output_problems" , "./" + src_envs + "_output_problems_plans" )

    return output_plans



def drift_generator(output_plans):

    # copy the plans to drift_generator/
    # safeRemoveDir("./drift_generator/" + output_plans)
    # shutil.copytree("./" + output_plans, "./drift_generator/" + output_plans)
    # os.system("cp -R ./%s ./drift_generator/%s" % (output_plans, output_plans) )

    os.chdir("./drift_generator/")

    plan_pool_root = output_plans
    for domain in os.listdir(plan_pool_root):
        if str(domain)[0] == ".":
            continue

        pathOfDomain = plan_pool_root + "/" + str(domain)
        for a_problem in os.listdir(pathOfDomain):
            if str(a_problem)[0] == ".":
                continue

            problemPath = pathOfDomain + "/" + str(a_problem)

            # random_select_goal or give_all_goal:
            if drift_option == "-Sudden":
                os.system("python3 driftGenerator.py %s %s %s" % (problemPath, drift_option, str(sudden_cases_per_env)) )
            if drift_option == "-Gradual":
                os.system("python3 driftGenerator.py %s %s %s %s" % (problemPath, drift_option, str(gradual_stable_period), str(gradual_changing_period)) )
            if drift_option == "-Reoccurring":
                os.system("python3 driftGenerator.py %s %s %s %s" % (problemPath, drift_option, str(casePerEnv), str(reoccurTimes)) )


            # remove the original pools of plans, the output is a sequence of plans (a drift)
            os.system("rm -rf %s/" % problemPath)
            # output for all types of drifts are the same: outputDrift/
            os.system("mv outputDrift/ %s/" % problemPath)


    # change dir back
    os.chdir("../")
    safeRemoveDir(output_plans + "_drift")
    shutil.move("./drift_generator/" + output_plans , "./" + output_plans + "_drift")

    return True



output_fill_goals = env_modifier(src_envs)

# if len(os.listdir("./ori_env_output_problems")) != 0:
#     output_fill_goals = "./ori_env_output_problems"
#     output_plans = planner(output_fill_goals)

#     if len(os.listdir("./ori_env_output_problems_plans")) != 0:

#         output_plans = "ori_env_output_problems_plans"
#         drift_generator(output_plans)


# output_fill_goals = "./ori_env_output_problems"
# output_plans = planner1(output_fill_goals)
# print(output_plans)

# trainingSetPartition("ori_env_output_problems_src_plans")


# output_plans = "ori_env_output_problems_plans"
# drift_generator(output_plans)

# ############################ collect data ########################
# output_collection = "output_collection/"
# reCreateDir(output_collection)

# shutil.move(src_envs + "_output_problems" , output_collection)
# shutil.move(src_envs + "_output_templates" , output_collection)
# shutil.move("goal_count.csv", output_collection)

# shutil.move("training" , output_collection)
# shutil.move(src_envs + "_output_problems_plans" , output_collection + src_envs + "_output_problems_plans" )

# shutil.move(src_envs + "_output_problems_plans_drift" , output_collection + src_envs + "_output_problems_plans_drift")


