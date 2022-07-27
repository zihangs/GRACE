## The Environment Modifier

The environment modifier is a module of Janus

#### Inputs:
The input is a synthetic GR model (the seed environment) including: domain.pddl, template.pddl, and hyps.dat

#### Outputs:
The output is a modified GR model stored in a directory `modified`.

#### Parameters:

Options:
1. remove object:
Running in a docker container, start the container as below:
```sh
docker container start xenodochial_poitras -i
```

2. random walk from init

3. random walk from goal

use other action to change env by planner:



commands: (only modify a single environment)

```sh
python env_modifier.py original -InitRW 10

python env_modifier.py original -ObjectRM 5
```





Environment modifier:



modify the synthetic planning domain with four method options. We packed all required dependencies in a docker container, you can pull the docker image from:



To run the python script `env_modifier.py`, a few parameters need to be specified:



\1) Input (the original enviroment, in PDDL): a domain.pddl, template.pddl, hyps.dat (the goal candidates)



\2) Options: 



`-InitRW`: number of steps



`-ObjectRM`, number of objects to remove



`-ActionRM`: number of actions to remove (the ground actions)



`-GoalRW`: number of steps to backward execute from each goal candidate



\3) Number of new environments require to generate







Examples of commands:



\```sh

\# python env_modifier.py <input> <option> <associated_param> <number_of_env>

python env_modifier.py original_env/ -InitRW 10 1



python env_modifier.py original_env/ -ObjectRM 10 1



python env_modifier.py original_env/ -ActionRM 10 1



python env_modifier.py original_env/ -GoalRW 10 1

\```














 
