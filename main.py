import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from datetime import date
from copy import copy

import time

import subprocess
import sys
import os

import csv
import json

# data is pulled from the users.json file, needs to be global and 'updated' ensures that the code has been pulled for this session
sessionData = {
    "name": None,
    "code": None,
    "isAdmin": False,
    "updated": False
}

# attempt to install tkcalendar on the computer of the person who runs this code
# no virus, just less work for moderators
try:
    import tkcalendar
except ModuleNotFoundError:
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'tkcalendar'])
        import tkcalendar
    except:
        tk.messagebox.showerror('Something went wrong', 
            'Something went wrong while trying to import the necessary modules.')
        quit()

# a basic setter for the session data
def set_session_data(name: str, code: str, isAdmin: bool = False):
    sessionData['name'] = name
    sessionData['code'] = code
    sessionData['isAdmin'] = isAdmin
    sessionData['updated'] = True

# code to keep each window looking the same
def style_window(window: tk.Tk, title: str, hideHomeButton: bool = False):
    window.title("Teacher Absentee Registry - " + title)
    window.resizable(height=False, width=False)
    window.grab_set()

    # this is a workaround to hide unwanted parts of the banner
    banner = ttk.Label(window, text='', font=('Sarabun', 30, 'bold'), background='#a31b37', padding=15, anchor='n', width=100)
    banner.place(x=0, y=0)

    bannerDiv = tk.Frame(window, bg='#a31b37')
    bannerDiv.pack(pady=12.5)

    text = tk.Label(bannerDiv, text=title, foreground='white', bg='#a31b37', font=('Sarabun', 30, 'bold'))
    text.grid(column=0, row=0)

    text.grid_configure(padx=(0, 20))

    # this option was added because some windows are styled, but having a home button makes it too hard to keep track of 
    # the grabset and too difficult when debugging or attempting to catch errors
    if hideHomeButton == False:
        def homeButton():
            mainWindow.deiconify()
            window.destroy()

        homeButton = tk.Button(bannerDiv, text='Home', foreground='black', font=('Sarabun', 15), command=homeButton)
        homeButton.grid(column=1, row=0)

# basic login system using the data from users.json
def open_login():
    loginWindow = tk.Tk() # not sure if it was a good decision, but this is its own window
    # the window completely shuts down after the login is complete and a new main window is opened, so that this window doesn't have to 
    # hide in the background or anything
    loginWindow.resizable(width=False, height=False)
    loginWindow.geometry('400x200')
    loginWindow.title('Login')

    l_user = tk.Label(loginWindow, text='username: ')
    l_user.pack(pady=(10, 0))

    e_user = tk.Entry(loginWindow)
    e_user.pack()

    l_pass = tk.Label(loginWindow, text='password:')
    l_pass.pack(pady=(10, 0))

    e_pass = tk.Entry(loginWindow, show='*')
    e_pass.pack()

    def submit_functionality(event = None):
        username = e_user.get()
        password = e_pass.get()

        if username == '' or password == '':
            messagebox.showwarning('An error occured', 'Ensure you enter both a username and a password.')
            return
        
        foundUser = False
        foundPass = False

        # if the user has inputted a correct username, check that the username matches the one in the json
        with open('users.json', 'r') as f:
            data = json.load(f)
            for profile in data:
                if username != data[profile]["username"]: continue
                foundUser = True

                fullProfile = data[profile]

                if password != fullProfile["password"]: continue
                foundPass = True

                set_session_data(
                    fullProfile['name'],
                    profile,
                    fullProfile['isAdmin']
                )

                loginWindow.destroy()
                
                open_main_menu()

            if foundUser == False or foundPass == False:
                messagebox.showerror('An error occured', 'Ensure the password and username match.')

    b_submit = tk.Button(loginWindow, text='submit', pady=5, padx=10, command=submit_functionality)
    loginWindow.bind('<Return>', submit_functionality) # nice line of code allows you to press enter to submit the form
    b_submit.pack(pady=20)

    loginWindow.mainloop()

# strv is a string variable - is basically the primary method of passing data around in this project
# preexistingdata allows the program to autofill old data
# oldWindow is for the grabset error fix, see below
def open_date_select(strv_edit: tk.StringVar, preexistingData: dict[str, str] = None, oldWindow: tk.Tk = None):
    # don't use style window, not worth it

    window = tk.Toplevel()
    window.geometry('600x400')
    window.title('Teacher Absentee Registry - Date select')
    window.resizable(height=False, width=False)
    
    window.grab_set()

    # if this window is closed using the X, the grabset is auto converted back to the previous window before this one closes
    # stops the user from opening a lot of unwanted windows at once
    def try_grab_set_previous():
        try:
            oldWindow.grab_set()
            window.destroy()
        except:
            return

    window.protocol("WM_DELETE_WINDOW", try_grab_set_previous)

    banner = ttk.Label(window, text='Date Select', foreground='white', font=('Sarabun', 30, 'bold'), background='#a31b37', padding=15, anchor='n', width=100)
    banner.pack(pady=(0, 10))

    dateFrame = tk.Frame(window)
    dateFrame.pack()

    # if there is data to autofill, do it. otherwise, ignore it
    currentHour = tk.StringVar(window, value='00')
    if preexistingData != None and preexistingData['hour'] != None and preexistingData['hour'] != ' ': 
        currentHour.set(preexistingData['hour'])
    currentMinute = tk.StringVar(window, value='00')
    if preexistingData != None and preexistingData['minute'] != None and preexistingData['minute'] != ' ': 
        currentMinute.set(preexistingData['minute'])

    # 4 functions - the validate functions ensure that the inputted times are appropriate and the invalid functions
    # specify what to do in the case they're not
    def hourValidateFunction(newValue):
        try:
            int_newValue = int(newValue)
        except ValueError:
            return False
        
        # needs to be a valid time
        if int_newValue < 0 or int_newValue > 23:
            return False

        return True

    def hourInvalidFunction(newValue):
        try:
            # cap it - makes it more user friendly + the user can understand why they can't have a super high number
            int_newValue = int(newValue)
            replaceValue = max(min(23, int_newValue), 0)
            replaceValue = f'{replaceValue:02}'
        except ValueError:
            replaceValue = '00'

        selectHour.delete(0, tk.END)
        selectHour.insert(0, replaceValue)

    def minuteInvalidFunction(newValue):
        try:
            int_newValue = int(newValue)
            replaceValue = max(min(59, int_newValue), 0)
            replaceValue = f'{replaceValue:02}'
        except ValueError:
            replaceValue = '00'

        selectMin.delete(0, tk.END)
        selectMin.insert(0, replaceValue)

    def minuteValidateFunction(newValue):
        try:
            int_newValue = int(newValue)
        except ValueError:
            return False

        if int_newValue < 0 or int_newValue > 59:
            return False
        
        return True

    selectHour = tk.Spinbox(dateFrame, textvariable=currentHour, from_=0, to=23, validate='focus', 
                            validatecommand=(window.register(hourValidateFunction), '%P'), invalidcommand=(window.register(hourInvalidFunction), '%P'),
                            format='%02.0f')

    selectHour.grid(column=0, row=0)
    hourExplain = tk.Label(dateFrame, text='Hour', font=('Sarabun', 9, 'italic'))
    hourExplain.grid(column=0, row=1)

    divider = tk.Label(dateFrame, text=':')
    divider.grid(column=1, row=0)

    selectMin = tk.Spinbox(dateFrame, textvariable=currentMinute, from_=0, to=59, validate='focus', 
                        validatecommand=(window.register(minuteValidateFunction), '%P'), invalidcommand=(window.register(minuteInvalidFunction), '%P'),
                        format='%02.0f')
    selectMin.grid(column=2, row=0)
    minExplain = tk.Label(dateFrame, text='Minute', font=('Sarabun', 9, 'italic'))
    minExplain.grid(column=2, row=1)

    # a calendar that should be filled with preexisting data if it exists, otherwise put it to the current day in the calendar
    if preexistingData != None and preexistingData['date'] != None and preexistingData['date'] != ' ': 
        structDate = time.strptime(preexistingData['date'], '%d/%m/%y')
        cal = tkcalendar.Calendar(window, selectmode = 'day', 
            year = structDate.tm_year, month = structDate.tm_mon,
            day = structDate.tm_mday,
            mindate = date(1971, 1, 1), maxdate = date(2068, 12, 31))
    else:
        current = time.localtime()
        cal = tkcalendar.Calendar(window, selectmode = 'day', 
            year = current.tm_year, month = current.tm_mon,
            day = current.tm_mday,
            mindate = date(1971, 1, 1), maxdate = date(2068, 12, 31))

    cal.pack(pady = 20)

    # transfer the data
    def submitFunc():
        returnDate = cal.get_date().replace('/', '-')
        returnDate = time.strptime(returnDate, '%m-%d-%y')

        try:
            formattedTime = time.strptime(f'{returnDate.tm_year}-{returnDate.tm_mon}-{returnDate.tm_mday} {currentHour.get()}:{currentMinute.get()}', '%Y-%m-%d %H:%M')
        except ValueError:
            messagebox.showwarning('An error occured', 'Please check your time value.')
            return

        strv_edit.set(time.strftime('%d/%m/%y %H:%M', formattedTime))

        window.destroy()

    submitButton = tk.Button(window, text='Submit', command=submitFunc)
    submitButton.pack()

# ensure there are no duplicates in the csv as this breaks the process for finding specific lines and editing/removing them
def check_possible_duplicates(line: list[str]) -> bool:
    with open('data.csv', 'r') as inp:
        reader = csv.reader(inp)

        for row in reader:
            if line == row:
                return True
            
    return False

# getting rid of duplicates as a last resort
def remove_duplicates():
    lines = []

    # basically writes to a new file without any line that may be a duplicate
    # and then renames that tempData file to the standard data file
    with open('data.csv', 'r') as inp, open('tempData.csv', 'w', newline='') as out:
        reader = csv.reader(inp)
        writer = csv.writer(out, delimiter=',')
        for row in reader:
            # for readability, dont really need
            lines.append(row)

        for line in lines:
            duplicateYet = False

            for row in reader:
                if line == row:
                    duplicateYet = True
                    break

            # if no duplicate, then add the line here
            if duplicateYet == False:
                writer.writerow(line)

    basePath = os.getcwd()

    os.remove(basePath + '/data.csv')
    os.rename(basePath + '/tempData.csv', basePath + '/data.csv')

def open_teacher_form():
    window = tk.Toplevel()
    mainWindow.withdraw()
    window.protocol("WM_DELETE_WINDOW", lambda: quit()) # using quit() here ensures the whole program closes and nothing
    # is left open in the background
    window.geometry('600x400')
    
    # the code that is unfinished would have gone here, replacing this, if it were bugfree

    style_window(window, 'Absentee Form')

    l_teacherCode = tk.Label(window, text="Enter your teacher code: ")
    l_teacherCode.pack(pady=(20, 0))

    b_teacherCode = tk.Entry(window, width=20, justify=tk.CENTER)
    b_teacherCode.insert(0, sessionData.get('code'))
    b_teacherCode.config(state='disabled')
    b_teacherCode.pack()

    l_leaveStart = tk.Label(window, text="Enter the start of your leave: ")
    l_leaveStart.pack(pady=(20, 0))

    strv_leaveStart = tk.StringVar(window)
    strv_leaveStart.set('Click to set date')

    b_leaveStart = tk.Button(window, textvariable=strv_leaveStart, width=20, justify=tk.CENTER, command=lambda: open_date_select(strv_leaveStart))
    b_leaveStart.pack()

    l_leaveEnd = tk.Label(window, text="Enter the end of your leave: ")
    l_leaveEnd.pack(pady=(20, 0))

    strv_leaveEnd = tk.StringVar(window)
    strv_leaveEnd.set('Click to set date')

    b_leaveEnd = tk.Button(window, textvariable=strv_leaveEnd, width=20, justify=tk.CENTER, command=lambda: open_date_select(strv_leaveEnd))
    b_leaveEnd.pack()

    LEAVE_TYPE = [
        'Sick leave',
        'Long service leave',
        'Carers leave',
        'Special leave',
        'Unpaid leave'
    ]

    leaveTypeValue = tk.StringVar(window)
    leaveTypeValue.set(LEAVE_TYPE[0]) # default value

    leaveType = tk.OptionMenu(window, leaveTypeValue, *LEAVE_TYPE)
    #leaveType.configure(image=imgDown, indicatoron=0, compound=tk.RIGHT, width=120)
    leaveType.pack(pady=(20, 0))

    def submit_functionality():
        # basic validation for each type of input
        teacherCode = b_teacherCode.get()
        leaveType = leaveTypeValue.get()

        if teacherCode.isupper() == False:
            messagebox.showwarning('An error occured', 'Please enter a teacher code.')
        elif len(teacherCode) <= 0:
            messagebox.showwarning('An error occured', 'Please enter a teacher code.')

        # start and end time in seconds for comparison
        try:
            startTime_s = time.mktime(time.strptime(strv_leaveStart.get(), '%d/%m/%y %H:%M'))
            endTime_s = time.mktime(time.strptime(strv_leaveEnd.get(), '%d/%m/%y %H:%M'))
        except ValueError:
            messagebox.showerror('An error occured', 'You need to enter a valid time.')
            return

        if endTime_s <= startTime_s:
            messagebox.showerror('An error occured', 'The end time needs to be at least 1 minute after the start time.')
            return

        if check_possible_duplicates([teacherCode, strv_leaveStart.get(), strv_leaveEnd.get(), leaveType]):
            messagebox.showerror('An error occured', 'You cannot have duplicate leave requests submitted.')
            return

        # learnt how to use tkinter messagebox's that actually cancel if you aren't happy with your changes
        # makes the code feel more polished
        msgbx = messagebox.askokcancel('Confirm', 'Press OK to confirm your changes')

        if msgbx != True:
            return

        # please add code
        with open('data.csv', 'a', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow([teacherCode, strv_leaveStart.get(), strv_leaveEnd.get(), leaveType])

        remove_duplicates()

        mainWindow.deiconify()
        window.destroy()

    submitButton = tk.Button(window, text='Submit', foreground='black', font=('Sarabun', 12), command=submit_functionality)
    submitButton.pack(anchor='se', side='bottom', padx=15, pady=15)

def open_admin_panel():
    window = tk.Toplevel()
    mainWindow.withdraw()
    window.protocol("WM_DELETE_WINDOW", lambda: quit())
    window.geometry('1000x300')
    
    style_window(window, "Administrator panel")

    # calling them "div"s because it reminds me of attempting to order things in HTML & CSS
    # also much easier to understand how frames work when they're described as divs
    leftBodyDiv = tk.Frame(window)
    leftBodyDiv.pack(side='left', padx=(100, 0))

    rightBodyDiv = tk.Frame(window)
    rightBodyDiv.pack(side='right', padx=(0, 100))

    def remove_functionality():
        curItem = treeview.focus()
        if curItem == '': return

        item = treeview.item(curItem)
        missIndex = int(item['text'].replace('item', ''))

        # rewrite the csv file missing that one line
        with open('data.csv', 'r') as inp, open('tempData.csv', 'w', newline='') as out:
            reader = csv.reader(inp)
            writer = csv.writer(out, delimiter=',')

            lineCount = 0
            for row in reader:
                lineCount += 1
                if lineCount != missIndex: 
                    writer.writerow(row)

        basePath = os.getcwd()

        os.remove(basePath + '/data.csv')
        os.rename(basePath + '/tempData.csv', basePath + '/data.csv')

        treeview.delete(curItem)

    def edit_functionality():
        curItem = treeview.focus()
        if curItem == '': return

        item = treeview.item(curItem)

        values = item['values']

        # this code is superfluous and needs to be changed to be more succinct
        # basically, it is a copy of the code that the teacher function calls to open
        # it should've been made into one function that is called twice, as opposed to once set of code rewritten twice
        newWindow = tk.Toplevel()

        newWindow.geometry('600x400')
        
        style_window(newWindow, 'Edit values', True)

        l_teacherCode = tk.Label(newWindow, text="Teacher code: ")
        l_teacherCode.pack(pady=(20, 0))

        b_teacherCode = tk.Entry(newWindow, width=20, justify=tk.CENTER)
        b_teacherCode.insert(0, values[0])
        b_teacherCode.config(state='disabled')
        b_teacherCode.pack()

        l_leaveStart = tk.Label(newWindow, text="Enter the start of your leave: ")
        l_leaveStart.pack(pady=(20, 0))

        strv_leaveStart = tk.StringVar(newWindow)
        strv_leaveStart.set(values[1] + " " + values[2])

        # breaking down preexisting data to autofill in the date select
        startPreexisting = {
            'hour': values[2].split(":")[0],
            'minute': values[2].split(":")[1],
            'date': values[1]
        }

        b_leaveStart = tk.Button(newWindow, textvariable=strv_leaveStart, width=20, justify=tk.CENTER, command=lambda: open_date_select(strv_leaveStart, startPreexisting, newWindow))
        b_leaveStart.pack()

        l_leaveEnd = tk.Label(newWindow, text="Enter the end of your leave: ")
        l_leaveEnd.pack(pady=(20, 0))

        strv_leaveEnd = tk.StringVar(newWindow)
        strv_leaveEnd.set(values[3] + " " + values[4])

        endPreexisting = {
            'hour': values[4].split(":")[0],
            'minute': values[4].split(":")[1],
            'date': values[3]
        }

        b_leaveEnd = tk.Button(newWindow, textvariable=strv_leaveEnd, width=20, justify=tk.CENTER, command=lambda: open_date_select(strv_leaveEnd, endPreexisting, newWindow))
        b_leaveEnd.pack()

        LEAVE_TYPE = [
            'Sick leave',
            'Long service leave',
            'Carers leave',
            'Special leave',
            'Unpaid leave'
        ]

        leaveTypeValue = tk.StringVar(newWindow)
        leaveTypeValue.set(LEAVE_TYPE[LEAVE_TYPE.index(values[5])]) # default value

        leaveType = tk.OptionMenu(newWindow, leaveTypeValue, *LEAVE_TYPE)
        leaveType.pack(pady=(20, 0))

        def submit_functionality():
            # same validation as above, hence why this part of the code is unwarranted and would be better as one function
            teacherCode = b_teacherCode.get()
            leaveType = leaveTypeValue.get()

            # start and end time in seconds for comparison
            startTime_s = time.mktime(time.strptime(strv_leaveStart.get(), '%d/%m/%y %H:%M'))
            endTime_s = time.mktime(time.strptime(strv_leaveEnd.get(), '%d/%m/%y %H:%M'))

            if endTime_s <= startTime_s:
                messagebox.showerror('An error occured', 'The end time needs to be at least 1 minute after the start time.')
                return

            if check_possible_duplicates([teacherCode, strv_leaveStart.get(), strv_leaveEnd.get(), leaveType]):
                messagebox.showerror('An error occured', 'You cannot have duplicate leave requests submitted.')
                return

            msgbx = messagebox.askokcancel('Confirm', 'Press OK to confirm your changes')

            if msgbx != True:
                return

            # THIS IS DIFFERENT
            # it is important, as it looks for the line of code that needs to be edited in the csv using a range of checks
            # (represented as dictionaries). then it rewrites the csv file, omitting the line that needs to be edited, and writes
            # in a new, edited version of the line. it is the major difference between the teacher code (which just submits a new line)
            # and the admin's code, which needs to edit a preexisting leave request
            with open('data.csv', 'r') as csvfile, open('tempData.csv', 'w', newline='') as output:
                reader = csv.reader(csvfile)
                writer = csv.writer(output, delimiter=',')

                checksDefault = {
                    0: False,
                    1: False,
                    2: False,
                    3: False,
                    4: False,
                    5: False
                }

                checksComplete = {
                    0: True,
                    1: True,
                    2: True,
                    3: True,
                    4: True,
                    5: True
                }

                checks = {
                    0: False,
                    1: False,
                    2: False,
                    3: False,
                    4: False,
                    5: False
                }

                for row in reader:
                    # deconstructing row so its the same format
                    newRow = [row[0], row[1].split(' ')[0], row[1].split(' ')[1], row[2].split(' ')[0], row[2].split(' ')[1], row[3]]
                    
                    # copy as otherwise the variable changes to the reference, but we don't want to edit checksDefault or checksComplete
                    checks = copy(checksDefault)

                    for i in range(0, 6):
                        if newRow[i] == values[i]:
                            # need to exit
                            checks[i] = True
                        else:
                            writer.writerow(row)
                            checks = copy(checksDefault)
                            break
                    # if loop completes, we have our row number
                    if checks == checksComplete:
                        # this is the row to not include in the new version
                        # therefore anytime it breaks before this we should write that row to the new file
                        # then, for this row, we need to replace it
                        writer.writerow([teacherCode, strv_leaveStart.get(), strv_leaveEnd.get(), leaveType])
                        checks = copy(checksDefault)
                        continue

            basePath = os.getcwd()

            os.remove(basePath + '/data.csv')
            os.rename(basePath + '/tempData.csv', basePath + '/data.csv')

            remove_duplicates()

            # quickly rewrites the treeview, so that the user can see the changes have taken place
            for item in treeview.get_children():
                treeview.delete(item)

            with open('data.csv', 'r', newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter=',')
                count = 0
                for row in reader:
                    count += 1

                    startValues = row[1].split(' ')
                    endValues = row[2].split(' ')

                    treeview.insert('', tk.END, text="item"+str(count), values=[row[0], startValues[0], startValues[1], endValues[0], endValues[1], row[3]])

            newWindow.destroy()

        submitButton = tk.Button(newWindow, text='Submit', foreground='black', font=('Sarabun', 12), command=submit_functionality)
        submitButton.pack(anchor='se', side='bottom', padx=15, pady=15)

    b_remove = tk.Button(leftBodyDiv, text="remove", width=10, command=remove_functionality)
    b_edit = tk.Button(leftBodyDiv, text="edit", width=10, command=edit_functionality)

    b_edit.pack(pady=10)
    b_remove.pack(pady=10)

    treeview = ttk.Treeview(
        rightBodyDiv,
        show="headings",
        columns=["code", "startTime", "startDate", "endTime", "endDate", 'type'], 
        height=5)  # table

    columnWidth = 110

    treeview.column('code', width=columnWidth)
    treeview.column('startTime', width=columnWidth)
    treeview.column('startDate', width=columnWidth)
    treeview.column('endTime', width=columnWidth)
    treeview.column('endDate', width=columnWidth)
    treeview.column('type', width=columnWidth)

    treeview.heading('code', text='Teacher code')
    treeview.heading('startTime', text='Start Time')
    treeview.heading('startDate', text='Start Date')
    treeview.heading('endTime', text='End Time')
    treeview.heading('endDate', text='End Date')
    treeview.heading('type', text='Leave Type')

    treeview.grid(row=1, column=1)
    vbar = ttk.Scrollbar(rightBodyDiv, orient=tk.VERTICAL, command=treeview.yview)
    treeview.configure(yscrollcommand=vbar.set)
    vbar.grid(row=1, column=2, sticky='ns')

    for item in treeview.get_children():
        treeview.delete(item)

    # read data from the csv (yes, same code - needs to be in a function, in an optimised world)
    with open('data.csv', 'r', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        count = 0
        for row in reader:
            count += 1

            startValues = row[1].split(' ')
            endValues = row[2].split(' ')

            treeview.insert('', tk.END, text="item"+str(count), values=[row[0], startValues[0], startValues[1], endValues[0], endValues[1], row[3]])

def open_main_menu():
    global mainWindow

    mainWindow = tk.Tk()
    mainWindow.geometry('600x400')
    mainWindow.title('Teacher Absentee Registry')
    mainWindow.resizable(height=False, width=False)

    strv_name_prefix = "Hello, "
    strv_name = tk.StringVar(mainWindow, strv_name_prefix + 'NONE')
    
    # check that the sessiondata has been correctly updated
    if sessionData['updated'] == False:
        messagebox.showerror("Ensure you have logged in first!")
        quit()

    # grabs the users name - i think this makes it look more advanced
    strv_name.set(strv_name_prefix + sessionData['name'])

    banner = ttk.Label(mainWindow, text='Home', foreground='white', font=('Sarabun', 30, 'bold'), background='#a31b37', padding=15, anchor='n', width=100)
    banner.pack(pady=(0, 10))

    # just something to look more polished and feel nice
    tkstrv_currentTime = tk.StringVar(mainWindow)
    currentTimePrefix = 'The time is currently: '
    timeAppend = time.strftime('%H:%M:%S', time.localtime())
    tkstrv_currentTime.set(currentTimePrefix + timeAppend)

    def time_update():
        tkstrv_currentTime.set(currentTimePrefix + time.strftime('%H:%M:%S', time.localtime()))

        mainWindow.after(1000, time_update)

    helloLabel = tk.Label(mainWindow, textvariable=strv_name, foreground='black', font=('Sarabun', 20))
    helloLabel.pack()

    timeLabel = tk.Label(mainWindow, textvariable=tkstrv_currentTime, foreground='black', font=('Sarabun', 16))
    timeLabel.pack()

    questionLabel = tk.Label(mainWindow, text='What would you like to do?', foreground='black', font=('Sarabun', 20), pady=10)
    questionLabel.pack()

    teachersButton = tk.Button(mainWindow, text='Teacher absentee form', foreground='black', font=('Sarabun', 12), command=open_teacher_form)
    teachersButton.pack(pady=10)

    adminState = 'disable' if sessionData.get('isAdmin') == False else 'active'

    adminButton = tk.Button(mainWindow, text='Administrator panel', foreground='black', font=('Sarabun', 12), state=adminState, command=open_admin_panel)
    adminButton.pack(pady=10)

    quitButton = tk.Button(mainWindow, text='Quit', foreground='black', font=('Sarabun', 12), command=lambda:quit())
    quitButton.pack(anchor='se', side='bottom', padx=15, pady=15)

    mainWindow.after(1000, time_update)
    mainWindow.mainloop()

open_login()