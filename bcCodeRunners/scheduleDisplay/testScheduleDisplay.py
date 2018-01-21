# ---- TESTING -----
import pygame
from ScheduleDisplay import ScheduleDisplay
from BCScheduleCreator import PrintClass

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
    testScreen = pygame.display.set_mode((300, 300))
    testScreen.fill((0,0,0))
    schedule = ScheduleDisplay(100,100)
    testScreen.blit(schedule, (0, 0))
    schedule.LoadTodaysClasses()
    print(schedule.todaysClasses)
    cycleClasses(schedule)
    cycleClasses(schedule)
    cycleClasses(schedule)
    cycleClasses(schedule)
    cycleClasses(schedule)
    cycleClasses(schedule)
    cycleClasses(schedule)
    cycleClasses(schedule)
    cycleClasses(schedule)
    cycleClasses(schedule)
    cycleClasses(schedule)
    cycleClasses(schedule)

    

    pygame.display.update()
    run = True
    while(run):
        clock.tick(26)
        #testScreen.blit(ScheduleDisplay, (0, 0))
        #pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == ord('q'):
                    run = False
            elif event.type == pygame.QUIT:
                run = False

    pygame.quit()


if __name__ == "__main__":
    main()


