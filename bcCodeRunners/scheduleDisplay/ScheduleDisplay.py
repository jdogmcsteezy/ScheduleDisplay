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
        self.todaysClasses = []
        self.todaysTimeSlots = []
        self.timeSlotFont = (path.join(self.fonts_path,'OpenSans-CondBold.ttf') , 21)
        self.scheduleDisplay_numberOfClasses = 20 + 2
        self.classSurface_classCodeFont = (path.join(self.fonts_path,'OpenSans-Bold.ttf') , 21)
        self.classSurface_classCodeLeftBuffer = 25
        self.classSurface_classTitleFont = (path.join(self.fonts_path,'OpenSans-Regular.ttf') , 20)
        self.classSurface_widthBuffer = 10
        self.classSurface_dimensions = (width - (self.classSurface_widthBuffer * 2), height / self.scheduleDisplay_numberOfClasses)
        self.classSurface_bgColors = ((242,242,242), (255,255,255))
        self.classSurface_roomNumberFont = (path.join(self.fonts_path,'OpenSans-CondBold.ttf'), 45)
        self.classSurface_floorSurface_widthRatio = .15
        self.classSurface_floorSurface_buffer = (0 , 0)
        self.classSurface_floorSurface_dimensions = (int(self.classSurface_dimensions[0] * self.classSurface_floorSurface_widthRatio), int(self.classSurface_dimensions[1]  - (2 * self.classSurface_floorSurface_buffer[1])))
        self.classesSurface = None

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
                if DoesClassMeet('M', meeting, 'LEC'): # <<<< """''Artificially''""" made to "F" for testing, replace with daysOfWeek[today]
                    self.todaysClasses.append(meeting)
        self.todaysClasses = sorted(self.todaysClasses, key=lambda k: k['LEC']['Start']) 

    def LoadTodaysTimeSlots(self):
        today = datetime.datetime.today().weekday()
        daysOfWeek = ['M', 'T', 'W', 'Th', 'F', 'Sat', 'S']
        self.todaysTimeSlots = []
        for meeting in self.todaysClasses:
            nextTimeSlot = ConvertMilitaryToStd(meeting['LEC']['Start'])
            if not self.todaysTimeSlots or self.todaysTimeSlots[-1] != nextTimeSlot:
                self.todaysTimeSlots.append(nextTimeSlot)

    def GetNextTimeSlotClasses(self):
        nextTimeSlotClasses = []
        assert self.todaysTimeSlots, 'TodaysTimeSlots is empty, maybe call LoadTodaysTimeSlots()'
        for meeting in list(self.todaysClasses):
            if ConvertMilitaryToStd(meeting['LEC']['Start']) == self.todaysTimeSlots[0]:
                nextTimeSlotClasses.append(meeting)
                self.todaysClasses.pop(0)
            else:
                break
        self.todaysTimeSlots.pop(0)
        sorted(nextTimeSlotClasses, key=lambda k: k['LEC']['Room'])
        return nextTimeSlotClasses

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

    def CreateClassesSurface(self, classes):
        if classes:
            self.classesSurface = Surface((self.width, self.height))
            self.classesSurface.fill((255,255,255))
            timeSurfaceText = ConvertMilitaryToStd(classes[0]['LEC']['Start'])
            timeSurfaceFont = font.Font(*self.timeSlotFont)
            timeSurface = timeSurfaceFont.render(timeSurfaceText, True, (51,51,51))
            self.classesSurface.blit(timeSurface, (self.classSurface_widthBuffer, 0))
            for i, meeting in enumerate(classes):
                nextClass = self.CreateClassSurface(meeting, self.classSurface_bgColors[i % 2])
                self.classesSurface.blit(nextClass,(self.classSurface_widthBuffer, timeSurface.get_rect().height + nextClass.get_rect().height * i))
            self.classesSurface.convert_alpha()
        return self.classesSurface


