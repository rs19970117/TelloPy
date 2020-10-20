import time
import sys
import tellopy
import datetime

prev_flight_data = None
video_player = None
video_recorder = None
font = None
wid = None
date_fmt = '%Y-%m-%d_%H%M%S'

drone = tellopy.Tello()
drone.connect()
drone.start_video()
drone.subscribe(drone.EVENT_FLIGHT_DATA, flightDataHandler)
drone.subscribe(drone.EVENT_VIDEO_FRAME, videoFrameHandler)
drone.subscribe(drone.EVENT_FILE_RECEIVED, handleFileReceived)
speed = 30

def take_picture(drone):
    print("before")
    drone.take_picture()
    print("done")


# def take_picture(self):
#     log.info('take picture')
#     return self.send_packet_data(TAKE_PICTURE_COMMAND, type=0x68)
#     drone.take_picture()
#     print("done")

def handleFileReceived(event, sender, data):
    global date_fmt
    # Create a file in ~/Pictures/ to receive image data from the drone.
    path = '%s/Pictures/tello-%s.jpeg' % (
        os.getenv('HOME'),
        datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S'))
    with open(path, 'wb') as fd:
        fd.write(data)
    status_print('Saved photo to %s' % path)

take_picture()
handleFileReceived()