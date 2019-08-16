#!/usr/bin/env python3

import time
import board
import json
from threading import Thread
import adafruit_dotstar as dotstar
import roslibpy

LAMP_COUNT =  359
MAX_BRIGHTNESS = 0.4
BAUDRATE = 10000000

class LampController:
    def __init__(self):
        self.is_connected = False
        self.running_thread = True

        self.lamp_mode = 0
        self.dots = dotstar.DotStar(board.SCK, board.MOSI, LAMP_COUNT, brightness=MAX_BRIGHTNESS, baudrate=BAUDRATE)
        self.dots.fill((0, 0, 0))

        self.lamp_thread = Thread(target=self.thread_callback)
        self.lamp_thread.start()

        self.client = roslibpy.Ros(host="192.168.1.207", port=9090)
        self.client.on_ready(lambda: self.on_connected())        
        
        self.client.run_forever()
    
    def on_receive_message(self, message):
        #self.dots.fill((0, 0, 0))
        self.lamp_mode = 1

    def on_connected(self):
        print("connected successfully to ROS.")
        self.is_connected = True
        self.listener = roslibpy.Topic(self.client, '/chatter', 'std_msgs/String')
        self.listener.subscribe(self.on_receive_message)        

    def stop(self):
        print('stop')
        self.client.close()
        self.is_connected = False
        self.running_thread = False
        self.lamp_thread.join()

        self.dots.fill((0, 0, 0))
        time.sleep(1)
        self.dots.fill((0, 0, 0))

    def thread_callback(self):
        cnt = 0
        direction = 1
        
        while(self.running_thread):
            if(self.is_connected and not self.client.is_connected):
                print("disconnected from ROS.")
                self.client.close()
                self.is_connected = False

                self.lamp_mode = 0                
                self.client.on_ready(lambda: self.on_connected())

            if self.lamp_mode == 0:
                self.dots.fill((cnt, cnt, cnt))
                if direction == 0:
                    cnt += 4
                    if cnt > 255:
                        direction = 1
                        cnt = 255
                else:
                    cnt -= 4
                    if cnt < 0:
                        direction = 0
                        cnt = 0

            elif self.lamp_mode == 1:
                self.dots.fill((0, 100, 0))
            else:
                print("connected")
                time.sleep(0.5)          

if __name__ == '__main__':
    m = LampController()
    m.stop()
    
