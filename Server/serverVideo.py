import base64
import dispatcher
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
            self.frame = (base64.decodestring(data['frame'].encode()), data['time'])
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
        self.DHT = self.DHT_Dispatcher("DHT")
        self.Frame = self.Frame_Dispatcher("Frame")
        
        # register dispatchers
        connection.register(self.DHT)
        connection.register(self.Frame)
        
    def run(self):
        print("[+] Running Video")
        self.rLock.acquire()
        self.running = True
        self.rLock.release()
        
        while self.running:
            if not self.Frame.get_data()[0]:
                time.sleep(1) # Do something
            else:
                time.sleep(1) # Delay
        
    def stop(self):
        print("[-] Stopping Video")
        self.running = False
