import tellopy
# tl = tellopy.Tello()
# tl.connect()
# tl.takeoff()
# tl.take_picture()
# tl.quit()

def take_picture(drone, speed):
    if speed == 0:
        return
    drone.take_picture()


    def take_picture(self):
        log.info('take picture')
        return self.send_packet_data(TAKE_PICTURE_COMMAND, type=0x68)