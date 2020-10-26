#import
import time
import sys
import tellopy
import pygame
import pygame.display
import pygame.key
import pygame.locals
import pygame.font
import os
import datetime
from subprocess import Popen, PIPE

prev_flight_data = None
video_player = None
video_recorder = None
font = None
wid = None
date_fmt = '%Y-%m-%d_%H%M%S'

def update_hud(hud, drone, flight_data):
    (w,h) = (158,0) # width available on side of screen in 4:3 mode
    blits = []
    for element in hud:
        surface = element.update(drone, flight_data)
        if surface is None:
            continue
        blits += [(surface, (0, h))]
        # w = max(w, surface.get_width())
        h += surface.get_height()
    h += 64  # add some padding
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    overlay.fill((0,0,0)) # remove for mplayer overlay mode
    for blit in blits:
        overlay.blit(*blit)
    pygame.display.get_surface().blit(overlay, (0,0))
    pygame.display.update(overlay.get_rect())

def take_picture(drone, speed):
    if speed == 0:
        return
    drone.take_picture()

def flightDataHandler(event, sender, data):
    global prev_flight_data
    text = str(data)
    if prev_flight_data != text:
        update_hud(hud, sender, data)
        prev_flight_data = text

def videoFrameHandler(event, sender, data):
    global video_player
    global video_recorder
    if video_player is None:
        cmd = [ 'mplayer', '-fps', '35', '-really-quiet' ]
        if wid is not None:
            cmd = cmd + [ '-wid', str(wid) ]
        video_player = Popen(cmd + ['-'], stdin=PIPE)

    try:
        video_player.stdin.write(data)
    except IOError as err:
        status_print(str(err))
        video_player = None

    try:
        if video_recorder:
            video_recorder.stdin.write(data)
    except IOError as err:
        status_print(str(err))
        video_recorder = None

def handleFileReceived(event, sender, data):
    global date_fmt
    # Create a file in ~/Pictures/ to receive image data from the drone.
    path = '%s/Pictures/tello-%s.jpeg' % (
        os.getenv('HOME'),
        datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S'))
    with open(path, 'wb') as fd:
        fd.write(data)
    # status_print('Saved photo to %s' % path)
    print('Saved photo to %s' % path)

controls = {
    # 'w': 'forward',
    # 's': 'backward',
    # 'a': 'left',
    # 'd': 'right',
    # 'space': 'up',
    # 'left shift': 'down',
    # 'right shift': 'down',
    # 'q': 'counter_clockwise',
    # 'e': 'clockwise',
    # # arrow keys for fast turns and altitude adjustments
    # 'left': lambda drone, speed: drone.counter_clockwise(speed*2),
    # 'right': lambda drone, speed: drone.clockwise(speed*2),
    # 'up': lambda drone, speed: drone.up(speed*2),
    # 'down': lambda drone, speed: drone.down(speed*2),
    # 'tab': lambda drone, speed: drone.takeoff(),
    # 'backspace': lambda drone, speed: drone.land(),
    # 'p': palm_land,
    # 'r': toggle_recording,
    # 'z': toggle_zoom,
    'enter': take_picture,
    'return': take_picture,
}

def main():
    pygame.init()
    pygame.display.init()
    pygame.display.set_mode((1280, 720))
    pygame.font.init()

    global font
    font = pygame.font.SysFont("dejavusansmono", 32)

    global wid
    if 'window' in pygame.display.get_wm_info():
        wid = pygame.display.get_wm_info()['window']
    print("Tello video WID:", wid)

    #instance of Tello calss
    drone = tellopy.Tello()
    print(drone)
    drone.connect()
    drone.start_video()
    # drone.subscribe(drone.EVENT_FLIGHT_DATA, flightDataHandler)
    # drone.subscribe(drone.EVENT_VIDEO_FRAME, videoFrameHandler)
    drone.subscribe(drone.EVENT_FILE_RECEIVED, handleFileReceived)
    speed = 30


    # tmp = drone.take_picture()
    # print(tmp)



    try:
        while 1:
            time.sleep(0.01)  # loop with pygame.event.get() is too mush tight w/o some sleep
            for e in pygame.event.get():
                # WASD for movement
                if e.type == pygame.locals.KEYDOWN:
                    print('+' + pygame.key.name(e.key))
                    keyname = pygame.key.name(e.key)
                    if keyname == 'escape':
                        drone.quit()
                        exit(0)
                    if keyname in controls:
                        key_handler = controls[keyname]
                        if type(key_handler) == str:
                            getattr(drone, key_handler)(speed)
                        else:
                            key_handler(drone, speed)

                elif e.type == pygame.locals.KEYUP:
                    print('-' + pygame.key.name(e.key))
                    keyname = pygame.key.name(e.key)
                    if keyname in controls:
                        key_handler = controls[keyname]
                        if type(key_handler) == str:
                            getattr(drone, key_handler)(0)
                        else:
                            key_handler(drone, 0)
    except e:
        print(str(e))
    # finally:
    #     print('Shutting down connection to drone...')
    #     if video_recorder:
    #         toggle_recording(drone, 1)
    #     drone.quit()
    #     exit(1)

main()