import base64
import cv2
import dispatcher
import numpy as np
import serverConnection
import threading
import time

class Video(threading.Thread):        
    class DHT_Dispatcher(dispatcher.Dispatcher):
        def __init__(self, URI):
            super().__init__(URI)
            self.dLock = threading.Lock()
            self.DHT   = (None, None, None)
        
        def dispatch(self, data):
            self.dLock.acquire()
            self.DHT = (data['humidity'], data['temperature'], data['time'])
            self.dLock.release()
            
        def get_data(self):
            self.dLock.acquire()
            DHT = self.DHT
            self.dLock.release()
            
            return DHT      
        
    class Frame_Dispatcher(dispatcher.Dispatcher):
        def __init__(self, URI):
            super().__init__(URI)
            self.dLock = threading.Lock()
            self.frame = (None, None)
            
        def dispatch(self, data):
            self.dLock.acquire()
            self.frame = (data['frame'], data['time'])
            self.dLock.release()
            
        def get_data(self):
            self.dLock.acquire()
            frame = self.frame
            self.dLock.release()
            
            return frame            
            
    def __init__(self, connection):
        threading.Thread.__init__(self)
        self.running = False
        self.rLock = threading.Lock()
        
        # create dispatchers
        self.Frame = self.Frame_Dispatcher("Frame")
        self.DHT   = self.DHT_Dispatcher("DHT")
        
        # register dispatchers
        connection.register(self.Frame)
        connection.register(self.DHT)
        
    def run(self):
        print("[+] Running Video")
        self.rLock.acquire()
        self.running = True
        self.rLock.release()
        
        while self.running:
            frame = self.Frame.get_data()
            
            if frame[0] is not None:
                data = np.fromstring(frame[0], dtype=np.uint8)
                img = cv2.imdecode(data, flags=1)
                
                cv2.imshow("Monitor", img)
                cv2.waitKey(1)
            else:
                time.sleep(1) # Delay
        
    def stop(self):
        print("[-] Stopping Video")
        self.running = False
