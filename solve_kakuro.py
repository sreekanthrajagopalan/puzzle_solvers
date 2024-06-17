import re
import os
import sys
from typing import Dict, List

from ortools.sat.python import cp_model as cp


def parse_input(model: cp.CpModel, data: List[List]):

    vars = {}
    specs = []

    m = re.compile("(A([0-9]*))?(D([0-9]*))?")

    for i, row in enumerate(data):
        for j, val in enumerate(row):
            # variable
            if val == "?":
                vars[(i, j)] = model.NewIntVar(lb=1, ub=9, name=f"X({i},{j})")
            # do nothing
            elif val == "X":
                continue
            # specification
            else:
                res = m.match(val)

                # Across
                if res.group(2):
                    start = j + 1
                    end = start
                    for k in range(j + 1, len(row)):
                        if data[i][k] == "?":
                            end = k
                        else:
                            break
                    specs.append(("A", i, start, end, int(res.group(2))))

                # Down
                if res.group(4):
                    start = i + 1
                    end = start
                    for k in range(i + 1, len(data)):
                        if data[k][j] == "?":
                            end = k
                        else:
                            break
                    specs.append(("D", j, start, end, int(res.group(4))))

    return vars, specs


def solve_puzzle(model: cp.CpModel, vars: List, specs: Dict):

    # add constraints
    for spec in specs:
        # Across
        if spec[0] == "A":
            model.Add(
                sum(vars[(spec[1], k)] for k in range(spec[2], spec[3] + 1)) == spec[4]
            )
            model.AddAllDifferent(
                [vars[(spec[1], k)] for k in range(spec[2], spec[3] + 1)]
            )

        # Down
        elif spec[0] == "D":
            model.Add(
                sum(vars[(k, spec[1])] for k in range(spec[2], spec[3] + 1)) == spec[4]
            )
            model.AddAllDifferent(
                [vars[(k, spec[1])] for k in range(spec[2], spec[3] + 1)]
            )

    # solve CP
    solver = cp.CpSolver()
    solver.solve(model)
    print(solver.status_name())
    print(solver.wall_time)

    return solver


def write_output(solver: cp.CpSolver, vars: dict, data: List[List], file: str):

    with open(file, "w") as f:
        for i, row in enumerate(data):
            line = []
            for j, val in enumerate(row):
                if val != "?":
                    line.append(val)
                else:
                    line.append(str(solver.value(vars[(i, j)])))
            f.write("\t".join(line) + "\n")


def main():

    # get input file name from argument
    inputfile = sys.argv[1]

    # read input
    data = [line.split() for line in open(inputfile, "r").readlines()]

    # solve CP model
    model = cp.CpModel()
    vars, specs = parse_input(model, data)

    # solve puzzle
    solver = solve_puzzle(model, vars, specs)

    # set output file name
    outputfile = os.path.join(
        os.path.dirname(inputfile),
        os.path.splitext(os.path.basename(inputfile))[0]
        + "-solution"
        + os.path.splitext(os.path.basename(inputfile))[1],
    )

    # write output
    write_output(solver, vars, data, outputfile)


if __name__ == "__main__":
    main()
