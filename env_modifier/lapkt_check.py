## Notice: only works on windows and linux (suggest to build a container)

from func_timeout import func_timeout
# Load the default planner
from lapkt.load_planner import Planner
from generalFunc import setHyps, safeRemoveFile


def validate(timeout, domain, template, hyps):

  # BrFS Planner configuration (Optimal Planner)
  config_BRFS = {
            'log_file': {'var_name': 'log_filename', 'value': 'log'}, 
            'plan_file': {'var_name': 'plan_filename', 'value': 'plan.ipc'}, 
            'planner': {'value': 'BRFS_Planner'}, 
            'lapkt_instance_generator': {'value': 'Tarski'}, 
            'domain': {'value': ''}, 
            'problem': {'value': ''}, 
          }

  f = open(hyps, "r")
  goalCount = len(f.readlines()) # get number of goals
  f.close()

  isAllValid = True

  for index in range(goalCount):
    selectedHyps, tmpProblem = setHyps(template, hyps, index=index)

    # Set PDDL domain and problem file path in the planner configuration
    config_BRFS['domain'] = {'value': domain}
    config_BRFS['problem'] = {'value': tmpProblem}

    # the domain and problem is totally invalid (no plan can be found)
    try:
      optPlanner = Planner(config_BRFS)
    except:
      isAllValid = False
      break

    #### timeout (may be able to find a plan, but it will spend too much time)
    try:
      func_timeout(timeout, optPlanner.solve, args=(), kwargs=None)
    except:
      isAllValid = False
      break

  safeRemoveFile("tmp_template.pddl")
  safeRemoveFile("plan.ipc")
  return isAllValid

####################################################
if __name__ == "__main__":
  # domain = sys.argv[1]
  # problem = sys.argv[2]
  timeout = 10

  domain = "modified/domain.pddl"
  template = "modified/template.pddl"
  hyps = "modified/hyps.dat"

  print( validate(timeout, domain, template, hyps) )

####################################################