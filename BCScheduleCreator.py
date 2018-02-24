import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from contextlib import contextmanager
from bs4 import BeautifulSoup
import re
import sys
import json

Subjects_dir = 'Subjects_Schedules'
Subjects = ['AB - Agriculture Business', 'ACCT - Accounting', 'AET - Agricultural Engineering Tech', 'AGR - Agriculture', 'AGS - Agricultural Science', 'AJ - Administration of Justice', 'AJLE - AJ Law Enforcement', 'ALH - Allied Health', 'ANTH - Anthropology', 'ART - Art', 'ASL - American Sign Language', 'AUT - Automotive Technology', 'BCIS - Business Computer Information', 'BIOL - Biological Sciences', 'BUS - Business', 'CDF - Child Development & Family Rel', 'CHEM - Chemistry', 'CHIN - Chinese', 'CLP - Career Life Planning', 'CMST - Communication Studies', 'COS - Cosmetology', 'CSCI - Computer Science', 'CSL - Counseling', 'DFT - Drafting', 'DRAM - Drama', 'DSPS - Disabled Student Programs/Serv', 'ECON - Economics', 'EDUC - Education', 'EH - Environmental Horticulture', 'EMS - Emergency Medical Services', 'ENGL - English', 'ENGR - Engineering', 'ESL - English as a Second Language', 'FASH - Fashion', 'FN - Foods & Nutrition', 'FREN - French', 'FSC - Fire Science', 'GEOG - Geography', 'GEOL - Geology', 'GERM - German', 'HIM - Health Information Management', 'HIST - History', 'HLTH - Health', 'HON - Honors', 'HUM - Humanities', 'IDST - Interdisciplinary Studies', 'ITAL - Italian', 'JOUR - Journalism', 'JPN - Japanese', 'KIN - Kinesiology', 'LATN - Latin', 'LEAD - Language Education/Development', 'LIS - Library & Information Science', 'LM - Life Management', 'MATH - Mathematics', 'MCS - Multicultural Studies', 'MSP - MultiMedia Studies Program', 'MUS - Music', 'NR - Natural Resources', 'NSG - Nursing', 'OLS - Occupational & Life Skills', 'PE - Physical Education', 'PHIL - Philosophy', 'PHO - Photography', 'PHYS - Physics', 'POS - Political Science', 'PSC - Physical Science', 'PSY - Psychology', 'READ - Reading', 'RLS - Real Estate', 'RT - Respiratory Care', 'RTVF - Radio/TV/Film', 'SOC - Sociology', 'SPAN - Spanish', 'SPE - Special Education', 'WKE - Work Experience', 'WLD - Welding']

# Selenium web driver wrapped in a context manager to ensure the browser closes.
# The browser runs -headless, meaning no screen appears.
@contextmanager
def Web_Driver():
    try:
        options = Options()
        options.add_argument('-headless')
        driver = webdriver.Firefox(firefox_options=options)
        yield driver
    except WebDriverException: 
        raise TimeoutError("Selenium webdriver times out.")
    driver.quit()

# Used to do the work of using a firefox web browser to fill Butte College class search forms.
# All paramaters are filled the same as the actual web form at 'http://searchclasses.butte.edu/'.
# If None is input into the Subject paramater web browser will attempt to get all info from all
# departments which may timeout.
def GrabClassData(Term, Location, Subject):
    with Web_Driver() as Driver:
        Driver.get('http://searchclasses.butte.edu/')
        selection = Select(Driver.find_element_by_id('InputTermId'))
        selection.select_by_visible_text(Term)
        selection = Select(Driver.find_element_by_id('InputLocationId'))
        selection.select_by_visible_text(Location)
        if Subject is not None:
            selection = Select(Driver.find_element_by_id('InputSubjectId'))
            selection.select_by_visible_text(Subject)
        Driver.find_element_by_id('searchButton').click()
        WebDriverWait(Driver, 60).until(EC.presence_of_element_located((By.ID, 'resultsBoiler')))
        tableData = Driver.page_source
        return tableData

# NOT REALLY USED FOR PROJECT
# Just saves the Data paramater as html file. 
# Subject field is used to name the file.
def SaveDataToHTML(Subject, Data):
    # Grab the acronymn for the subject
    pattern = re.compile(r'[A-Z]+\b')
    fileName = pattern.search(Subject).group()
    # Create file name
    filePath = os.path.join(Subjects_dir, fileName + '_Schedule.html')
    # Create directory if it does not exist
    if not os.path.exists(Subjects_dir):
        os.makedirs(Subjects_dir)
    with open(filePath, 'w') as file:
        file.write(Data)


# This function is mostly for TESTING.
# It takes in a dictionary containing class info and 
# prints it in a nice format.
# Normally used in conjuction with the CreateClassList()
# function which returns a list of dictionaries.
def PrintClass(classDict):
    print('Name: ', classDict['Title'])
    print('Instructor: ', classDict['Instructor'])
    print('LEC: ', classDict['LEC'])
    print('LAB: ', classDict['LAB'])


# Used to quickly clean off unnecessary characters (\n, \, *, whitespace) from scraped text.
def CleanText(string):
    string = string.replace(r'\n', '')
    string = string.replace('\'', '')
    string = string.replace(',', '')
    string = string.replace('*', '')
    string = string.replace('  ', '')
    return string.strip()

# Used to convert standard time to military time, this makes it easier to compare times.
# Parse schedule stores class Start and End times in military.
def ConvertStdToMilitary(time12):
    hour24 = 0
    min24 = 0 
    if 'PM' in time12:
        hour24 += 12
    hourPattern = re.compile(r'\d{1,2}:')
    minPattern = re.compile(r':\d\d')
    hourMatch = hourPattern.search(time12)
    minMatch = minPattern.search(time12)
    hour24 += int(hourMatch.group()[:-1]) if int(hourMatch.group()[:-1]) != 12 else 0
    min24 += int(minMatch.group()[1:])
    return '{}:{}'.format(hour24 if hour24 > 9 else ('0' + str(hour24)), min24 if min24 > 9 else ('0' + str(min24)))

 # Used to convert military time to standard time. So that info can be displayed for us humans.
 # Parse schedule stores class Start and End times in military.
def ConvertMilitaryToStd(time24):
    hour12 = 0
    min12 = 0 
    hourPattern = re.compile(r'\d{1,2}:')
    minPattern = re.compile(r':\d\d')
    hourMatch = hourPattern.search(time24)
    minMatch = minPattern.search(time24)
    hour12 += int(hourMatch.group()[:-1])
    min12 += int(minMatch.group()[1:])
    timeOfDay = ''
    if hour12 >= 12:
        timeOfDay = 'PM'
        if hour12 > 12:
            hour12 -= 12
    else:
        timeOfDay = 'AM'
    
    
    return '{}:{} {}'.format(hour12, min12 if min12 > 9 else ('0' + str(min12)), timeOfDay)

def ParseSchedule(classes):
    schedule = {}
    schedule['LEC'] = None
    schedule['LAB'] = None
    # Iterate through each type of class LEC or LAB
    for classType in classes:
        # To store Building, Days, Room, and start/stop time.
        meeting = {}
        # Find if it is LEC or LAB
        pattern = re.compile(r'(LEC|LAB)')
        match = pattern.search(classType)
        # If LEC or LAB is not found then skip over class because it does not concern project.
        if match is None:
            continue
        type_ = match.group()
        # Find which building
        pattern = re.compile(r'^\w{2,5}')
        match = pattern.search(classType)
        meeting['Building'] = match.group()
        # Find which room
        pattern = re.compile(r'\s\d{3}\s')
        match = pattern.search(classType)
        meeting['Room'] = match.group().strip()
        # Find which days
        pattern = re.compile(r'\s[MTWHhF]{1,6}\s')
        match = pattern.search(classType)
        # Check if the class even has official meeting times
        if match is not None:
            meeting['Days'] = match.group().strip()
        else:
            meeting['Days'] = None
        # Find start and stop times
        pattern = re.compile(r'\s\d{1,2}:\d{2}\s(AM|PM)')
        # Save those time to a list
        matches = [match for match in pattern.finditer(classType)]
        times = ['Start','End']
        for match,time in zip(matches, times):
            meeting[time] = ConvertStdToMilitary(match.group().strip())
        # Add the dic to a schedule
        schedule[type_] = meeting
    # Return schedule dict.
    return schedule

def ParseSemesterDates(data):
    soup = BeautifulSoup(data, 'lxml')
    # Grab every table row inside a <body> 
    body = soup.find('body')
    # Look for the date pattern
    datePattern = re.compile(r'\d{1,2}/\d{1,2}/\d{4} - \d{1,2}/\d{1,2}/\d{4}')
    dateMatch = datePattern.search(body.text)
    dateTuple = tuple(dateMatch.group().split(' - '))
    return (dateTuple)

# Takes the files saved by GrabClassData and parses them into a dict.
# At this point this function needs a building specified based on how it parses
# the <div> that contains class info. A later improvment will be using regex to be 
# able to compile classes from any building into one dict.
def ParseHTMLtoJSON(data, classes, building):
    soup = BeautifulSoup(data, 'lxml')
    # Grab every table row inside a <bodyt> 
    rows = soup.find('tbody').findAll('tr')
    for row in rows:
        classInfo = {}
        LocationTime = []
        # Traverse <td>'s within <tr>
        for td in row.findAll('td', 'col-md-4'):
            for div in td.findAll('div', limit=2):
                text = div.text
                if building in text:
                    LocationTime.append(CleanText(text))
        if not LocationTime:
            continue 
        # Parse the div that holds LEC, LAB, Start, End, Days, Building, Room.
        schedule = ParseSchedule(LocationTime)
        # Merge the returned scheule
        classInfo = {**classInfo, **schedule}
        td = row.find('td', 'col-md-2')
        pattern = re.compile(r'[A-Z]\w{1,3}-\d+')
        department_num = pattern.search(td.text).group()
        pattern = re.compile(r'[A-Z]\d{4}\s.+')
        name = pattern.search(td.text).group()
        name = CleanText(name)[6:]
        classInfo['Title'] = department_num + ' ' + name
        for td in row.findAll('a',href=True):
            if 'http://www.butte.edu/district_info/directory' in td['href']:
                classInfo['Instructor'] = CleanText(td.text)
        if 'Instructor' not in classInfo.keys():
            classInfo['Instructor'] = None
        classes.append(classInfo)
    return classes

# Just checks to see if the depatment can be found.
# Data should be an HTML string.
# Buillding should be a string of department. ex: 'MC'
def IsDepartmentInBuilding(data, building):
    inBuilding = False
    soup = BeautifulSoup(data, 'lxml')
    tbody = soup.find('tbody')
    if not tbody:
        return False
    rows = tbody.findAll('tr')
    for row in rows:
        for td in row.findAll('td', 'col-md-4'):
            for div in td.findAll('div', limit=2):
                text = div.text
                if building in text:
                    inBuilding = True
    return inBuilding

# Goes to webpage and fills out forms for all subjects
# then checks whether the subject has any classes in the 'building' paramater.
# Saves every relevant subject to a txt file named subjectsIn_building.txt.
def CompileSubjectsInBuilding(building, semester, location, fileName):
    with open(fileName, 'w') as file:
        with Web_Driver() as driver:
            for subject in Subjects:
                data = GrabClassData(semester, location, subject)
                if IsDepartmentInBuilding(data, building):
                    print(subject)
                    file.write(subject + '\n')

def GetCurrentTerm():
    with Web_Driver() as Driver:
        currentDate = datetime.now()
        Driver.get('http://searchclasses.butte.edu/')
        selection = Select(Driver.find_element_by_id('InputTermId'))
        semesterOptions = [option.text for option in selection.options]
        for semester in semesterOptions:
            Driver.get('http://searchclasses.butte.edu/')
            selection = Select(Driver.find_element_by_id('InputLocationId'))
            selection.select_by_visible_text('Main Campus')
            selection = Select(Driver.find_element_by_id('InputSubjectId'))
            selection.select_by_visible_text('MATH - Mathematics')
            selection = Select(Driver.find_element_by_id('InputTermId'))
            if str(currentDate.year) in semester:
                selection.select_by_visible_text(semester)
                Driver.find_element_by_id('searchButton').click()
                WebDriverWait(Driver, 60).until(EC.presence_of_element_located((By.ID, 'resultsBoiler')))
                tableData = Driver.page_source
                semesterDateTuple = ParseSemesterDates(tableData)
                startDate = datetime.strptime(semesterDateTuple[0], '%m/%d/%Y')
                endDate = datetime.strptime(semesterDateTuple[1], '%m/%d/%Y')
                if startDate <= currentDate and currentDate <= endDate:
                    semesterDict = {'Term' : semester, 'Start': semesterDateTuple[0], 'End': semesterDateTuple[1]}
                    return semesterDict

        return {'Term' : None, 'Start': None, 'End': None}



def DoesClassMeet(day, meeting, type):
    if meeting[type] is not None:
        if day in meeting[type]['Days']:
            return True
    return False

def CreateClassesList(building, semester, location, fileName):
    classes = []
    with open(fileName) as file:
        subjectsMC = [subject.strip() for subject in file.readlines()]
    for subject in subjectsMC:
        data = GrabClassData(semester, location, subject)
        print(subject)
        ParseHTMLtoJSON(data, classes, building)
    classesSet = []
    for d in classes:
        if d not in classesSet:
            classesSet.append(d)
    return classesSet

def DumpListToJson(classes, fileName):
    with open(fileName,'w') as file:
        json.dump(classes, file)

def LoadJsonToList(fileName):
    with open(fileName) as file:
        data = json.loads(file.read())
        return data

