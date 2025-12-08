import re
import os
import sys
from typing import Dict, List, Tuple

from ortools.sat.python import cp_model as cp
from matplotlib import pyplot as plt


def generate_graph(rows: int, cols: int) -> Tuple[List[int], List[Tuple[int, int]], Dict[int, List[int]]]:
    edges = []
    neighbors = {}
    for r in range(rows):
        for c in range(cols):
            node = r * cols + c
            neighbors[node] = []
            for dr in [-2, -1, 1, 2]:
                for dc in [-2, -1, 1, 2]:
                    if abs(dr) != abs(dc):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < rows and 0 <= nc < cols:
                            neighbor = nr * cols + nc
                            neighbors[node].append(neighbor)
                            if neighbor > node:
                                edges.append([node, neighbor])

    return list(range(rows * cols)), edges, neighbors


def solve_puzzle(nodes: List[int], edges: List[Tuple[int, int]], neighbors=Dict[int, List[int]]) -> List[int]:
    num_nodes = len(nodes)
    model = cp.CpModel()

    # add ordering variables
    u = {}
    for i in range(num_nodes):
        u[i] = model.NewIntVar(lb=1, ub=num_nodes, name=f"U({i})")

    # add boolean variables
    x = {}
    for i in range(num_nodes):
        for j in neighbors[i]:
            x[(i, j)] = model.NewBoolVar(name=f"X({i}, {j})")

    # TSP MTZ formulation
    for i in range(num_nodes):
        model.Add(sum(x[(i, j)] for j in neighbors[i]) == 1)
        model.Add(sum(x[(j, i)] for j in neighbors[i]) == 1)
    for i in range(num_nodes):
        if neighbors[0] != [] and i != neighbors[0][0]:
            for j in neighbors[i]:
                model.Add(u[i] - u[j] + 1 <= (num_nodes - 1) * (1 - x[(i, j)]))
    # redundant constraint
    model.AddAllDifferent([u[i] for i in range(num_nodes)])

    # solve CP
    solver = cp.CpSolver()
    status = solver.solve(model)
    print(f"Solve time: {solver.wall_time}")

    solution = []
    if status == cp.OPTIMAL or status == cp.FEASIBLE:
        for i in range(num_nodes):
            solution.append(solver.value(u[i] - 1))

    return solution


def write_output(solution: List[int], rows: int, cols: int, file: str):
    with open(file, "w") as f:
        for r in range(rows):
            for c in range(cols):
                node = r * cols + c
                f.write(f"{solution[node]:>6}")
            f.write("\n")


def draw_output(solution: List[int], rows: int, cols: int, file: str):
    x_points = []
    y_points = []
    for i in range(rows * cols):
        n = solution.index(i)
        r = n // cols
        c = n % cols
        x_points.append(c + 0.5)
        y_points.append(rows - r - 1 + 0.5)
    x_points.append(x_points[0])
    y_points.append(y_points[0])
    fig, ax = plt.subplots(figsize=(cols, rows))
    ax.plot(x_points, y_points, marker="o", color="black")
    ax.grid(True, which="major", axis="both")
    ax.set_xlim(0, cols)
    ax.set_ylim(0, rows)
    ax.set_xticks([i for i in range(cols + 1)])
    ax.set_yticks([i for i in range(rows + 1)])
    ax.tick_params(
        axis="both",  # Apply to both x and y axes
        which="both",  # Apply to both major and minor ticks (if minor exist)
        length=0,  # Set tick length to 0 to hide tick marks
        labelbottom=False,  # Hide x-axis labels
        labelleft=False,  # Hide y-axis labels
        bottom=False,  # Hide bottom tick marks
        left=False,  # Hide left tick marks
        top=False,  # Hide top tick marks
        right=False,  # Hide right tick marks
    )
    fig.savefig(file)


def main():

    # get grid size from command line first argument
    grid = sys.argv[1]
    rows, cols = map(int, grid.split("x"))

    # display
    print(f"Finding Knight's Tour on a {rows}x{cols} board...")

    # generate graph
    nodes, edges, neighbors = generate_graph(rows, cols)
    print(f"Generated graph with {len(nodes)} nodes and {len(edges)} edges.")

    # solve puzzle
    print(f"Solving...")
    solution = solve_puzzle(nodes, edges, neighbors)
    if solution == []:
        print("No solution found.")
        return

    # set output file name
    outputfile = f"{rows}x{cols}-solution.dat"

    # write output
    write_output(solution, rows, cols, outputfile)

    # set output file name for figure
    outputfile = f"{rows}x{cols}-solution.png"

    # draw output
    draw_output(solution, rows, cols, outputfile)


if __name__ == "__main__":
    main()
