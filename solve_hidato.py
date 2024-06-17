import os
import sys
from typing import Dict, List, Tuple

from ortools.sat.python import cp_model as cp


def solve_puzzle(model: cp.CpModel, data: List[List]):

    num_nodes = max([int(i) for row in data for i in row if i != "?" and i != "X"])

    # add ordering variables
    u = {}
    node_of_cell = {}
    node = 1
    for i, row in enumerate(data):
        for j, val in enumerate(row):
            # do nothing
            if val == "X":
                continue
            # variable
            else:
                if val == "?":
                    node_of_cell[(i, j)] = node
                    u[node] = model.NewIntVar(lb=2, ub=num_nodes - 1, name=f"U({node})")
                else:
                    node_of_cell[(i, j)] = node
                    u[node] = model.NewIntVar(
                        lb=int(val), ub=int(val), name=f"U({node})"
                    )
                    if int(val) == 1:
                        source = (i, j)
                        source_node = node
                    elif int(val) == num_nodes:
                        target = (i, j)
                        target_node = node
                node += 1

    # find adjacency
    neighbors = {}
    for i, row in enumerate(data):
        for j, val in enumerate(row):
            # do nothing
            if val == "X":
                continue

            node_neighbors = []
            # (i,j) and (i-1,j)
            if i - 1 in range(0, len(data)) and data[i - 1][j] != "X":
                node_neighbors.append(node_of_cell[(i - 1, j)])
            # (i,j) and (i-1,j+1)
            if (
                i - 1 in range(0, len(data))
                and j + 1 in range(0, len(data[i - 1]))
                and data[i - 1][j + 1] != "X"
            ):
                node_neighbors.append(node_of_cell[(i - 1, j + 1)])
            # (i, j) and (i, j + 1)
            if j + 1 in range(0, len(data[i])) and data[i][j + 1] != "X":
                node_neighbors.append(node_of_cell[(i, j + 1)])
            # (i,j) and (i+1,j+1)
            if (
                i + 1 in range(0, len(data))
                and j + 1 in range(0, len(data[i + 1]))
                and data[i + 1][j + 1] != "X"
            ):
                node_neighbors.append(node_of_cell[(i + 1, j + 1)])
            # (i,j) and (i+1,j)
            if i + 1 in range(0, len(data)) and data[i + 1][j] != "X":
                node_neighbors.append(node_of_cell[(i + 1, j)])
            # (i,j) and (i+1,j-1)
            if (
                i + 1 in range(0, len(data))
                and j - 1 in range(0, len(data[i + 1]))
                and data[i + 1][j - 1] != "X"
            ):
                node_neighbors.append(node_of_cell[(i + 1, j - 1)])
            # (i,j) and (i,j-1)
            if j - 1 in range(0, len(data[i])) and data[i][j - 1] != "X":
                node_neighbors.append(node_of_cell[(i, j - 1)])
            # (i,j) and (i-1,j-1)
            if (
                i - 1 in range(0, len(data))
                and j - 1 in range(0, len(data[i - 1]))
                and data[i - 1][j - 1] != "X"
            ):
                node_neighbors.append(node_of_cell[(i - 1, j - 1)])

            if (i, j) == source:
                node_neighbors.append(target_node)
            elif (i, j) == target:
                node_neighbors.append(source_node)

            neighbors[node_of_cell[(i, j)]] = node_neighbors

    # add boolean variables
    x = {}
    for i in range(1, num_nodes + 1):
        for j in neighbors[i]:
            x[(i, j)] = model.NewBoolVar(name=f"X({i}, {j})")

    # TSP MTZ formulation
    for i in range(1, num_nodes + 1):
        model.Add(sum(x[(i, j)] for j in neighbors[i]) == 1)
        model.Add(sum(x[(j, i)] for j in neighbors[i]) == 1)
    for i in range(1, num_nodes + 1):
        if i != target_node:
            for j in neighbors[i]:
                model.Add(u[i] - u[j] + 1 <= (num_nodes - 1) * (1 - x[(i, j)]))
    # redundant constraint
    model.AddAllDifferent([u[i] for i in range(1, num_nodes + 1)])

    # solve CP
    solver = cp.CpSolver()
    solver.solve(model)
    print(solver.status_name())
    print(solver.wall_time)

    return solver, u, node_of_cell


def write_output(
    solver: cp.CpSolver, vars: dict, map: dict, data: List[List], file: str
):

    with open(file, "w") as f:
        for i, row in enumerate(data):
            line = []
            for j, val in enumerate(row):
                if val != "?":
                    line.append(val)
                else:
                    line.append(str(solver.value(vars[map[(i, j)]])))
            f.write("\t".join(line) + "\n")


def main():

    # get input file name from argument
    inputfile = sys.argv[1]

    # read input
    data = [line.split() for line in open(inputfile, "r").readlines()]

    # setup and solve puzzle
    model = cp.CpModel()
    solver, vars, map = solve_puzzle(model, data)

    # set output file name
    outputfile = os.path.join(
        os.path.dirname(inputfile),
        os.path.splitext(os.path.basename(inputfile))[0]
        + "-solution"
        + os.path.splitext(os.path.basename(inputfile))[1],
    )

    # write output
    write_output(solver, vars, map, data, outputfile)


if __name__ == "__main__":
    main()
