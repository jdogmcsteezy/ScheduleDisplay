from pygame import Surface, time, font
from BCScheduleCreator import ConvertMilitaryToStd, DoesClassMeet, PrintClass
import os
import datetime
import sys
import json

class ScheduleDisplay(Surface):
    def __init__(self, width, height):
        Surface.__init__(self, (width, height))
        font.init()
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        # Change this when done testing ----
        self.scheduleFile = 'testJSON.json'
        self.width = width
        self.height = height
        self.fill((255,255,255))
        self.todaysClasses = []
        self.firstTimeSlot = ''
        self.firstTimeSlotClasses = []
        self.secondTimeSlot = ''
        self.secondTimeSlotClasses = []

    def Update(self):
        pass

    def LoadTodaysClasses(self):
        self.todaysClasses = []
        today = datetime.datetime.today().weekday()
        daysOfWeek = ['M', 'T', 'W', 'Th', 'F', 'Sat', 'S']
        with open(os.path.join(self.dir_path, self.scheduleFile)) as file:
            data = json.loads(file.read())
        for meeting in data:
                if DoesClassMeet('M', meeting, 'LEC'): # <<<< Artificially made to monday, replace with daysOfWeek[today]
                    self.todaysClasses.append(meeting)
        self.todaysClasses = sorted(self.todaysClasses, key=lambda k: k['LEC']['Start']) 
        for day in self.todaysClasses:
            PrintClass(day)


    def UpdateTimeSlotHeaders(self):
        pass

    def UpdateClassList(self):
        pass

    def CreateClassSurface(self):
        pass

    def GetNextTimeSlot(self):
        pass


