import pygame, time, random
from pygame.locals import *
import pandas as pd
import json
from datetime import datetime, timedelta
import threading, time

""" Settings """
EXCEL_FILE = "exams.xlsx"
WORKSHEET = "exams"

""" Read excel file into json data """
def get_excel_data(xlsx_filename, worksheet):
    xl = pd.read_excel(xlsx_filename, sheet_name=worksheet, index_col=None, na_values=["NA"])
    data = []
    for rowid, row in sorted(xl.iterrows()):
        record = {}
        for k,v in row.items():
            k = k.lower()
            record[k] = v
        data.append(record)
    return(data)

def get_session_list(exams):
    res = []
    for exam in exams:
        if exam["session_id"] not in res:
            res.append(exam["session_id"])
    return res

""" Initialise clock """
seconds_elapsed = 0
clock_running = False
quit = False

def clock_tick():
    global seconds_elapsed
    if clock_running:
        seconds_elapsed += 1
    if not quit:
        threading.Timer(1, clock_tick).start()
    pass
ticker = threading.Timer(1, clock_tick).start()

""" Initialise Pygame """
pygame.init()

""" Pygame Constants """
BACKGROUND = (0x00, 0x00, 0x00)
BACKGROUND_ROW = (0x33, 0x33, 0x33)
FOREGROUND_PRIMARY = (0xC0, 0xC0, 0xA0)
FOREGROUND_SECONDARY = (0xF0, 0xF0, 0xF0)
HIGHLIGHT = (0x40, 0x40, 0x40)
PAUSED = (0xA0, 0x00, 0x00)
HELP_COLOUR = (0x00, 0x00, 0xA0)
TEXT1 = pygame.font.SysFont("Arial", 64)
TEXT2 = pygame.font.SysFont("Arial", 36)
TEXT3 = pygame.font.SysFont("Arial", 24)
TEXT_MEGA = pygame.font.SysFont("Arial", 72)
CLOCK = pygame.font.SysFont("Consolas", 64)
WARNING1 = (0xD8, 0x61, 0x06)
WARNING2 = (0xF4, 0x41, 0x41)

window = pygame.display.set_mode((1280, 720), pygame.FULLSCREEN)
#window = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
pygame_width, pygame_height = pygame.display.get_surface().get_size()
fps = pygame.time.Clock()
exams = get_excel_data(EXCEL_FILE, WORKSHEET)
session_list = get_session_list(exams)
session_id = None
pos = (0,0)                                                                      ### HERE
click = (0,0)                                                                    ### HERE
show_instructions = False
while not quit:
    window.fill(BACKGROUND)
    for event in pygame.event.get():
        if event.type == QUIT:
            quit = True
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                show_instructions = not show_instructions
            if event.key == K_x and show_instructions:
                quit = True
            if event.key == K_1 and session_id is not None:
                seconds_elapsed -= 60
            if event.key == K_2 and session_id is not None:
                seconds_elapsed += 60
            if event.key == K_SPACE and session_id is not None:
                clock_running = not clock_running
            if event.key == K_l:
                BACKGROUND = (0xFF, 0xFF, 0xFF)
                BACKGROUND_ROW = (0xDD, 0xDD, 0xDD)
                FOREGROUND_PRIMARY = (0x00, 0x00, 0x00)
                FOREGROUND_SECONDARY = (0x21, 0x21, 0x21)
                HIGHLIGHT = (0xB0, 0xB0, 0xB0)
            if event.key == K_d:
                BACKGROUND = (0x00, 0x00, 0x00)
                BACKGROUND_ROW = (0x33, 0x33, 0x33)
                FOREGROUND_PRIMARY = (0xC0, 0xC0, 0xA0)
                FOREGROUND_SECONDARY = (0xF0, 0xF0, 0xF0)
                HIGHLIGHT = (0x40, 0x40, 0x40)
        elif event.type == MOUSEMOTION:                                             ### HERE
            pos = event.pos                                                          ### HERE
        elif event.type == MOUSEBUTTONDOWN:                                          ### HERE
            if session_id is None:
                click = event.pos                                                    ### HERE
            else:
                clock_running = not clock_running

    if session_id is None:  # no session selected yet
        # Display all sessions
        window.blit(TEXT2.render("Select session:", 1, FOREGROUND_PRIMARY), (20, 20))
        for i in range(len(session_list)):                                           ### HERE
            y = 60+50*i                                                              ### HERE
            h = 50                                                                   ### HERE
            if pos[1] > y and pos[1] < (y+h):                                        ### HERE
                pygame.draw.rect(window, HIGHLIGHT, (0,y,pygame_width,h))           ### HERE
            if click[1] > y and click[1] < (y+h):
                session_id = session_list[i]
                click = (0,0)
            window.blit(TEXT2.render(session_list[i], 1, FOREGROUND_SECONDARY), (20, y))         ### HERE

    else: # display session exam information:
        now = datetime.now()
        window.blit(TEXT1.render(now.strftime("%A, %d %B, %Y"), 1, FOREGROUND_PRIMARY), (10, 10))
        if now.second % 2 == 0:
            window.blit(CLOCK.render(now.strftime("%H %M"), 1, FOREGROUND_PRIMARY), (pygame_width-200, 10))
        else:
            window.blit(CLOCK.render(now.strftime("%H:%M"), 1, FOREGROUND_PRIMARY), (pygame_width-200, 10))
        window.blit(TEXT3.render("EXAM", 1, FOREGROUND_SECONDARY), (10, 110))
        window.blit(TEXT3.render("REMAINING", 1, FOREGROUND_SECONDARY), (pygame_width-450, 110))
        window.blit(TEXT3.render("FINISH AT", 1, FOREGROUND_SECONDARY), (pygame_width-200, 110))
        i = 0
        for exam in exams:
            if exam["session_id"] == session_id:
                if "seconds_duration" not in exam:
                    exam["seconds_duration"] = int(exam["minutes"]*60)
                y = 150+70*i

                # Display exam label
                window.blit(TEXT1.render(exam["exam_label"], 1, FOREGROUND_SECONDARY), (10, y))

                # Calculate and display remaining time
                seconds_remaining = exam["seconds_duration"] - seconds_elapsed
                h = seconds_remaining // 3600
                m = (seconds_remaining % 3600) // 60
                time_remaining = f"{h:02}:{m:02}"
                if clock_running and now.second % 2 == 0: # pulse between "hh:mm" and "hh mm"
                    time_remaining = f"{h:02} {m:02}"
                if seconds_remaining < (5*60): # 5 minute warning
                    pygame.draw.rect(window, WARNING2, (pygame_width-310,y-10,150,60))
                elif seconds_remaining < (30*60): # 30 minute warning
                    pygame.draw.rect(window, WARNING1, (pygame_width-310,y-10,150,60))
                if seconds_remaining < 60:
                    if now.second % 2 == 0:
                        time_remaining = f"   {seconds_remaining:02}"
                    else:
                        time_remaining = f"  .{seconds_remaining:02}"
                if seconds_remaining < 0:
                    time_remaining = "stop"
                window.blit(CLOCK.render(time_remaining, 1, FOREGROUND_SECONDARY), (pygame_width-450, y))

                # Calculate and display estimated finish time
                finish = now + timedelta(seconds=seconds_remaining)
                window.blit(CLOCK.render(finish.strftime("%H:%M"), 1, FOREGROUND_SECONDARY), (pygame_width-200, y))

                if not clock_running:
                    s = pygame.Surface((pygame_width - 400, pygame_height - 400))
                    s.set_alpha(128)
                    s.fill(PAUSED)
                    window.blit(s, (200, 200))
                    window.blit(TEXT_MEGA.render("PAUSED", 1, FOREGROUND_PRIMARY), (500, 320))
                    window.blit(TEXT3.render("Press SPACE to RESUME", 1, FOREGROUND_PRIMARY), (500, 460))
                    window.blit(TEXT3.render("Press ESC for HELP", 1, FOREGROUND_PRIMARY), (500, 490))
                i += 1
            # end: if exam["session_id"] == session_id:
        # end: for exam in exams
    if show_instructions:
        s = pygame.Surface((pygame_width - 400, pygame_height - 400))
        s.fill(HELP_COLOUR)
        window.blit(s, (200, 200))
        window.blit(TEXT1.render("INSTRUCTIONS", 1, FOREGROUND_PRIMARY), (210, 210))
        window.blit(TEXT3.render("Press SPACE to PAUSE / RESUME countdown", 1, FOREGROUND_PRIMARY), (210, 290))
        window.blit(TEXT3.render("Press ESC again to close instructions", 1, FOREGROUND_PRIMARY), (210, 320))
        window.blit(TEXT3.render("Press 1 to add a minute to time remaining", 1, FOREGROUND_PRIMARY), (210, 325))
        window.blit(TEXT3.render("Press 2 to subtract a minute from time remaining", 1, FOREGROUND_PRIMARY), (210, 380))
        window.blit(TEXT3.render("Press L or D to switch between light and dark color modes", 1, FOREGROUND_PRIMARY), (210, 410))
        window.blit(TEXT3.render("Press X now (from instruction screen) to exit", 1, FOREGROUND_PRIMARY), (210, 440))

    pygame.display.update() # Actually does the screen update
    fps.tick(25) # Run the game at 25 frames per second
pygame.quit()

