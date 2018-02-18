from pygame import Surface, time, font, image, transform, SRCALPHA
from BCScheduleCreator import ConvertMilitaryToStd, DoesClassMeet, PrintClass, CreateClassesList, LoadJsonToList, DumpListToJson, CompileSubjectsInBuilding, GetCurrentTerm
from apscheduler.schedulers.background import BackgroundScheduler
from os import path
from datetime import datetime, timedelta
from time import localtime, strptime
import sys
import json
import re

class ScheduleDisplay(Surface):
    def __init__(self, width, height):
        Surface.__init__(self, (width, height))
        # You need this if you intend to display any text
        font.init()
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        # These are the folders we will use for images and fonts
        self.dir_path = path.dirname(path.realpath(__file__))
        self.assets_path = path.join(self.dir_path, 'Assets')
        # notice the 'Fonts' folder is located in the 'Assets'
        self.fonts_path = path.join(self.assets_path, 'Fonts')
        # Change this when done testing ----
        self.location = 'Main Campus'
        self.building = 'MC'
        self.term = 'Spring 2018'
        self.scheduleFile = 'testJSON.json'
        self.compiledSubjectsFile = 'subjectsIn_MC.txt'
        self.width = width
        self.height = height
        self.backgroundImageFile = 'MapBG.png'
        self.backgroundImage = image.load(path.join(self.assets_path, self.backgroundImageFile))
        self.backgroundImage = transform.smoothscale(self.backgroundImage, (self.width, self.height))
        self.backgroundImage.convert_alpha()
        self.timeSlotDisplayBuffer = 5
        self.classesSurfacesAndTimes = []
        self.noMoreClassesFlag = False
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
        self.scheduler.add_job(CompileSubjectsInBuilding,'cron', id='CompileSubjects01', day_of_week='mon-fri', hour=1, args=[self.building, self.term, self.location, path.join(self.dir_path, self.compiledSubjectsFile)])
        self.scheduler.add_job(self.UpdateJson,'cron', id='UpdateJson01', day_of_week='mon-fri', hour=2)
        self.scheduler.add_job(self.LoadTodaysClasses, 'cron', id='LoadTodaysClasses01', day_of_week='mon-fri', hour=2, minute=30)
        self.scheduler.add_job(self.LoadTodaysTimeSlots, 'cron', id='LoadTodaysTimeSlots01', day_of_week='mon-fri', hour=2, minute=35)
        self.InitializeJsonData()
        self.LoadTodaysClasses()
        self.LoadTodaysTimeSlots()
        
        


    def Update(self):
        maxHeight = self.height
        currentTime = datetime.now()
        if self.classesSurfacesAndTimes:
            latestTimeSlot = self.classesSurfacesAndTimes[0][1]
            if latestTimeSlot < currentTime:
                self.classesSurfacesAndTimes.pop(0)
                self.fill((252,252,252))
                self.blit(self.backgroundImage, (0,0))
                for classesSurface in self.classesSurfacesAndTimes[:-1][0]:
                    self.blit(classesSurface, ((self.classSurface_widthBuffer), (self.height - maxHeight)))
                    maxHeight -= classesSurface.get_rect().height
                if self.classesSurfacesAndTimes[0] < maxHeight:
                    self.blit(self.classesSurfacesAndTimes[0], ((self.classSurface_widthBuffer), (self.height - maxHeight)))
                    for i in range(len(self.todaysTimeSlots)):
                        nextClasses = self.GetNextTimeSlotClasses()
                        nextClassesSurface = self.CreateClassesSurface(nextClasses)
                        if nextClassesSurface.get_rect().height > maxHeight:
                            break
                        self.blit(nextClassesSurface, ((self.classSurface_widthBuffer), (self.height - maxHeight)))
                        maxHeight -= nextClassesSurface.get_rect().height

        else:
            if self.todaysClasses:
                self.noMoreClassesFlag = False
                self.fill((252,252,252))
                self.blit(self.backgroundImage, (0,0))
                for i in range(len(self.todaysTimeSlots)):
                    nextClasses = self.GetNextTimeSlotClasses()
                    nextClassesSurface = self.CreateClassesSurface(nextClasses)
                    if nextClassesSurface.get_rect().height > maxHeight:
                        break
                    self.blit(nextClassesSurface, ((self.classSurface_widthBuffer), (self.height - maxHeight)))
                    maxHeight -= nextClassesSurface.get_rect().height
            else:
                if not self.noMoreClassesFlag:
                    self.noMoreClassesFlag = True
                    noClassesSurface = self.CreateClassesSurface([])
                    self.fill((252,252,252))
                    self.blit(self.backgroundImage, (0,0))
                    self.blit(noClassesSurface,(0,0))




        #print(self.todaysTimeSlots[0])

    # Should be called as the clock striked midnight.
    def LoadTodaysClasses(self):
        currentTime = datetime.now()
        self.todaysClasses = []
        # Returns number from 0-6
        today = datetime.today().weekday()
        daysOfWeek = ['M', 'T', 'W', 'Th', 'F', 'Sat', 'S']
        data = LoadJsonToList(path.join(self.dir_path, self.scheduleFile))
        for meeting in data[1:]:
                if DoesClassMeet('M', meeting, 'LEC'): # <<<< """''Artificially''""" made to "T" for testing, replace with daysOfWeek[today]
                    meetingStart = ConvertMilitaryToStd(meeting['LEC']['Start'])
                    timeSlot = datetime.combine(currentTime.date(), datetime.strptime(meetingStart, '%I:%M %p').time())
                    timeSlot = timeSlot + timedelta(minutes=self.timeSlotDisplayBuffer)
                    if timeSlot >= currentTime:
                        self.todaysClasses.append(meeting)
        self.todaysClasses = sorted(self.todaysClasses, key=lambda k: k['LEC']['Start'])
        print(self.todaysClasses)
    # Should be called as the clock striked midnight.
    def LoadTodaysTimeSlots(self):
        today = datetime.today().weekday()
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
        if timeSurfaceText != 'No More Classes Today':
            currentTime = datetime.now()
            timeSlot = datetime.combine(currentTime.date(), datetime.strptime(timeSurfaceText, '%I:%M %p').time())
            timeSlot = timeSlot + timedelta(minutes=self.timeSlotDisplayBuffer)
            self.classesSurfacesAndTimes.append((classesSurface, timeSlot))
        return classesSurface

    def UpdateJson(self):
        currentTermDict = GetCurrentTerm()
        schedulePath = path.join(self.dir_path, self.scheduleFile)
        if currentTermDict['Term']:
            subjectsPath = path.join(self.dir_path, self.compiledSubjectsFile)
            newClassesList = CreateClassesList(self.building, currentTermDict['Term'], self.location, subjectsPath)
            newClassesList.insert(0, currentTermDict)
            if path.isfile(schedulePath) and path.getsize(schedulePath) > 0:
                currentClassesList = LoadJsonToList(schedulePath)
                if newClassesList != currentClassesList:
                    DumpListToJson(newClassesList, schedulePath)
            else:
                open(path.join(self.dir_path, self.scheduleFile), 'w').close()
                DumpListToJson(newClassesList, schedulePath)
        else:
            emptyList = [currentTermDict]
            DumpListToJson(emptyList, self.scheduleFile)


    def InitializeJsonData(self):
        schedulePath = path.join(self.dir_path, self.scheduleFile)
        if not path.isfile(path.join(self.dir_path, self.compiledSubjectsFile)):
            CompileSubjectsInBuilding(self.building, self.term, self.location, path.join(self.dir_path, self.compiledSubjectsFile))
        if path.isfile(schedulePath) and path.getsize(schedulePath) > 0:
            termDict = LoadJsonToList(schedulePath)[0]
            if termDict['Term']:
                currentDate = datetime.now()
                startDate = datetime.strptime(termDict['Start'], '%m/%d/%Y')
                endDate = datetime.strptime(termDict['End'], '%m/%d/%Y')
                if not (startDate <= currentDate and currentDate <= endDate):
                    self.UpdateJson()
            else:
                self.UpdateJson()
        else:
            self.UpdateJson()
