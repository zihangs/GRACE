## Notice: only works on windows and linux (suggest to build a container)

from func_timeout import func_timeout
# Load the default planner
from lapkt.load_planner import Planner
from generalFunc import setHyps, safeRemoveFile
from time import *
from multiprocessing import Process

def runSearch(timeout, optPlanner):
  func_timeout(timeout, optPlanner.solve, args=(), kwargs=None)

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
    _, tmpProblem = setHyps(template, hyps, index=index)

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
      p2 = Process(target=runSearch, args=(timeout, optPlanner,))
      p2.start()

      i = 0
      while i < timeout:
        sleep(1)
        i += 1

      if p2.is_alive():
        p2.terminate()
        isAllValid = False
        break
      else:
        pass

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

  domain = "segfault/domain.pddl"
  template = "segfault/template.pddl"
  hyps = "segfault/hyps.dat"

  print( validate(timeout, domain, template, hyps) )

####################################################