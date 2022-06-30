import sys
import ActionRM, GoalRW, InitRW, ObjectRM, lapkt_check
from generalFunc import safeRemoveDir


def iterativeModify(args):
    oriDir = args[1]
    oriDomainFile = oriDir + "/domain.pddl"
    oriTemplateFile = oriDir + "/template.pddl"
    oriHypsFile = oriDir + "/hyps.dat"
    method = args[2]  # "-ObjectRM", "-InitRW", "-GoalRW", "-ActionRM"

    # lapkt timeout
    timeout = 10
    # try to generate valid env for 20 times
    attempts = 20

    modifySucceed = False
    for i in range(attempts):
        if method == "-ObjectRM":
            numRemove = int(args[3])
            ObjectRM.randomRemoveObj(numRemove, oriDomainFile, oriTemplateFile, oriHypsFile)

        elif method == "-InitRW":
            steps = int(args[3])
            InitRW.randomWalkInit(steps, oriDomainFile, oriTemplateFile, oriHypsFile)

        elif method == "-GoalRW":
            pass
        elif method == "-ActionRM":
            pass
        else:
            raise Exception("Method not found.")

        # check if valid (lapkt)
        domain = "modified/domain.pddl"
        template = "modified/template.pddl"
        hyps = "modified/hyps.dat"
        if lapkt_check.validate(timeout, domain, template, hyps):
            modifySucceed = True
            break

    if not modifySucceed:
        safeRemoveDir("modified")

    return modifySucceed


if __name__ == "__main__":
    status = iterativeModify(sys.argv)
    print("Modify Succeed? : " + str(status))