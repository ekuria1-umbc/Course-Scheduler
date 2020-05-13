#!/usr/bin/env python
# coding: utf-8

# In[1]:


# For scheduler algorithm
from __future__ import division
import argparse
from ortools.sat.python import cp_model
from google.protobuf import text_format
import csv
import re
import os

# For UI
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets, uic
import sys, os


# In[2]:


# Read in UI file
qtCreatorFile = "scheduler_UI5.ui" # Enter file here.

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


# In[3]:


# Reads in data from chosen files to lists
# Contains checks to perform internal file analysis
def loadFiles(self, courses, location):
    self.calc_sched_button.setEnabled(True)
    
    # String Error Output
    s = '\n' # Newline Character
    error = "Import Error: "
    errorBuild = ""
    emptyFile = ""
    dataFileErrorInst = "An error occurred  in the following file: "
    noDataErrorInst = "The following file(s) contain no data: "
    formatErrorInst = "Please ensure all columns are properly formatted and contain appropriate data."
    result = False # Was the file import a success?
    caughtException = False # Was an exception caught?
    currentFile = "" # Which file are we currently reading in?
    
    
    lookUpDistance = {'Public Policy':0.4,
                      'Engineering':0.1,
                      'Information Technology':0,
                      'Interdisciplinary Life':0.2,
                      'Janet & Walter Sondheim':0.1,
                      'Meyerhoff Chemistry':0.1,
                      'Sherman Hall': 0.1,
                      'Biological Sciences':0.2,
                      'Math & Psychology': 0.1,
                     }   
    
    # Attempts to load in files
    try:
        # Read in classroom information and store each row's cell into the courses variables
        csvDataFileOne = open(courses, 'r')
        csvDataFileTwo = open(location, 'r')
        
        # Looping Variable
        x = 0
        
        csvReaderOne = csv.reader(csvDataFileOne, delimiter=',')
        
        # Currently reading in courses file
        currentFile = courses

        # Omits the headers
        next(csvDataFileOne, None)

        # Note: Typcasting the "capacity" value to int
        for row in csvReaderOne:
                
            courseTemp = Course(row[0],row[1],row[2],row[3],row[4],row[5],row[6],int(row[7]))
            course_arr.append(courseTemp)
            
            # Separate cell 'tt130' into day and time variables for each row
            splitResults =  re.findall(r'[A-Za-z]+|\d+', course_arr[x].day) 
            course_arr[x].day = splitResults[0]
            course_arr[x].time = splitResults[1]
            splitResults.clear()
            
            # Increments to the next index 
            x += 1
        
        # Continues loading process with second file   
        csvReaderTwo = csv.reader(csvDataFileTwo, delimiter = ',')
        
        # Currently reading in location file 
        currentFile = location

        # Omits the headers
        next(csvReaderTwo, None)

        # Note: Typecasting the "size" value to int
        for rows in csvReaderTwo:
                
            classroom = Room(rows[0],int(rows[1]))
            class_arr.append(classroom)
            
        # Assign distances for each classroom
        
        # For each building name
        for word in lookUpDistance:
            # If it matches the classroom Building name, assign it the distance
            for x in range(len(class_arr)):
                if word in class_arr[x].location:
                    class_arr[x].distance = lookUpDistance[word]
                      
        # No error occurred in both files
        currentFile = "" 
                                       
    # Captures other errors
    except Exception as err:
        
        # Creates string to display which file the error occured in
        errorBuild = dataFileErrorInst + s + currentFile + s
        
        # Clears out read in data to preserve resources
        class_arr.clear()
        course_arr.clear()
        
        # Import Failed
        result = False
        
        # Exception was caught
        caughtException = True
    
    finally:
            # Are the lists populated?
            if(len(class_arr) > 0) and (len(course_arr) > 0):
                result = True
            
            else:
                
                # Lengths of classroom and course list
                classLen = len(class_arr)
                courseLen = len(course_arr)
                
                 # Was an exception caught?                                     
                if(caughtException == True):
                    
                    # Outputs caught exception
                    self.class_results_window.setText(error + errorBuild + s + formatErrorInst)
                
                 # Are the lists empty?
                elif(((classLen == 0) and (courseLen == 0) or (caughtException == False))):
                    
                    # Is the class list empty?
                    if(classLen == 0):
                        emptyFile += courses + s
                    
                    # Is the course list empty?
                    if(courseLen == 0):
                        emptyFile += location + s
                    
                    # Outputs no data error
                    self.class_results_window.setText(error + noDataErrorInst + s + emptyFile 
                                                      + s + formatErrorInst)
                    
                # Prohibits user from pressing "Create Schedule Button"
                # since no data was succesfully imported
                self.calc_sched_button.setEnabled(False)
      
            # Closes files
            csvDataFileOne.close()
            csvDataFileTwo.close()
            
            return result
            


# In[4]:


# Generates constraints for data and finds optimal schedule
def SimpleSatProgram(self):
    
    # Sets global status for this subsection module
    global c_arr, dist_arr, class_sorted_arr
    
    # String Error Output
    error = "Scheduling Error: "
    errorAdvice = "Please contact one of the system administrators for assistance"
    noResults = "Did not find an optimal schedule from provided data set based on constraints."
    
    # Declares the model
    model = cp_model.CpModel()
    
    try: 
        # Clears out out data for new data
        c_arr.clear()
        dist_arr.clear()
        class_sorted_arr.clear()
        
        # Declare the solver
        index = 0
        arrSize = len(class_arr) - 1
  
        # Create variables for scheduling problem
        for n in course_arr:
            c_arr.append(model.NewIntVar(0, arrSize, 'course'+str(index)))
            index+=1
        
        # Define Constraints

        # Distance Constraint
        # Sort the room array by distance
        # Now the smaller indices have shorter distance from ITE Building
        for n in class_arr:
            dist_arr.append(n.distance)
            dist_arr = sorted(dist_arr)
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
                    if(course_arr[countOne].time == course_arr[countTwo].time and countOne != countTwo):
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
     
        # Cp model solver is used for scheduling programs                                                                             
        solver = cp_model.CpSolver()
        status = solver.Solve(model)
        output =  ""
        s = '\n'          # Newline Character
        l = '-----------' # Separator Character
        count = 0
    
        # Outputs all optimal solutions
        for n in c_arr:
            if status == cp_model.OPTIMAL:
                c = course_arr[count].title
                r = str(class_sorted_arr[solver.Value(n)].location) 
                i = str(course_arr[count].instructor)
                d = str(course_arr[count].day)
                t = str(course_arr[count].time)
                output += f" {c}{s} Room: {r}{s} Instructor: {i}{s} Day: {d}{s} Time: {t}{s} {l}{s}"
                
                # Keep track of what data needs to be exported
                optimal_arr.append(Schedule(c, r, i, d, t))
                
                count +=1  
            else:
                output = error + noResults
                
        # Set the output in UI
        self.class_results_window.setText(output)
        
        # Is there optimal data to export?
        # Note: This dictates whether or not the export function becomes 
        #       avaliable to the user
        if(len(optimal_arr) > 0):
            
            # Enables the export button
            self.export_button.setEnabled(True)
            
        print('Statistics')
        print('  - conflicts       : %i' % solver.NumConflicts())
        print('  - branches        : %i' % solver.NumBranches())
        print('  - wall time       : %f s' % solver.WallTime())
    
    # Captures other exceptions
    except Exception as err:
        # Informs user that something went wrong with the optimizer
        self.class_results_window.setText(error + errorAdvice)
        
        # Prevents user from clicking the "Create Schedule" button
        self.calc_sched_button.setEnabled(False)
        
        # Prohibits user from pressing "Export Optimal Schedule" button
        self.export_button.setEnabled(False)
        
        
            
      


# In[5]:


# Exporting Function
def writeOut(self, fileDir):
    
    # String Messages
    status = "Exporting Status: "
    badResults = "Error! There was an issue exporting the data."
    goodResults = "Exporting was successful. The .csv file is located at: "
    newLine = "\n"
    
    try:
        # Name of exported file
        exportPath = str(fileDir) + "/optimalSchedule.csv"
    
        # Transfers optimal data to .csv file
        with open(exportPath, 'w', newline = '') as f:
            category = ['Course', 'Room', 'Instructor', 'Day', 'Time']
            fileWriter = csv.DictWriter(f, fieldnames = category)
            fileWriter.writeheader()
            for i in range(len(optimal_arr)):
                fileWriter.writerow({'Course'     : optimal_arr[i].course,
                                     'Room'       : optimal_arr[i].room, 
                                     'Instructor' : optimal_arr[i].instructor, 
                                     'Day'        : optimal_arr[i].day, 
                                     'Time'       : optimal_arr[i].time})
        f.close()
        
        # Informs user exporting was a success
        self.export_results_window.setText(status + goodResults 
                                           + newLine + exportPath)
     
    # Captures other exceptions
    except Exception as err:
        
        # Informs user exporting was a failure
        self.export_results_window.setText(status + badResults)
        
        # Prohibits user from pressing "Export Optimal Schedule" button
        self.export_button.setEnabled(False)
        
        


# In[6]:


# Define Room, Course, and Schedule classes
class Room:
    def __init__(self, location, size):

        self.location = location
        self.size = size
        self.distance = 100
        
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
        
class Schedule:
    def __init__(self, course, room, instructor, day, time):
        self.course = course
        self.room = room
        self. instructor = instructor
        self.day = day
        self.time = time     


# In[7]:


# UI class
class MainWindow(QtWidgets.QMainWindow):
    #initialize
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi(qtCreatorFile, self)
        self.importResult = True
        self.exportPath = ""
        self.import_files_button.clicked.connect(self.importFiles)
        self.calc_sched_button.clicked.connect(self.CalculateSchedule)
        self.export_button.clicked.connect(self.exportFiles)
        
        # Prohibits user from pressing "Create Schedule" button
        self.calc_sched_button.setEnabled(False)
        
        # Prohibits user from pressing "Export Optimal Results" button
        self.export_button.setEnabled(False)
        
    # Imports/Stores files
    # Contains checks to perform external file analysis
    def importFiles(self):
        
        # Standard Error String Output Builder
        less = "Amount of files loaded was less than two." 
        more = "Amount of files loaded was greater than two." 
        wrongFile = "The following file(s) are invalid: " 
        stdInstOne = "Please ensure the files contain the names 'buildinglocation' and 'classroom'"
        stdInstTwo = "Upload the files in this order: buildinglocation and classroom"
        s = "\n"
        
        # Clears out old data for new data
        class_arr.clear()
        course_arr.clear()
        optimal_arr.clear()
        
        # Clears out old notifications and results
        self.file_results_window.setText(s)
        self.class_results_window.setText(s)
        self.export_results_window.setText(s)
                
        # Gets the files
        fp, _filter = QtWidgets.QFileDialog.getOpenFileNames(self, 'Multiple File',"C:/", '*.csv') 
        
        # Is there appropriate amount of files loaded?
        if(len(fp) == 2):
            
            # Checks for specific file names
            patternOne = fp[0].lower().find(fpOne)
            patternTwo = fp[1].lower().find(fpZero)
            
            # Are the chosen files valid 
            if((patternOne > -1) and (patternTwo > -1)):
                
                # Loads up data
                self.importResult = loadFiles(self, fp[1], fp[0])
        
                # Did the files import successfully?
                if(self.importResult == True):
                    # Allows user from pressing "Create Schedule Button"
                    self.calc_sched_button.setEnabled(True)
                    
                    # Sets export path
                    self.exportPath = fp[1]
                    
                # Displays files that are imported
                self.file_results_window.setText('\n'.join(map(str, fp)))
                
            else:
                # Prevents schedule from being built
                self.importResult = False
                
                # Outputs a string error message for file one
                if((patternOne == -1) and (patternTwo > -1)):
                    self.file_results_window.setText(wrongFile + s + fp[0] 
                                                     + s + s + stdInstOne 
                                                     + s + stdInstTwo)
                    
                # Outputs a string error message for file two    
                elif((patternOne > -1) and (patternTwo == -1)):
                    self.file_results_window.setText(wrongFile + s + fp[1]  
                                                     + s + s + stdInstOne 
                                                     + s + stdInstTwo)
                    
                # Outputs a string error message for files one and two    
                else:
                     self.file_results_window.setText(wrongFile + s + fp[0]  
                                                      + s +  fp[1] + s + s
                                                      + stdInstOne + s + stdInstTwo)    
        else:
            # Prevents schedule from being built
            self.importResult = False
            
            # Outputs file amount error message
            # Less than error
            if(len(fp) < 2):
                 self.file_results_window.setText(less + s + s + stdInstOne + s + stdInstTwo)
                    
            # Greater than error
            else:
                self.file_results_window.setText(more + s + s + stdInstOne + s + stdInstTwo)
    
    # Creates constraints and finds optimal solution
    def CalculateSchedule(self):
          
        # Are the files loaded in and ready to go?
        if(self.importResult == True):   
            # Finds optimal solution
            SimpleSatProgram(self)
        
            # Prohibits user from pressing "Create Schedule Button"
            # Prevents program from building same constraints multiple times
            self.calc_sched_button.setEnabled(False)
            
    # Exports the optimal schedule to .csv file
    def exportFiles(self):
        
            # Grabs directory path from where the imported file was located 
            # Note: Split function below seperates the file directory and 
            #        file name. "fileName" varaible is needed to split up the 
            #        tuple by directory and file
            fileDir, fileName = os.path.split(self.exportPath)
            
            # Executes exporting function 
            writeOut(self, fileDir)
            
           # Prohibits user from pressing "Export Optimal Schedule" button
            self.export_button.setEnabled(False)
            
        
            
    
            


# In[8]:


if __name__ == "__main__":
    course_arr = []
    class_arr = []
    c_arr = []
    class_sorted_arr = []
    dist_arr = []
    optimal_arr = []
    fpZero = 'classroom'
    fpOne = 'buildinglocation'
    
    # Start up and execute application
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
    


# In[ ]:





# In[ ]:




