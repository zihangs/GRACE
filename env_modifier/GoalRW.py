import os
import copy
import random
import shutil

from generalFunc import loadPDDLProblem, reCreateDir, setHyps
from tarski.grounding.lp_grounding import ground_problem_schemas_into_plain_operators

from tarski.fstrips import AddEffect, DelEffect
from tarski.syntax import Atom, CompoundFormula
from tarski.evaluators.simple import evaluate


def can_backward(model, operator):
    """ Check whether a given (ground) operator is applicable in the given model (state). """
    flag = False

    for eff in operator.effects:
        # must have no delete effect in model
        if isinstance(eff, DelEffect) and evaluate(eff.atom, model):
            flag = False
            break

        # least one add effect in model
        if isinstance(eff, AddEffect) and evaluate(eff.atom, model):
            flag = True

    return flag


def apply_effect(model, effect, precondition):
    """ Apply the given effect to the given model. """
    # if not is_effect_applicable(model, effect):
    #     return

    if isinstance(effect, AddEffect):
        model.discard(effect.atom.predicate, *effect.atom.subterms)
    elif isinstance(effect, DelEffect):
        pass
    else:
        raise Exception("Unexpected type 1.")

    if isinstance(precondition, CompoundFormula):
        for sub in precondition.subformulas:
            if isinstance(sub, Atom):
                model.add(sub.predicate, *sub.subterms)
            elif isinstance(sub, CompoundFormula):
                for atom in sub.subformulas:
                    model.discard(atom.predicate, *atom.subterms)
            else:
                raise Exception("Unexpected type 2.")

    elif isinstance(precondition, Atom):
        model.add(precondition.predicate, *precondition.subterms)
    
    else:
        raise Exception("Unexpected type 3.")


def goback(state, operator):

    """ Returns the progression of the given state along the effects of the given operator.
    Note that this method does not check that the operator is applicable.
    """
    # TODO This is unnecessarily expensive, but a simple copy wouldn't work either.
    #      If/when we transition towards a C++-backed model implementation, this should be improved.
    sprime = copy.deepcopy(state)

    # Let's push to the beginning the delete effect, to ensure add-after-delete semantics
    effects = sorted(operator.effects, key=lambda e: 0 if isinstance(e, DelEffect) else 1)
    for eff in effects:
        apply_effect(sprime, eff, operator.precondition)
    return sprime


class GroundBackwardSearchModel:
    """ A standard forward search model that operates on a given set of ground operators, obtained through
    reachability analysis or otherwise.
    Note that this is not a particularly performant search model, but rather intended for illustrative purposes
    and for use in low-performance environments.
    """

    def __init__(self, problem, operators):
        self.problem = problem
        self.operators = operators

    def init(self):
        return self.problem.init

    def applicable(self, state):
        """ Return a generator with all ground operators that are applicable in the given state. """
        return (op for op in self.operators if can_backward(state, op))

    def backSuccessors(self, state):
        """ Return a generator with all tuples (op, successor) for successors of the given state. """
        return ((op, goback(state, op)) for op in self.applicable(state))

    def is_goal(self, state):
        """ Return whether the given state is a goal"""
        return evaluate(self.problem.goal, state)  # Just interpret the goal formula on the state

# remove a predicate from the initial state (the type of a predicate is "atom").
def removePredicate(problem, atom):
    p = atom.symbol
    arguments = atom.subterms
    problem.init.remove(p, *arguments)
    return problem

# random walk (Backward) for n steps, operators are the available ground actions
def randomWalkBack(problem, operators, steps):
    # create a gbs_model
    gbs_model = GroundBackwardSearchModel(problem, operators)

    currState = problem.init
    stepCount = 0

    while stepCount < steps:
        succ = gbs_model.backSuccessors(currState)
        # elem in succ is a tuple (operator, state)
        sel = random.choice(list(succ))
        print(sel)
        print("\n")
        currState = sel[1]  # select and re-assign the state
        stepCount += 1

    problem.init = currState
    return problem


if __name__ == "__main__":
    #########################################################
    steps = 10  # steps for random walk for each goal

    oriDomainFile = "original/domain.pddl"
    oriTemplateFile = "original/template.pddl"
    oriHypsFile = "original/hyps.dat"
    #########################################################

    f = open(oriHypsFile, "r")
    goalCount = len(f.readlines()) # get number of goals
    f.close()

    f = open("newHyps.dat", 'w')
    newGoals = ""

    for index in range(goalCount):

        selectedHyps, tmpFile = setHyps(oriTemplateFile, oriHypsFile, index=index)
        
        problem = loadPDDLProblem(oriDomainFile, tmpFile)
        lang = problem.language

        # need ground operators before remove all predicates
        allActions = ground_problem_schemas_into_plain_operators(problem)

        # remove all predicates from initial state
        for atom in problem.init.as_atoms():  # atom is a predicate
            removePredicate(problem, atom)

        # write the predicates in the goal condition into the initial state
        if isinstance(problem.goal, CompoundFormula):
            for atom in problem.goal.subformulas:
                args = [lang.get(str(x)) for x in atom.subterms]
                problem.init.add(atom.symbol, *args)
        elif isinstance(problem.goal, Atom):
            args = [lang.get(str(x)) for x in problem.goal.subterms]
            problem.init.add(problem.goal.symbol, *args)
        else:
            raise Exception("Unexpected type of a goal condidtion")
        

        # random walk (backward) from a goal condition
        problem = randomWalkBack(problem, allActions, steps)

        # need to remove all irrelevant predicates (symbol)
        relevantPredicateSymbols = []
        if isinstance(problem.goal, CompoundFormula):
            for atom in problem.goal.subformulas:
                if isinstance(atom, Atom):
                    relevantPredicateSymbols.append(atom.symbol)
                else:
                    raise Exception("There may be a NOT predicate in goal condition.")
        else:
            if isinstance(problem.goal, Atom):
                relevantPredicateSymbols.append(problem.goal.symbol)
            else:
                raise Exception("There may be a NOT predicate in goal condition.")

        
        for pred in problem.init.as_atoms():
            if pred.symbol in relevantPredicateSymbols:
                newGoals += str(pred) + ", "
        newGoals = newGoals[0:-2] + "\n"

    newGoals = newGoals[0:-1]
    f.write(newGoals)
    f.close()

    reCreateDir("modified")
    shutil.copyfile(oriDomainFile, "modified/domain.pddl")
    shutil.copyfile(oriTemplateFile, "modified/template.pddl")
    shutil.move("newHyps.dat", "modified/hyps.dat")
    os.remove("tmp_template.pddl")






