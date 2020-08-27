import Adafruit_DHT
import datetime
import threading
import time

def Make_DHT_Msg(humidity, temperature, time):
    payload = {
        "payload" : {
            "humidity"    : humidity,
            "temperature" : temperature,
            "time"        : time
        }
    }
    
    return payload

class DHT(threading.Thread):
    def __init__(self, pin, rate, connection):
        threading.Thread.__init__(self)
        
        self.DHT_SENSOR = Adafruit_DHT.DHT22
        self.DHT_PIN  = pin
        self.running  = False
        self.rate  = rate
        self.rLock = threading.Lock()
        self.connection = connection
        
    def run(self):
        print("[+] Running DHT")
        self.rLock.acquire()
        self.running = True
        self.rLock.release()
        
        while self.running:
            humidity, temperature = Adafruit_DHT.read_retry(self.DHT_SENSOR, self.DHT_PIN)
        
            if humidity is not None and temperature is not None:                
                # send the frame
                self.connection.send("DHT", Make_DHT_Msg(round(humidity,1), round(temperature,1), datetime.datetime.now()))                
                
            else:
                print("[!] DHT Error")
            
            time.sleep(self.rate)
        
    def stop(self):
        print("[-] Stopping DHT")
        self.rLock.acquire()
        self.running = False
        self.rLock.release()
            
    def get_DHT(self):
        self.vLock.acquire()
        vDHT = (self.humidity, temperature)
        self.vLock.release()
        
        return vDHT
