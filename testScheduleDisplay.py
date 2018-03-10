# ---- TESTING -----
import pygame
from ScheduleDisplay import ScheduleDisplay
from BCScheduleCreator import PrintClass
from contextlib import contextmanager
import os

def main():
    pygame.init()
    clock = pygame.time.Clock()
    testScreen = pygame.display.set_mode((633, 730), pygame.NOFRAME)
    schedule = ScheduleDisplay(633,730)
    schedule.Update()
    pygame.display.update()
    run = True
    print(schedule.term)
    while(run):
        #testScreen.fill((255, 255, 225))
        schedule.Update()
        testScreen.blit(schedule,(0, 0))
        clock.tick(26)
    #     pygame.time.wait(5000)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == ord('q'):
                    run = False
            elif event.type == pygame.QUIT:
                run = False

    pygame.quit()
    os.abort()

if __name__ == "__main__":
    main()


