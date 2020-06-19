from picamera import PiCamera
import io
import threading
import time

class Video(threading.Thread):
    def __init__(self, resolution, framerate):
        threading.Thread.__init__(self)
        
        self.resolution = resolution
        self.framerate = framerate
        self.stream = io.BytesIO()
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
                self.vLock.acquire()
                
                # reset the buffer
                self.stream.seek(0)
                self.stream.truncate()
                    
                # take the frame
                camera.capture(self.stream,'jpeg',True)
                self.vLock.release()
                    
    def stop(self):
        print("[-] Stopping Recording Video")
        self.rLock.acquire()
        self.running = False
        self.rLock.release()
        
    def getFrame(self):
        self.vLock.acquire()
        frame = self.stream
        self.vLock.release()
        
        return frame