from picamera import PiCamera
import base64
import clientConnection
import datetime
import io
import threading
import time

def Make_Frame_Msg(frame, time):
    return {
        "frame" : base64.encodestring(frame.read()).decode(),
        "time"  : time
    }

class Video(threading.Thread):
    def __init__(self, resolution, framerate, connection):
        threading.Thread.__init__(self)
        
        self.connection = connection
        self.resolution = resolution
        self.framerate = framerate
        self.frame = (io.BytesIO(), datetime.datetime.now().isoformat(), False)
        self.rLock = threading.Lock()
        self.vLock = threading.Lock()
        
    def run(self):
        print("[+] Recording Video")
        self.rLock.acquire()
        self.running = True
        self.rLock.release()
        
        with PiCamera(resolution=self.resolution, framerate=self.framerate) as camera:
            # wait for camera to wake-up
            print("[*] Waking Camera")
            time.sleep(2.0)
            print("[*] Getting Frames")
                
            while self.running:
                # lock the frame handle
                self.vLock.acquire()
                
                # reset the buffer
                self.frame[0].seek(0)
                self.frame[0].truncate()
                    
                # take the frame
                camera.capture(self.frame[0],'jpeg',True)
                self.frame = (self.frame[0], datetime.datetime.now().isoformat(), True)
                
                # release the frame handle
                self.vLock.release()
                
                self.sendFrame()
                    
    def stop(self):
        print("[-] Stopping Recording Video")
        self.rLock.acquire()
        self.running = False
        self.rLock.release()
        
    def sendFrame(self):
        self.vLock.acquire()
        frame = self.frame
        self.vLock.release()
        
        if frame[2]:
            self.connection.send("Frame", Make_Frame_Msg(frame[0], frame[1]))
        
        return frame