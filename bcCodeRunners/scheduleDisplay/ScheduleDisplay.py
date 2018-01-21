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
    # Should be called as the clock striked midnight.
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

    def UpdateTimeSlotHeaders(self):
        # If nothing is stored is time slot.
        if not self.firstTimeSlot:
            # If the todaysclasses list is not empty
            if self.todaysClasses:
                self.firstTimeSlot = ConvertMilitaryToStd(self.todaysClasses[0]['LEC']['Start'])
                for meeting in self.todaysClasses:
                    if ConvertMilitaryToStd(meeting['LEC']['Start']) != self.firstTimeSlot:
                        self.secondTimeSlot = ConvertMilitaryToStd(meeting['LEC']['Start'])
                        break
            # If todaysclasses list is empty
            else:
                self.firstTimeSlot = 'No Upcoming Classes'
                self.secondTimeSlot = ''
        # If somthing is in first time slot
        elif self.firstTimeSlot:
            # If nothing is in second time slot there is not more time slots for the day
            if not self.secondTimeSlot:
                self.firstTimeSlot = 'No Upcoming Classes'
            # If somthing is in the second time slot move second time slot to first time slot and update second.
            else:
                self.firstTimeSlot = self.secondTimeSlot
                # Make sure todaysclasses list is not empty
                if self.todaysClasses:
                    for meeting in self.todaysClasses:
                        if ConvertMilitaryToStd(meeting['LEC']['Start']) != self.firstTimeSlot:
                            self.secondTimeSlot = ConvertMilitaryToStd(meeting['LEC']['Start'])
                            break
                # This if may not be needed but will ensure that secondtimeslot is empty if there are no new timeslots.
                if self.firstTimeSlot == self.secondTimeSlot:
                    self.secondTimeSlot = ''


        print(self.firstTimeSlot)
        print(self.secondTimeSlot)

            
    def UpdateClassLists(self):
        pass

    def CreateClassSurface(self):
        pass

    def GetNextTimeSlot(self):
        pass


