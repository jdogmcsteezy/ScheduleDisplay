from pygame import Surface, time, font, image, transform, SRCALPHA
from BCScheduleCreator import ConvertMilitaryToStd, DoesClassMeet, PrintClass
from os import path
import datetime
import sys
import json
import re

class ScheduleDisplay(Surface):
    def __init__(self, width, height):
        Surface.__init__(self, (width, height))
        # You need this if you intend to display any text
        font.init()
        # These are the folders we will use for images and fonts
        self.dir_path = path.dirname(path.realpath(__file__))
        self.assets_path = path.join(self.dir_path, 'Assets')
        # notice the 'Fonts' folder is located in the 'Assets'
        self.fonts_path = path.join(self.assets_path, 'Fonts')
        # Change this when done testing ----
        self.scheduleFile = 'testJSON.json'
        self.width = width
        self.height = height
        self.classesSurfaces = []
        self.todaysClasses = []
        self.todaysTimeSlots = []
        self.timeSlotFont = (path.join(self.fonts_path,'OpenSans-CondBold.ttf') , int(height * .03425))
        self.scheduleDisplay_numberOfClasses = 20
        self.classSurface_classCodeFont = (path.join(self.fonts_path,'OpenSans-Bold.ttf') , int(height * .02877))
        self.classSurface_classCodeLeftBuffer = int(width * .0395)
        self.classSurface_classTitleFont = (path.join(self.fonts_path,'OpenSans-Regular.ttf') , int(height * .02740))
        self.classSurface_classTitleLeftBuffer = int(width * .02)
        # These can be removed, then we can just put (int(width/height * 1111)) where ever they end up in the code.
        self.classSurface_widthBuffer = int(width * .0158)
        self.classSurface_heightBuffer = int(height * .00411)
        self.classSurface_bgColors = ((242,242,242), (255,255,255))
        self.classSurface_roomNumberFont = (path.join(self.fonts_path,'OpenSans-CondBold.ttf'), int(height * .04110))
        self.classSurface_floorSurface_widthRatio = .15
        self.classSurface_floorSurface_buffer = (0 , 0)

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
                if DoesClassMeet('T', meeting, 'LEC'): # <<<< """''Artificially''""" made to "T" for testing, replace with daysOfWeek[today]
                    self.todaysClasses.append(meeting)
        self.todaysClasses = sorted(self.todaysClasses, key=lambda k: k['LEC']['Start']) 
    # Should be called as the clock striked midnight.
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
        if self.todaysTimeSlots:
            for meeting in list(self.todaysClasses):
                if ConvertMilitaryToStd(meeting['LEC']['Start']) == self.todaysTimeSlots[0]:
                    nextTimeSlotClasses.append(meeting)
                    self.todaysClasses.pop(0)
                else:
                    break
            self.todaysTimeSlots.pop(0)
        nextTimeSlotClasses = sorted(nextTimeSlotClasses, key=lambda k: k['LEC']['Room'])
        return nextTimeSlotClasses

    def CreateClassSurface(self, meeting, bg, width, height):
        room = meeting['LEC']['Room']
        instructor = meeting['Instructor']
        title = meeting['Title']
        classCodePatter =  re.compile(r'^\w{2,5}-\d{1,3}')
        classCode = classCodePatter.search(title).group()
        title = title.replace(classCode + ' ', '')
        # Chooses which png to load based on number
        roomSurface =  image.load(path.join(self.assets_path, '2ndFloor2.png')) if int(room) < 200 else image.load(path.join(self.assets_path, '1stFloor2.png'))
        roomSurface.convert_alpha()
        floorSurfaceDimensions = (int(width * self.classSurface_floorSurface_widthRatio), int(height  - (2 * self.classSurface_floorSurface_buffer[1])))
        roomSurface = transform.smoothscale(roomSurface, floorSurfaceDimensions)
        roomSurfaceFont = font.Font(*self.classSurface_roomNumberFont)
        roomSurfaceText = roomSurfaceFont.render(room, True, (255,255,255))
        roomSurface.blit(roomSurfaceText, (roomSurface.get_rect().centerx - roomSurfaceText.get_rect().centerx, roomSurface.get_rect().centery - roomSurfaceText.get_rect().centery))
        classCodeFont = font.Font(*self.classSurface_classCodeFont)
        classCodeText = classCodeFont.render(classCode, True, (0,0,0))
        classTitleFont = font.Font(*self.classSurface_classTitleFont)
        classTitleText = classTitleFont.render(title, True, (0,0,0))
        classSurface = Surface((width, height))
        classSurface.fill(bg)
        classSurface.blit(roomSurface,self.classSurface_floorSurface_buffer)
        classSurface.blit(classCodeText, (roomSurface.get_rect().right + self.classSurface_classCodeLeftBuffer, classSurface.get_rect().centery - classCodeText.get_rect().centery))
        classSurface.blit(classTitleText, (roomSurface.get_rect().right + self.classSurface_classCodeLeftBuffer + int(self.width * .18957), classSurface.get_rect().centery - classTitleText.get_rect().centery))
        return classSurface

    def CreateClassesSurface(self, classes):
        if classes:
            timeSurfaceText = ConvertMilitaryToStd(classes[0]['LEC']['Start'])
        else:
            timeSurfaceText = 'No More Classes Today'
        timeSurfaceFont = font.Font(*self.timeSlotFont)
        timeSurface = timeSurfaceFont.render(timeSurfaceText, True, (51,51,51))
        classSurfaceHeight = (self.height - (timeSurface.get_rect().height * 2) - ((self.scheduleDisplay_numberOfClasses - 1) * self.classSurface_heightBuffer)) / self.scheduleDisplay_numberOfClasses
        classesSurfaceHeight = timeSurface.get_rect().height + (len(classes) * (classSurfaceHeight + self.classSurface_heightBuffer))
        classesSurface = Surface((self.width - (self.classSurface_widthBuffer * 2), classesSurfaceHeight), SRCALPHA, 32)
        classesSurface.blit(timeSurface, (self.classSurface_widthBuffer, 0))
        for i, meeting in enumerate(classes):
            nextClass = self.CreateClassSurface(meeting, self.classSurface_bgColors[i % 2], self.width - (2 * self.classSurface_widthBuffer), classSurfaceHeight)
            classesSurface.blit(nextClass,(0, timeSurface.get_rect().height + (nextClass.get_rect().height + self.classSurface_heightBuffer) * i))
        classesSurface.convert_alpha()
        self.classesSurfaces.append(classesSurface)
        return classesSurface


