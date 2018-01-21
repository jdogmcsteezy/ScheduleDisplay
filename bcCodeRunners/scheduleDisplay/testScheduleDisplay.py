# ---- TESTING -----
import pygame
from ScheduleDisplay import ScheduleDisplay
from BCScheduleCreator import PrintClass



def main():
    pygame.init()
    clock = pygame.time.Clock()
    testScreen = pygame.display.set_mode((300, 300))
    testScreen.fill((0,0,0))
    schedule = ScheduleDisplay(100,100)
    testScreen.blit(schedule, (0, 0))
    #schedule.LoadTodaysClasses()
    schedule.firstTimeSlot = '8:00 AM'
    #schedule.secondTimeSlot = '8:30 AM'
    print(schedule.todaysClasses)
    schedule.UpdateTimeSlotHeaders()
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
