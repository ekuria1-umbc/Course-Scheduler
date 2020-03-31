from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from ortools.sat.python import cp_model


def SimpleSatProgram():
    """Minimal CP-SAT example to showcase calling the solver."""
    # Creates the model.
    model = cp_model.CpModel()

    # Creates the variables.
    num_rooms = 3
    course1 = model.NewIntVar(0, num_rooms - 1, 'course1')
    course2 = model.NewIntVar(0, num_rooms - 1, 'course2')
    course3 = model.NewIntVar(0, num_rooms - 1, 'course3')

    # Creates the constraints. courses can't be in the same room
    model.Add(course1 != course2)
    model.Add(course2 != course3)
    model.Add(course1 != course3)
    
    # Creates a solver and solves the model.
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.FEASIBLE:
        print('course1 = room %i' % solver.Value(course1))
        print('course2 = room %i' % solver.Value(course2))
        print('course3 = room %i' % solver.Value(course3))


SimpleSatProgram()
