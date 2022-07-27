import os
import shutil
from env_modifier.generalFunc import reCreateDir, safeRemoveDir


# lapkt check: to configure in 
lapktTimeout = 100   # in seconds
lapktAttempts = 10  
## training set
trainingPlanPerGoal = 50

############################### parameters ###############################
# env_modifier: mandatory
src_envs = "ori_env"
env_change_option = "-InitRW"

# env_modifier: associated
# initRW_step = 10
step_percentage = 0.3



# planner: mandatory
planner_option = "-Topk"
numPlans = 1000
timeLimit = 600 # in seconds


# drift_generator: mandatory
drift_option = "-Sudden"

# drift_generator: associated
sudden_cases_per_env = 50

gradual_stable_period = 50
gradual_changing_period = 50


############################## env_modifier #############################
# change dir to modifier and run 
os.chdir("./env_modifier")

if env_change_option == "-InitRW":
    os.system("python3 runScript.py %s %s %s %s %s" % (src_envs, env_change_option, str(step_percentage), str(lapktTimeout), str(lapktAttempts)) )

# the output dirName will be used by planner (next)
output_fill_goals = src_envs + "_output_problems"
# change dir back
os.chdir("../")
################################### planner ###############################
src_problems = output_fill_goals

if planner_option == "-Topk":
    # move the output_fill_goals to planner
    safeRemoveDir("./planner/symk/" + src_problems)
    shutil.copytree("./env_modifier/" + src_problems, "./planner/symk/" + src_problems)
    # shutil.move("./env_modifier/" + src_problems, "./planner/symk/")
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
############################# drift generator ##############################
# copy the plans to drift_generator/
safeRemoveDir("./drift_generator/" + output_plans)
shutil.copytree("./planner/symk/" + output_plans, "./drift_generator/" + output_plans)

# move it to drift_generator/
# shutil.move("./planner/symk/" + output_plans, "./drift_generator/")
# change dir to drift_generator/

# output_plans = "output_plans"   ## need to delete

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


        # remove the original pools of plans, the output is a sequence of plans (a drift)
        os.system("rm -rf %s/" % problemPath)
        # output for all types of drifts are the same: outputDrift/
        os.system("mv outputDrift/ %s/" % problemPath)


# change dir back
os.chdir("../")

############################ collect data ########################
output_collection = "output_collection/"
reCreateDir(output_collection)
# os.mkdir(output_collection)
shutil.move("./env_modifier/" + src_envs + "_output_problems" , output_collection)
shutil.move("./env_modifier/" + src_envs + "_output_templates" , output_collection)
shutil.move("./env_modifier/goal_count.csv", output_collection)

shutil.move("./planner/symk/training" , output_collection)
shutil.move("./planner/symk/" + src_envs + "_output_problems" , output_collection + src_envs + "_output_problems_plans" )

shutil.move("./drift_generator/" + src_envs + "_output_problems" , output_collection + src_envs + "_output_problems_drift")


