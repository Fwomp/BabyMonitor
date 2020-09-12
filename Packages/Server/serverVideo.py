import base64
import cv2
import datetime
from . import dispatcher
import numpy as np
from . import serverConnection
import threading
import time

# TODO: we want to rename this class to something more fitting - screen or output?
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
            self.frame_time  = time.time()
            self.frame_count = 0
            
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
        
        # setup thresholds in seconds
        self.frame_threshold = 3
        self.dht_threshold   = 120
        
        # setup frame data
        self.font   = cv2.FONT_HERSHEY_SIMPLEX
        self.iThick = 2
        self.oThick = 5
        self.line   = cv2.LINE_AA
        
    def get_datetime(self, datetime_str):
        return datetime.datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S.%f')
        
    def valid_frame(self, frame):
        # do we have a frame to start with?
        if frame[0] is not None:
            # is the frame within our threshold?
            if datetime.datetime.now() - datetime.timedelta(seconds=self.frame_threshold) < frame[1]:
                return True
            
        return False
    
    def valid_dht(self, dht):
        if dht[1] is not None:
            # is the dht within our threshold?
            if datetime.datetime.now() - datetime.timedelta(seconds=self.dht_threshold) < dht[2]:
                return True
            
        return False
    
    def add_text(self, text, location, image):
        # add the text to the image with a border
        image = cv2.putText(image, text, location, self.font, 1, (000,000,000), self.oThick, self.line)
        image = cv2.putText(image, text, location, self.font, 1, (255,255,255), self.iThick, self.line)
        
        return image
    
    def add_text_center(self, text, image):
        # get boundary of this text
        textsize_1 = cv2.getTextSize(text, self.font, 1, self.oThick)[0]
        
        # get co-ords based on boundary
        text1_x = int((image.shape[1] - textsize_1[0]) / 2)
        text1_y = int((image.shape[0] + textsize_1[1]) / 2)
        
        # add the text to the image with a border
        image = cv2.putText(image, text, (text1_x, text1_y), self.font, 1, (000,000,000), self.oThick, self.line)
        image = cv2.putText(image, text, (text1_x, text1_y), self.font, 1, (255,255,255), self.iThick, self.line)
        
        # return the image
        return image
        
    def run(self):
        self.rLock.acquire()
        self.running = True
        self.rLock.release()
        
        print("[+] Running Video")        
        cv2.namedWindow("Monitor", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("Monitor", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        while self.running:
            frame = self.Frame.get_data()
            dht   = self.DHT.get_data()
            image = np.zeros((480, 680, 3), np.uint8)
            
            if self.valid_frame(frame):
                image = frame[0]
            else:
                # TODO: We want to fall in here if the last frame is too old and show no connection
                image = self.add_text_center("Not connected...", image)
                time.sleep(1) # Delay until we get a frame
                
            # TODO: We need to add the temperature to the screen
            if self.valid_dht(dht):
                image = self.add_text(str(dht[1]) + 'C', (10,35), image)
            else:
                image = self.add_text('N/A', (10,35), image)
            
            # show the frame image
            cv2.imshow("Monitor", image)
            
            if (cv2.waitKey(100) & 0xFF) == ord('q'):
                self.stop()
            
        
    def stop(self):
        if self.running:
            print("[-] Stopping Video")
            cv2.destroyAllWindows()
            self.running = False
            
    def getRunning(self):
        self.rLock.acquire()
        running = self.running
        self.rLock.release()
        
        return running