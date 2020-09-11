from picamera import PiCamera
import picamera.array
import base64
from . import clientConnection
import datetime
import io
import threading
import time

def Make_Frame_Msg(frame, time):
    payload = {
        "payload" : {
            "frame" : frame,
            "time"  : time
        }
    }
    
    return payload

class Video(threading.Thread):
    def __init__(self, resolution, framerate, connection):
        threading.Thread.__init__(self)
        
        self.connection = connection
        self.resolution = resolution
        self.framerate  = framerate
        self.rLock = threading.Lock()
        
    def run(self):
        self.rLock.acquire()
        self.running = True
        self.rLock.release()
        
        with PiCamera(resolution=self.resolution, framerate=self.framerate) as camera:
            with picamera.array.PiRGBArray(camera) as stream:
               # wait for camera to wake-up
                time.sleep(2.0)
                print("[+] Recording Video")
                
                while self.running:
                    try:
                        # reset the buffer
                        stream.truncate(0)
                    
                        # take the frame
                        camera.capture(stream, 'rgb', True)
                
                        # send the frame
                        self.sendFrame((stream.array, datetime.datetime.now()))
                    except:
                        print("[!] Error capturing...")
                    
    def stop(self):
        print("[-] Stopping Recording Video")
        self.rLock.acquire()
        self.running = False
        self.rLock.release()
        
    def sendFrame(self, frame):
        self.connection.send("Frame", Make_Frame_Msg(frame[0], frame[1]))