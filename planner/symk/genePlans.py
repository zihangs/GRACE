import os
import sys

def generate_Plan(dataPath, number_of_plan, timelimit):

    # number_of_plan = 10
    # dataPath: Path to a single problem in env

    for env in os.listdir(dataPath):
        # pass the hidden dir
        if str(env)[0] == ".":
            continue
        envPath = dataPath + "/" + env
        for goal in os.listdir(envPath):
            # pass the hidden dir
            if str(goal)[0] == ".":
                continue

            goalPath = envPath + "/" + goal

            domain = goalPath + "/domain.pddl"
            problem = goalPath + "/problem.pddl"
            os.system('timeout %s ./fast-downward.py %s %s --search "symk-bd(plan_selection=top_k(num_plans=%s))"'%(str(timelimit), domain, problem, str(number_of_plan))  )

            # os.system("./plan_topk.sh %s %s %s"% (domain, problem, str(number_of_plan)) )
            
            # os.system("rm -rf %s/found_plans/" % goalPath)
            os.system("rm -rf %s/" % goalPath)
            os.system("mv found_plans/ %s/" % goalPath)



if __name__ == "__main__":
    # dataDir = "a_problem"
    # generate_Plan(dataDir, number_of_plan)

    # number_of_plan = 10
    # src_data = "miniout_problems"

    src_data = sys.argv[1]
    number_of_plan = sys.argv[2]
    timelimit = sys.argv[3]
    

    for domain in os.listdir(src_data):
        if str(domain)[0] == ".":
            continue

        pathOfDomain = src_data + "/" + str(domain)
        for a_problem in os.listdir(pathOfDomain):
            if str(a_problem)[0] == ".":
                continue
            dataDir = pathOfDomain + "/" + str(a_problem)
            generate_Plan(dataDir, number_of_plan, timelimit)