from pygame import Surface, time, font
import os

class ScheduleDisplay(Surface):
	def __init__(self, width, height):
        Surface.__init__(self, (width, height))
        font.init()
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.width = width
        self.height = height
        self.fill(255,255,255)
        self.todaysClasses = []
        self.firstTimeSlot = ''
        self.firstTimeSlotClasses = []
        self.secondTimeSlot = ''
        self.secondTimeSlotClasses = []

    def Update(self):
    	pass

    def LoadTodaysClasses():
    	pass

    def UpdateTimeSlotHeaders():
    	pass

    def UpdateClassList():
    	pass

    def CreateClassSurface():
    	pass

    def GetNextTimeSlot():


