import Adafruit_DHT
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
    def __init__(self, pin, rate):
        threading.Thread.__init__(self)
        
        self.DHT_SENSOR = Adafruit_DHT.DHT22
        self.DHT_PIN  = pin
        self.running  = False
        self.humidity = None
        self.temperature = None
        self.rate = rate
        self.rLock = threading.Lock()
        self.vLock = threading.Lock()
        
    def run(self):
        print("[+] Running DHT")
        self.rLock.acquire()
        self.running = True
        self.rLock.release()
        
        while self.running:
            humidity, temperature = Adafruit_DHT.read_retry(self.DHT_SENSOR, self.DHT_PIN)
        
            if humidity is not None and temperature is not None:
                self.vLock.acquire()
                self.humidity = humidity
                self.temperature = temperature
                self.vLock.release()
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
