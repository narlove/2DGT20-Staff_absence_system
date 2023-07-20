# 2DGT20-Staff_absence_system
DATE: 20/07/2023
## Description
This project was another assignment for a digital technologies class. The goal here is to create a program that allows teachers to easily submit any requests for leave.
## Functions
The program is able to perform the following functions:
 - Submit a leave request, taking in data such as: 
  - A start and end date, selected through a calendar
  - A self-validating start and end time
  - Teacher name/identifying code
  - A leave reason, accessible through a drop down box
 - View leave requests as an administator
  - Delete existing leave requests
  - Edit dates, times and leave reasons on existing leave requests
 - Save data to a CSV file
 - Add users through a JSON file
## Quick overview
 - This project was originally created as an assignment for my digital technologies class.
 - Written in Python, using Tkinter for the GUI
 - The python module cvs is used to save the data to an excel document for saving and loading purposes. The users file is in a JSON format, and is written to
 with the help of the json python module.
 - The program is based on a UI that creates multiple windows for each purpose.
 - This program was written with the intent to follow the iterative design process.
 - This project was a step-up and an attempt to use the GUI's to their fullest potential, limiting the user input and validating each check as much as possible.