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
#use CP-SAT model
model = cp_model.CpModel()

#Create Variables
class Room:
    location = ""
    capacity = ""
    
class Course:
    name = ""
    number =""
    subject = ""
    section = ""
    location = ""
    professor = ""
    length = ""
    start_time = ""
    day = ""
    capacity = ""


#should read the csv file and assign each course to a course object
#and each room to a room object: can be 2 arrays of courses and rooms
def assign_var():
courses = {} 

#make course_arr and room_arr
#make solver arr
for n in course_arr:
    courses[n] = model.NewIntVar(0, len(room_arr) - 1, 'course%i', n)

#this means room 1 can take on the value of 1-len(room array), can use this ints to determine location
#we can do this in a loop for all courses in the coure_arr
#at the end the model will have an array of courses that can get any room from 0-len(room_arr)-1


#define the constraints
"""
Hard Constraints
1. No classes at the same time can have the same professor (but that might be gaurenteed in input )
2. class size <= size
3. No classes at the same time can have the same location

Soft Constraints (determine if any)
"""
#time overlaps for rooms
for n in course_arr:
    for j in course_arr:
        if(n.day == j.day && n.time == j.time):
            model.Add(coursen != coursej)

#size constraints
for n in course_arr:
    for j in room_arr:
        if(n.size > j.size):
            model.Add(coursen != j)


#declare the solver
solver = cp_model.CpSolver()
#cp model solver is used for scheduling programs
status = solver.Solve(model)

if status == cp_model.FEASIBLE:#NOTE: FEASIBLE NOT OPTIMAL
        #print assignments 

#convert to csv
#loop through courses in model so course[1] = 2 means course 1 will be in room 2
#find room 2 in rooms_arr and put location in location variable of course1. elements in course 1 can be columns, each course will be a new row in the csv.
