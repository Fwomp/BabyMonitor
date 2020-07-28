from picamera import PiCamera
import base64
import clientConnection
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
        self.framerate = framerate
        self.frame = (io.BytesIO(), datetime.datetime.now().isoformat(), False)
        self.rLock = threading.Lock()
        
    def run(self):
        print("[+] Recording Video @", self.framerate, "fps")
        self.rLock.acquire()
        self.running = True
        self.rLock.release()
        
        with PiCamera(resolution=self.resolution, framerate=self.framerate) as camera:
            # wait for camera to wake-up
            print("[*] Waking Camera")
            time.sleep(2.0)
            print("[*] Getting Frames")
            buffer = io.BytesIO()
                
            while self.running:
                # reset the buffer
                buffer.seek(0)
                buffer.truncate()
                    
                # take the frame
                camera.capture(buffer, 'jpeg', True)
                
                # send the frame
                self.sendFrame((buffer, datetime.datetime.now().isoformat()))
                    
    def stop(self):
        print("[-] Stopping Recording Video")
        self.rLock.acquire()
        self.running = False
        self.rLock.release()
        
    def sendFrame(self, frame):
        frame[0].seek(0)
        
        # TODO: this is taking ~0.1 seconds per hit - too slow
        self.connection.send("Frame", Make_Frame_Msg(frame[0].read(), frame[1]))