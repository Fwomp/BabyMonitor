import datetime
import enum
import json
import socket
import threading
import time

# What if we create a dispatcher? - We register URI's, then we messages come in we check the
# hash and then dispatch to the handler registered against the URI.
# message : {
#    header : {
#       type : <string>
#       time : <float?>
#       checksum : <string>
#    }
#    body : {
#       if DHT:
#          temperature : <float>
#          humidity : <float>
#          time : <float?>
#    }
# }

def __make_message(msg_type, payload):
    return {
        "header" : {
            "type" : msg_type,
            "time" : datetime.datetime.now().isoformat()
        },
        "payload" : payload
    }

def Make_DHT_Msg(humidity, temperature, time):
    payload = {
        "humidity"    : humidity,
        "temperature" : temperature,
        "time"        : time
    }
    
    return __make_message("DHT", payload)

def Make_Frame_Msg(frame, time):
    payload = {
        "frame" : frame,
        "time"  : time
    }
    
    return __make_message("Frame", payload)    

class Connection(threading.Thread):
    def __init__(self, S_IP, S_PORT):
        threading.Thread.__init__(self)
        self.running = False
        self.rLock   = threading.Lock()
        self.S_IP    = S_IP
        self.S_PORT  = S_PORT
        self.socket  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = False
        
    def __connect(self):
        self.connected = False
        
        while not self.connected and self.running: 
            #try:
            print("[*] Connecting to server...")
            self.socket.connect((self.S_IP, self.S_PORT))
            self.socket.sendall(json.dumps(Make_DHT_Msg(0, 0, datetime.datetime.now().isoformat())).encode())
            self.handle = self.socket.makefile('wb')
            self.connected = True
            #except:
            #    time.sleep(1)
        if self.connected:
            print("[*] Connected!")
        
        
    def run(self):
        print("[+] Running Connection")
        self.rLock.acquire()
        self.running = True
        self.rLock.release()
        
        self.__connect()
        
        while self.connected and self.running:
            time.sleep(2)
        
    def stop(self):
        print("[-] Stopping Connection")
        self.running = False
