import sys
from func_timeout import func_timeout
# Load the default planner
from lapkt.load_planner import Planner

# BrFS Planner configuration (Optimal Planner)
config_BRFS = {
          'log_file': {'var_name': 'log_filename', 'value': 'log'}, 
          'plan_file': {'var_name': 'plan_filename', 'value': 'plan.ipc'}, 
          'planner': {'value': 'BRFS_Planner'}, 
          'lapkt_instance_generator': {'value': 'Tarski'}, 
          'domain': {'value': ''}, 
          'problem': {'value': ''}, 
        }

domain = sys.argv[1]
problem = sys.argv[2]

# Set PDDL domain and problem file path in the planner configuration
config_BRFS['domain'] = {'value': domain}
config_BRFS['problem'] = {'value': problem}

planner_tsp = Planner(config_BRFS)
func_timeout(1, planner_tsp.solve, args=(), kwargs=None)

print("Checked")

