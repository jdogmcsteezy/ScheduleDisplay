# ---- TESTING -----
import pygame
from ScheduleDisplay import ScheduleDisplay
from BCScheduleCreator import PrintClass
from contextlib import contextmanager

def cycleClasses(schedule):
    schedule.UpdateTimeSlotHeaders()
    schedule.UpdateClassLists()
    print('*'*50)
    print(schedule.firstTimeSlot)
    for meeting in schedule.firstTimeSlotClasses:
        PrintClass(meeting)
    print('-'*50)
    print(schedule.secondTimeSlot)
    for meeting in schedule.secondTimeSlotClasses:
        PrintClass(meeting)


def main():
    pygame.init()
    clock = pygame.time.Clock()
    #testScreen = pygame.display.set_mode((600, 730), pygame.NOFRAME)
    schedule = ScheduleDisplay(600,1000)
    schedule.fill((255,255,255))
    schedule.LoadTodaysClasses()
    schedule.LoadTodaysTimeSlots()
    print(schedule.GetNextTimeSlotClasses())
    #testScreen.fill((255,255,255))
    #pygame.display.update()
    #run = True
    # while(run):
    #     testScreen.fill((255,255,255))
    #     schedule.UpdateTimeSlotHeaders()
    #     schedule.UpdateClassLists()
    #     testScreen.blit(schedule.CreateClassesSurface(schedule.firstTimeSlotClasses),(0, 0))
    #     clock.tick(26)
    #     pygame.time.wait(1000)
    #     pygame.display.update()
    #     for event in pygame.event.get():
    #         if event.type == pygame.KEYDOWN:
    #             if event.key == ord('q'):
    #                 run = False
    #         elif event.type == pygame.QUIT:
    #             run = False

    pygame.quit()


if __name__ == "__main__":
    main()


