import tkinter as tk
from tkinter import ttk

import datetime
from copy import copy

import time

import subprocess
import sys

# Although this code does not work, it was very close to being complete. However, adding it would mean no time to check for bugs 
# and ensure that it functions correctly with the rest of the code.

# GORE WARNING - THIS CODE IS NOT OPTIMISED IN THE SLIGHTEST AND I AM ASHAMED I WROTE IT, NO MATTER HOW FAST I TRIED TO DO IT
# YOU HAVE BEEN WARNED

# same code from main, as this is just a segment taken out of the main code so as not to break it
# would have been better to use github as version control and make this a branch
sessionData = {
    "name": "Admin",
    "code": "ADM",
    "isAdmin": True,
    "updated": True
}

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

def open_date_select(strv_edit: tk.StringVar, preexistingData: dict[str, str] = None):
    # dont style menu here, too simple

    window = tk.Toplevel()
    window.geometry('600x400')
    window.title('Teacher Absentee Registry - Date select')
    window.resizable(height=False, width=False)

    banner = ttk.Label(window, text='Date Select', foreground='white', font=('Sarabun', 30, 'bold'), background='#a31b37', padding=15, anchor='n', width=100)
    banner.pack(pady=(0, 10))

    dateFrame = tk.Frame(window)
    dateFrame.pack()

    # checkbox doesn't use a simple .get() method, instead need to check that the int variable is 1 for on, 0 for off
    multiDaysIntVar = tk.IntVar(window)

    # a function that toggles what is shown depending on the value of the checkbox
    def toggleMulti(event=None):
        selectionFrameSingle.pack_forget()
        selectionFrameMulti.pack_forget()

        clear_buttons()
        endTimes.clear()
        startTimes.clear()

        if multiDaysIntVar.get() == 1:
            selectionFrameMulti.pack()
        else:
            selectionFrameSingle.pack()

    # toggle the lessons shown, if it is a monday it needs to be different
    def toggleDays(event=None):
        rightSelectionFrameNotMonday.grid_forget()
        rightSelectionFrameMonday.grid_forget()

        clear_buttons()
        endTimes.clear()
        startTimes.clear()

        if cal.selection_get().weekday() != 0:
            rightSelectionFrameNotMonday.grid(column=1, row=0)
            rightSelectionFrameNotMonday.grid_configure(padx=30)
        else:
            rightSelectionFrameMonday.grid(column=1, row=0)
            rightSelectionFrameMonday.grid_configure(padx=30)

    multipleDays = tk.Checkbutton(dateFrame, text='Does your leave span multiple days?', variable=multiDaysIntVar, command=toggleMulti)
    multipleDays.pack()

    # lots and lots of divs
    # this needs to be broken down so much because
    # 1. attempting to style without a thoroughly broken down code is a pain
    # 2. making frames disappear and be replaced means that it should be clear which frame is the parent of which
    selectionFrameSingle = tk.Frame(window)
    selectionFrameSingle.pack()

    selectionFrameMulti = tk.Frame(window)

    leftMultiFrame = tk.Frame(selectionFrameMulti)
    leftMultiFrame.grid(column=0, row=0)
    leftMultiFrame.grid_configure(pady=40)

    rightMultiFrame = tk.Frame(selectionFrameMulti)
    rightMultiFrame.grid(column=1, row=0)
    rightMultiFrame.grid_configure(pady=40)

    leftSelectionFrame = tk.Frame(selectionFrameSingle)
    leftSelectionFrame.grid(column=0, row=0)

    rightSelectionFrameMonday = tk.Frame(selectionFrameSingle)

    rightSelectionFrameNotMonday = tk.Frame(selectionFrameSingle)

    # change the day depending on if the day selected is a monday
    # custom tkcalendar event
    window.bind('<<CalendarSelected>>', toggleDays)

    buttonWidth = 7
    
    lessonHeight = 2
    breakHeight = 1

    # setting up frames in the worst way possible
    frame1 = tk.Frame(rightSelectionFrameNotMonday)
    frame1.pack()
    frame2 = tk.Frame(rightSelectionFrameNotMonday)
    frame2.pack()
    frame3 = tk.Frame(rightSelectionFrameNotMonday)
    frame3.pack()
    frame4 = tk.Frame(rightSelectionFrameNotMonday)
    frame4.pack()
    frame5 = tk.Frame(rightSelectionFrameNotMonday)
    frame5.pack()
    frame6 = tk.Frame(rightSelectionFrameNotMonday)
    frame6.pack()

    selectedButtons = []
    startTimes = []
    endTimes = []
    # this code was a lot harder to write than i thought it would be
    def toggle_button(lessonButton: tk.Button, timeStart: str, timeEnd: str):
        # this part is simple - a basic toggle system, if toggled, untoggle when pressed and vice versa
        if lessonButton in selectedButtons:
            selectedButtons.remove(lessonButton)
            lessonButton.config(bg='SystemButtonFace')

            startTimes.remove(timeStart)
            endTimes.remove(timeEnd)
        else:
            selectedButtons.append(lessonButton)
            lessonButton.config(bg='green')

            startTimes.append(timeStart)
            endTimes.append(timeEnd)

        # this section pulls the earliest time out of the buttons the user has selected
        # would be used as a start time for the leave
        earliest = startTimes[0] if len(startTimes) != 0 else "0830"
        for startTime in startTimes:
            if startTime < earliest:
                earliest = copy(startTime)

        # similar but for end
        latest = endTimes[0] if len(endTimes) != 0 else "1535"
        for endTime in endTimes:
            if endTime > latest:
                latest = copy(endTime)

        # debug statement, would be removed in production
        print(str(earliest) + " " + str(latest))

        # this following code attempts to colour the buttons in between two buttons, if the user selects a time at the beginning 
        # and then at the end of the day. it is supposed to be visual feedback that the user has marked their leave as running for the whole 
        # day, rather than just the first and last lesson, but it is much harder to update and keep track of than originally anticipated
        start = -1
        end = -1
        # find start
        count = 0
        for button in allButtons:
            # first check there are two buttons
            if button.cget('bg') == 'green':
                count += 1

        if count >= 2:
            # find start
            for button in allButtons:
                if button.cget('bg') == 'green':
                    start = allButtons.index(button)
                    break

            # find end
            reversedButtons = allButtons[::-1]
            for button in reversedButtons:
                if button.cget('bg') == 'green':
                    end = allButtons.index(button)
                    break

            for button in allButtons:
                if allButtons.index(button) <= start or allButtons.index(button) >= end:
                    continue

                button.config(bg='lime')

    def clear_buttons():
        for button in selectedButtons:
            button.config(bg='SystemButtonFace')
            
        selectedButtons.clear()       

    currentTime = time.localtime()

    allButtons = []

    # the entire following segment of code is duplicated, because one version needed to exist for mondays, with slight alterations
    # but the code for every other day is the same
    # theoretically weekends should not exist on there, but they do anyway
    lesson1button = tk.Button(frame1, text='L1', height=lessonHeight, width=buttonWidth, command=lambda:toggle_button(lesson1button, '0830', '1000'))
    break1button = tk.Button(frame2, state='disabled', text='Break 1', height=breakHeight, width=buttonWidth)
    lesson2button = tk.Button(frame3, text='L2', height=lessonHeight, width=buttonWidth, command=lambda:toggle_button(lesson2button, '1030', '1200'))
    lesson3button = tk.Button(frame4, text='L3', height=lessonHeight, width=buttonWidth, command=lambda:toggle_button(lesson3button, '1205', '1335'))
    break2button = tk.Button(frame5, state='disabled', text='Break 2', height=breakHeight, width=buttonWidth)
    lesson4button = tk.Button(frame6, text='L4', height=lessonHeight, width=buttonWidth, command=lambda:toggle_button(lesson4button, '1405', '1535'))

    # appended for the interval button colour check
    # see above
    allButtons.append(lesson1button)
    allButtons.append(lesson2button)
    allButtons.append(lesson3button)
    allButtons.append(lesson4button)

    lesson1button.pack(side='left', padx=5)
    break1button.pack(side='left', padx=5)
    lesson2button.pack(side='left', padx=5)
    lesson3button.pack(side='left', padx=5)
    break2button.pack(side='left', padx=5)
    lesson4button.pack(side='left', padx=5)

    explain1 = tk.Label(frame1, text='0830-1000', height=lessonHeight).pack(side='right')
    explain2 = tk.Label(frame2, text='1000-1030', height=breakHeight).pack(side='right')
    explain3 = tk.Label(frame3, text='1030-1200', height=lessonHeight).pack(side='right')
    explain4 = tk.Label(frame4, text='1205-1335', height=lessonHeight).pack(side='right')
    explain5 = tk.Label(frame5, text='1335-1405', height=breakHeight).pack(side='right')
    explain6 = tk.Label(frame6, text='1405-1535', height=lessonHeight).pack(side='right')

    # as mentioned, the exact same code with an m in front of the variable names
    # does the same process, but the dates, buttons, number of buttons, etc., are all changed to fit the monday timetable
    mframe1 = tk.Frame(rightSelectionFrameMonday)
    mframe1.pack()
    mframe2 = tk.Frame(rightSelectionFrameMonday)
    mframe2.pack()
    mframe3 = tk.Frame(rightSelectionFrameMonday)
    mframe3.pack()
    mframe4 = tk.Frame(rightSelectionFrameMonday)
    mframe4.pack()
    mframe5 = tk.Frame(rightSelectionFrameMonday)
    mframe5.pack()

    mlesson1button = tk.Button(mframe1, text='L1', height=lessonHeight, width=buttonWidth, command=lambda:toggle_button(mlesson1button, '0830', '1000'))
    mpcgButton = tk.Button(mframe2, text='PCG', height=breakHeight, width=buttonWidth, command=lambda:toggle_button(mpcgButton, '1000', '1045'))
    mbreak1Button = tk.Button(mframe3, text='Break 1', state='disabled', height=breakHeight, width=buttonWidth)
    mlesson2Button = tk.Button(mframe4, text='L2', height=lessonHeight, width=buttonWidth, command=lambda:toggle_button(mlesson2Button, '1115', '1245'))
    mlesson3Button = tk.Button(mframe5, text='L3', height=lessonHeight, width=buttonWidth, command=lambda:toggle_button(mlesson3Button, '1250', '1420'))

    mlesson1button.pack(side='left', padx=5)
    mpcgButton.pack(side='left', padx=5)
    mbreak1Button.pack(side='left', padx=5)
    mlesson2Button.pack(side='left', padx=5)
    mlesson3Button.pack(side='left', padx=5)

    mexplain1 = tk.Label(mframe1, text='0830-1000', height=lessonHeight).pack(side='right')
    mexplain2 = tk.Label(mframe2, text='1000-1045', height=breakHeight).pack(side='right')
    mexplain3 = tk.Label(mframe3, text='1045-1115', height=breakHeight).pack(side='right')
    mexplain4 = tk.Label(mframe4, text='1115-1245', height=lessonHeight).pack(side='right')
    mexplain5 = tk.Label(mframe5, text='1250-1420', height=lessonHeight).pack(side='right')

    # adding a calendar to choose the day
    if preexistingData != None and preexistingData['date'] != None and preexistingData['date'] != ' ': 
        structDate = time.strptime(preexistingData['date'], '%d/%m/%y')
        cal = tkcalendar.Calendar(leftSelectionFrame, selectmode = 'day', 
            year = structDate.tm_year, month = structDate.tm_mon,
            day = structDate.tm_mday,
            mindate = datetime.date(1969, 1, 1), maxdate = datetime.date(2068, 12, 31))
    else:
        current = time.localtime()
        cal = tkcalendar.Calendar(leftSelectionFrame, selectmode = 'day', 
            year = current.tm_year, month = current.tm_mon,
            day = current.tm_mday,
            mindate = datetime.date(1969, 1, 1), maxdate = datetime.date(2068, 12, 31))

    cal.pack(pady = 20)

    # this code is exactly the same as the code in main.py, for more comments/explanation please view that file
    def hourValidateFunction(newValue):
        try:
            int_newValue = int(newValue)
        except ValueError:
            return False
        
        if int_newValue < 0 or int_newValue > 23:
            return False

        return True

    def hourInvalidFunction(newValue, start=False):
        try:
            int_newValue = int(newValue)
            replaceValue = max(min(23, int_newValue), 0)
            replaceValue = f'{replaceValue:02}'
        except ValueError:
            replaceValue = '00'

        if start == True:
            EndSelectHour.delete(0, tk.END)
            EndSelectHour.insert(0, replaceValue)
        else:  
            StartSelectHour.delete(0, tk.END)
            StartSelectHour.insert(0, replaceValue)

    def minuteInvalidFunction(newValue, start=False):
        try:
            int_newValue = int(newValue)
            replaceValue = max(min(59, int_newValue), 0)
            replaceValue = f'{replaceValue:02}'
        except ValueError:
            replaceValue = '00'

        if start == True:
            EndSelectHour.delete(0, tk.END)
            EndSelectHour.insert(0, replaceValue)
        else:  
            StartSelectHour.delete(0, tk.END)
            StartSelectHour.insert(0, replaceValue)

    def minuteValidateFunction(newValue):
        try:
            int_newValue = int(newValue)
        except ValueError:
            return False

        if int_newValue < 0 or int_newValue > 59:
            return False
        
        return True

    leftLabel = tk.Label(leftMultiFrame, text='Start time & date')
    rightLabel = tk.Label(rightMultiFrame, text='End time & date')

    leftLabel.pack(padx=20)
    rightLabel.pack(padx=20)

    # LEFT & START

    # bad variable naming conventions because it had to be refactored when i realised i'd need to duplicate this code too
    # it needs to exist on the left side, so that the entry date and time can be picked
    # and everything similar (but of course hooked up to different variable names) needs to exist on the right, to pick the leave end date and time
    StartCurrentHour = tk.StringVar(window, value='00')
    if preexistingData != None and preexistingData['hour'] != None and preexistingData['hour'] != ' ': 
        StartCurrentHour.set(preexistingData['hour'])
    StartCurrentMinute = tk.StringVar(window, value='00')
    if preexistingData != None and preexistingData['minute'] != None and preexistingData['minute'] != ' ': 
        StartCurrentMinute.set(preexistingData['minute'])

    StartSelectionDiv = tk.Frame(leftMultiFrame)
    StartSelectionDiv.pack()

    StartSelectHour = tk.Spinbox(StartSelectionDiv, textvariable=StartCurrentHour, from_=0, to=23, validate='focus', 
                            validatecommand=(window.register(hourValidateFunction), '%P'), invalidcommand=(window.register(hourInvalidFunction), '%P'),
                            format='%02.0f', width=3)

    StartSelectHour.grid(column=0, row=0)
    StartHourExplain = tk.Label(StartSelectionDiv, text='Hour', font=('Sarabun', 9, 'italic'))
    StartHourExplain.grid(column=0, row=1)

    StartDivider = tk.Label(StartSelectionDiv, text=':')
    StartDivider.grid(column=1, row=0)

    StartSelectMin = tk.Spinbox(StartSelectionDiv, textvariable=StartCurrentMinute, from_=0, to=59, validate='focus', 
                        validatecommand=(window.register(minuteValidateFunction), '%P'), invalidcommand=(window.register(minuteInvalidFunction), '%P'),
                        format='%02.0f', width=3)
    StartSelectMin.grid(column=2, row=0)
    StartMinExplain = tk.Label(StartSelectionDiv, text='Minute', font=('Sarabun', 9, 'italic'))
    StartMinExplain.grid(column=2, row=1)

    if preexistingData != None and preexistingData['date'] != None and preexistingData['date'] != ' ': 
        structDate = time.strptime(preexistingData['date'], '%d/%m/%y')
        StartDateEntry = tkcalendar.DateEntry(leftMultiFrame, selectmode = 'day', date_pattern = "dd/MM/yyyy",
            year = structDate.tm_year, month = structDate.tm_mon,
            day = structDate.tm_mday,
            mindate = datetime.date(1969, 1, 1), maxdate = datetime.date(2068, 12, 31))
    else:
        current = time.localtime()
        StartDateEntry = tkcalendar.DateEntry(leftMultiFrame, selectmode = 'day', date_pattern = "dd/MM/yyyy",
            year = current.tm_year, month = current.tm_mon,
            day = current.tm_mday,
            mindate = datetime.date(1969, 1, 1), maxdate = datetime.date(2068, 12, 31))

    StartDateEntry.pack(pady = 5)

    ## RIGHT & END

    EndCurrentHour = tk.StringVar(window, value='00')
    if preexistingData != None and preexistingData['hour'] != None and preexistingData['hour'] != ' ': 
        EndCurrentHour.set(preexistingData['hour'])
    EndCurrentMinute = tk.StringVar(window, value='00')
    if preexistingData != None and preexistingData['minute'] != None and preexistingData['minute'] != ' ': 
        EndCurrentMinute.set(preexistingData['minute'])

    EndSelectionDiv = tk.Frame(rightMultiFrame)
    EndSelectionDiv.pack()

    EndSelectHour = tk.Spinbox(EndSelectionDiv, textvariable=EndCurrentHour, from_=0, to=23, validate='focus', 
                            validatecommand=(window.register(hourValidateFunction), '%P'), invalidcommand=(window.register(hourInvalidFunction), '%P'),
                            format='%02.0f', width=3)

    EndSelectHour.grid(column=0, row=0)
    EndHourExplain = tk.Label(EndSelectionDiv, text='Hour', font=('Sarabun', 9, 'italic'))
    EndHourExplain.grid(column=0, row=1)

    EndDivider = tk.Label(EndSelectionDiv, text=':')
    EndDivider.grid(column=1, row=0)

    EndSelectMin = tk.Spinbox(EndSelectionDiv, textvariable=EndCurrentMinute, from_=0, to=59, validate='focus', 
                        validatecommand=(window.register(minuteValidateFunction), '%P'), invalidcommand=(window.register(minuteInvalidFunction), '%P'),
                        format='%02.0f', width=3)
    EndSelectMin.grid(column=2, row=0)
    EndMinExplain = tk.Label(EndSelectionDiv, text='Minute', font=('Sarabun', 9, 'italic'))
    EndMinExplain.grid(column=2, row=1)

    if preexistingData != None and preexistingData['date'] != None and preexistingData['date'] != ' ': 
        structDate = time.strptime(preexistingData['date'], '%d/%m/%y')
        EndDateEntry = tkcalendar.DateEntry(rightMultiFrame, selectmode = 'day', date_pattern = "dd/MM/yyyy",
            year = structDate.tm_year, month = structDate.tm_mon,
            day = structDate.tm_mday,
            mindate = datetime.date(1969, 1, 1), maxdate = datetime.date(2068, 12, 31))
    else:
        current = time.localtime()
        EndDateEntry = tkcalendar.DateEntry(rightMultiFrame, selectmode = 'day', date_pattern = "dd/MM/yyyy",
            year = current.tm_year, month = current.tm_mon,
            day = current.tm_mday,
            mindate = datetime.date(1969, 1, 1), maxdate = datetime.date(2068, 12, 31))

    EndDateEntry.pack(pady = 5)

    # didn't get around to making the submit function work, because this code was abandon before this stage was reached
    # def submitFunc():
    #     returnDate = cal.get_date().replace('/', '-')
    #     returnDate = time.strptime(returnDate, '%m-%d-%y')

    #     try:
    #         formattedTime = time.strptime(f'{returnDate.tm_year}-{returnDate.tm_mon}-{returnDate.tm_mday} {currentHour.get()}:{currentMinute.get()}', '%Y-%m-%d %H:%M')
    #     except ValueError:
    #         messagebox.showwarning('An error occured', 'Please check your time value.')
    #         return

    #     strv_edit.set(time.strftime('%d/%m/%y %H:%M', formattedTime))

    #     window.destroy()

    submitButton = tk.Button(window, text='Submit')#, command=submitFunc)
    submitButton.pack(side='bottom', pady=(0, 20))

# just a simple little mainWindow to mimic whatever other window would be used in the main.py
mainWindow = tk.Tk()
mainWindow.geometry('600x200')

# again, mimicking main.py
strv_a = tk.StringVar(mainWindow, 'variable to be changed')
tk.Label(mainWindow, textvariable=strv_a).pack()

quit_button = tk.Button(mainWindow, text='QUIT BUTTON', command=lambda: quit()).pack()

open_date_select(strv_a)

mainWindow.mainloop()