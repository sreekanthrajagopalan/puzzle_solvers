import os
import sys
from typing import List

from ortools.sat.python import cp_model as cp


def solve_puzzle(model: cp.CpModel, data: List[List]):

    # add variables
    vars = {
        (i, j): (
            model.NewIntVar(lb=1, ub=9, name=f"X({i},{j})")
            if data[i][j] == "?"
            else model.NewIntVar(
                lb=int(data[i][j]), ub=int(data[i][j]), name=f"X({i},{j})"
            )
        )
        for j in range(0, 9)
        for i in range(0, 9)
    }

    # add row constraints
    for i in range(0, 9):
        model.AddAllDifferent([vars[(i, j)] for j in range(0, 9)])

    # add column constraints
    for j in range(0, 9):
        model.AddAllDifferent([vars[(i, j)] for i in range(0, 9)])

    # add block constraints
    for bi in range(0, 3):
        for bj in range(0, 3):
            model.AddAllDifferent(
                [
                    vars[(3 * bi + i, 3 * bj + j)]
                    for i in range(0, 3)
                    for j in range(0, 3)
                ]
            )

    # solve CP
    solver = cp.CpSolver()
    solver.solve(model)
    print(solver.status_name())

    return solver, vars


def write_output(solver: cp.CpSolver, vars: dict, file: str):

    with open(file, "w") as f:
        for i in range(0, 9):
            line = []
            for j in range(0, 9):
                line.append(str(solver.value(vars[(i, j)])))
            f.write("\t".join(line) + "\n")


def main():

    # get input file name from argument
    inputfile = sys.argv[1]

    # read input
    data = [line.split() for line in open(inputfile, "r").readlines()]

    # setup and solve puzzle
    model = cp.CpModel()
    solver, vars = solve_puzzle(model, data)

    # set output file name
    outputfile = os.path.join(
        os.path.dirname(inputfile),
        os.path.splitext(os.path.basename(inputfile))[0]
        + "-solution"
        + os.path.splitext(os.path.basename(inputfile))[1],
    )

    # write output
    write_output(solver, vars, outputfile)


if __name__ == "__main__":
    main()
