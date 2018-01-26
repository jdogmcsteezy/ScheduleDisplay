from pygame import Surface, time, font, image, transform
from BCScheduleCreator import ConvertMilitaryToStd, DoesClassMeet, PrintClass
from os import path
import datetime
import sys
import json
import re

class ScheduleDisplay(Surface):
    def __init__(self, width, height):
        Surface.__init__(self, (width, height))
        font.init()
        self.dir_path = path.dirname(path.realpath(__file__))
        self.assets_path = path.join(self.dir_path, 'Assets')
        self.fonts_path = path.join(self.assets_path, 'Fonts')
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
        self.scheduleDisplay_numberOfClasses = 20 + 2
        self.classSurface_classCodeFont = (path.join(self.fonts_path,'OpenSans-Bold.ttf') , 21)
        self.classSurface_classCodeLeftBuffer = 25
        self.classSurface_classTitleFont = (path.join(self.fonts_path,'OpenSans-Regular.ttf') , 20)
        self.classSurface_widthBuffer = 10
        self.classSurface_dimensions = (width - self.classSurface_widthBuffer, height / self.scheduleDisplay_numberOfClasses)
        self.classSurface_bgColor1 = (242,242,242)
        self.classSurface_bgColor2 = (255,255,255)
        self.classSurface_roomNumberFont = (path.join(self.fonts_path,'OpenSans-CondBold.ttf'), 45)
        self.classSurface_floorSurface_widthRatio = .15
        self.classSurface_floorSurface_buffer = (0 , 0)
        self.classSurface_floorSurface_dimensions = (int(self.classSurface_dimensions[0] * self.classSurface_floorSurface_widthRatio), int(self.classSurface_dimensions[1]  - (2 * self.classSurface_floorSurface_buffer[1])))

    def Update(self):
        pass
    # Should be called as the clock striked midnight.
    def LoadTodaysClasses(self):
        self.todaysClasses = []
        # Returns number from 0-6
        today = datetime.datetime.today().weekday()
        daysOfWeek = ['M', 'T', 'W', 'Th', 'F', 'Sat', 'S']
        with open(path.join(self.dir_path, self.scheduleFile)) as file:
            data = json.loads(file.read())
        for meeting in data:
                if DoesClassMeet('Th', meeting, 'LEC'): # <<<< """''Artificially''""" made to "F" for testing, replace with daysOfWeek[today]
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

    def UpdateClassLists(self):
        # If nothing is stored in timeslotclasses.
        if not self.firstTimeSlotClasses:
            for meeting in list(self.todaysClasses):
                if self.firstTimeSlot == ConvertMilitaryToStd(meeting['LEC']['Start']):
                    self.firstTimeSlotClasses.append(meeting)
                    self.todaysClasses.pop(0)
            for meeting in list(self.todaysClasses):
                if self.secondTimeSlot == ConvertMilitaryToStd(meeting['LEC']['Start']):
                    self.secondTimeSlotClasses.append(meeting)
                    self.todaysClasses.pop(0)
        # If somthing is in first time slot
        elif self.firstTimeSlotClasses:
            # If nothing is in second time slot there is not more time slots for the day
            if not self.secondTimeSlotClasses:
                self.firstTimeSlotClasses = []
            # If somthing is in the second time slot move second time slot to first time slot and update second.
            else:
                self.firstTimeSlotClasses = self.secondTimeSlotClasses
                # Make sure todaysclasses list is not empty
                self.secondTimeSlotClasses = []
                for meeting in list(self.todaysClasses):
                    if self.secondTimeSlot == ConvertMilitaryToStd(meeting['LEC']['Start']):
                        self.secondTimeSlotClasses.append(meeting)
                        self.todaysClasses.pop(0)
                # This 'if' may not be needed but will ensure that secondtimeslot is empty if there are no new timeslots.
                if self.firstTimeSlot == self.secondTimeSlot:
                    self.secondTimeSlot = []


    def CreateTimeSlotClassesSurface(self, classes):
        pass



    def CreateClassSurface(self, meeting, bg):
        room = meeting['LEC']['Room']
        instructor = meeting['Instructor']
        title = meeting['Title']
        classCodePatter =  re.compile(r'^\w{2,5}-\d{1,3}')
        classCode = classCodePatter.search(title).group()
        title = title.replace(classCode + ' ', '')
        # Chooses which png to load based on number
        roomSurface =  image.load(path.join(self.assets_path, '2ndFloor2.png')) if int(room) < 200 else image.load(path.join(self.assets_path, '1stFloor2.png'))
        roomSurface.convert_alpha()
        roomSurface = transform.smoothscale(roomSurface, self.classSurface_floorSurface_dimensions)
        roomSurfaceFont = font.Font(*self.classSurface_roomNumberFont) #<<<<<<<<<<<<<<<SYSFONT
        roomSurfaceText = roomSurfaceFont.render(room, True, (255,255,255))
        roomSurface.blit(roomSurfaceText, (roomSurface.get_rect().centerx - roomSurfaceText.get_rect().centerx, roomSurface.get_rect().centery - roomSurfaceText.get_rect().centery))
        classCodeFont = font.Font(*self.classSurface_classCodeFont) #<<<<<<<<<<<<<<<SYSFONT
        classCodeText = classCodeFont.render(classCode, True, (0,0,0))
        classTitleFont = font.Font(*self.classSurface_classTitleFont)
        classTitleText = classTitleFont.render(title, True, (0,0,0))
        classSurface = Surface(self.classSurface_dimensions)
        classSurface.fill(bg)
        classSurface.blit(roomSurface,self.classSurface_floorSurface_buffer)
        classSurface.blit(classCodeText, (roomSurface.get_rect().right + self.classSurface_classCodeLeftBuffer, classSurface.get_rect().centery - classCodeText.get_rect().centery))
        classSurface.blit(classTitleText, ( 225 , classSurface.get_rect().centery - classTitleText.get_rect().centery))
        return classSurface
