from __future__ import print_function
import argparse
from ortools.sat.python import cp_model
from google.protobuf import text_format
import csv

"""
protype for course scheduler

"""

"""
Outline
1. Create the variables
2. Define the constraints
3. Define the objective function
4. Declare the solver-the method that implements an algorithm
5. invoke the solver and display the results
"""


#Define Room and Course class
class Room:
    def __init__(self, room_num, location, size):
        self.room_num = room_num
        self.location = location
        self.size = size
    
class Course:
    def __init__(self, name, number, subject, section, professor, time, capacity):
        self.name = name
        self.number = number
        self.subject = subject
        self.section = section
        self.location = 0
        self.professor = professor 
        self.capacity = capacity
        self.time = time


#make sample data
def SimpleSatProgram():
    #declare the solver
    model = cp_model.CpModel()

    #create the variables
    #3 courses
    course1 = Course("Problem Solving & Prog.", 104, "CMSC", 1, "Staff", "tt530", 40)
    course2 = Course("Problem Solving & Prog.", 104, "CMSC", 2, "Staff", "mw530", 40)
    course3 = Course("Computer Science I", 201, "CMSC", 1, "Hamilton", "mw1", 60)

    #create course arr
    course_arr = []
    course_arr.append(course1)
    course_arr.append(course2)
    course_arr.append(course3)

    #2 rooms
    room1 = Room(1, "ENG102", 40)
    room2 = Room(2, "ENG302", 60)

    #create room_arr
    room_arr = []
    room_arr.append(room1)
    room_arr.append(room2)
    
    courses = {} 


    #add to model

    courses1 = model.NewIntVar(0, 1, 'courses1')
    courses2 = model.NewIntVar(0,1, 'courses2')
    courses3 = model.NewIntVar(0, 1, 'courses3')

    c_arr = []
    c_arr.append(courses1)
    c_arr.append(courses2)
    c_arr.append(courses3)
    
        #this means room 1 can take on the value of 1-len(room array), can use this ints to determine location
        #we can do this in a loop for all courses in the coure_arr
        #at the end the model will have an array of courses that can get any room from 0-len(room_arr)-1


        #define the constraints

    count1 = -1
    count2 = -1
    #time overlaps for rooms
    for n in course_arr:
        count1 += 1
        count2 = -1
        for j in course_arr:
            count2 += 1
            if(course_arr[count1].time == course_arr[count2].time and count1 != count2):
                model.Add(c_arr[count1] != c_arr[count2])


    #size constraints
    count1 = -1
    count2 = -1
    for n in course_arr:
        count1 += 1
        count2 = -1
        for j in room_arr:
            count2 +=1
            if(course_arr[count1].capacity > room_arr[count2].size):
                model.Add(c_arr[count1] != count2)



        #cp model solver is used for scheduling programs
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    if status == cp_model.FEASIBLE:#NOTE: FEASIBLE NOT OPTIMAL
        print('course1 = room%i' % solver.Value(courses1))
        print('course2=room%i' % solver.Value(courses2))
        print('course3=room%i' %solver.Value(courses3))

SimpleSatProgram()
