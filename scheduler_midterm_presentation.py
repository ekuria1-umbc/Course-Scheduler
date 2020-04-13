from __future__ import print_function
import argparse
from ortools.sat.python import cp_model
from google.protobuf import text_format
import csv

"""

File: scheduler.py
Project: UMBC Scheduler
Author: Group Nine
Date: 4/3/20

Description: This is a working protype for the course scheduler
             More updates and changes to follow in the near future.

Outline

1. Create the variables

2. Define the constraints

3. Define the objective function

4. Declare the solver-the method that implements an algorithm

5. Invoke the solver and display the results

"""

# Define Room and Course class

class Room:
    def __init__(self, location, size, distance):

        self.location = location
        self.size = size
        self.distance = distance
        
class Course:
    def __init__(self, subject, courseNumber, title, version, section, instructor, day, capacity):

        self.subject = subject
        self.courseNumber = courseNumber
        self.title = title
        self.version = version
        self.section = section
        self.instructor = instructor 
        self.day = day
        self.capacity = capacity
        self.time = 0

def loadFiles(courses, location):
    
    # Read in classroom information, store each row's cell into the courses variables
    with open(courses) as csvDataFile:
        csvReader = csv.reader(csvDataFile, delimiter=',')

        # Omits the headers
        next(csvReader, None)

        # Note: Typcasting the "capacity" value to int
        for row in csvReader:
            courseTemp = Course(row[0],row[1],row[2],row[3],row[4],row[5],row[6],int(row[7]))
            course_arr.append(courseTemp)

    # Read in building information, store each row's cells into Classroom variables
    with open(location) as csvDataFile2:
        csvReader2 = csv.reader(csvDataFile2, delimiter = ',')

        # Omits the headers
        next(csvReader2, None)

        # Note: Typecasting the "size" value to int
        for rows in csvReader2:
            classroom = Room(rows[0],int(rows[1]),rows[2])
            class_arr.append(classroom)
            
    # Separate cell 'tt130' into day and time variables for each row
    for x in range(len(course_arr)):
        flag = 0
        
        # For each character in the string 'time'
        for l in range(len(course_arr[x].day)):
            if (flag == 0):
                # Breaks the 'time' string by character
                charNum =  ord(course_arr[x].day[l])
                
                # Is the current character a number?
                if charNum >= 48 and charNum <= 57:
                    # Adds class variable time, Update day variable
                    course_arr[x].time = course_arr[x].day[l:]
                    course_arr[x].day = course_arr[x].day[:l]
                    flag = 1

def SimpleSatProgram():

    # Declare the solver
    c_arr = []
    index = 0
    arrSize = len(class_arr) - 1

    # Create variables for scheduling problem
    for n in course_arr:
        name = 'course'+str(index)
        c_arr.append(model.NewIntVar(0, arrSize, name))
        index+=1
        

   # Define Constraints

   # Distance Constraint
   # Sort the room array by distance
   # Now the smaller indices have shorter distance from ITE Building
    dist_arr = []
    for n in class_arr:
        dist_arr.append(n.distance)
    dist_arr = sorted(dist_arr)
    class_sorted_arr = []
    for n in dist_arr:
        for x in class_arr:
            if(x.distance == n and x not in class_sorted_arr):
                class_sorted_arr.append(x)

    # Time Constraint
    countOne = -1
    countTwo = -1
    for n in course_arr:
        countOne += 1
        countTwo = -1
        for j in course_arr:
            countTwo += 1
            # Are the days the same?
            if course_arr[countOne].day == course_arr[countTwo].day:
               # Are the times the same?
               if course_arr[countOne].time == course_arr[countTwo].time and countOne != countTwo:
                  model.Add(c_arr[countOne] != c_arr[countTwo])


    # Size Constraint
    countOne = -1
    countTwo = -1
    for n in course_arr:
        countOne += 1
        countTwo = -1
        for j in class_sorted_arr:
            countTwo +=1
            # Will the class be able to fit into chosen classroom?
            if(course_arr[countOne].capacity > class_sorted_arr[countTwo].size):
                model.Add(c_arr[countOne] != countTwo)       
    
            
    # We want to minimize the distance since every class is CMSC
    # if we minimize that means we try to get the smaller indexes
    # which have the shorter distances
    for n in c_arr:
        model.Minimize(n)
    
    # cp model solver is used for scheduling programs                                                                             
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    count = 0
    # Outputs all optimal solutions
    for n in c_arr:
       if status == cp_model.OPTIMAL:
           print('-----------')
           val = solver.Value(n)
           #print(course_arr[count].title, ' assigned to room ', class_sorted_arr[val].location)
           print(course_arr[count].title);
           print("Room:", class_sorted_arr[val].location)
           print("Instructor:", course_arr[count].instructor)
           print("Time:", course_arr[count].day)

           print('-----------')
           count +=1 
    
if __name__ == "__main__" :
    model = cp_model.CpModel()
    course_arr = []
    class_arr = []

    # Files that needs to be loaded in
    # Note: If you need to load in a different file
    #       modify the variables below
    fileOne = "classRoom.csv"
    fileTwo = "buildingLocation.csv"
    fileThree = "buildingLocationTwo.csv"
    
    # Loads in data
    loadFiles(fileOne, fileTwo)

    # Defines constraints and produces optimal solutions
    SimpleSatProgram()


    

    
