import socket
import threading
import time

# Protocol: JSON
# message : {
#    header : {
#       type : <enum>
#       checksum : <string>
#    }
#    body : {
#       if DHT:
#          temperature : <float>
#          humidity : <float>
#          datetime : <float?>
#    }
# }

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
            try:
                print("[*] Connecting to server...")
                self.socket.connect((self.S_IP, self.S_PORT))
                self.handle = self.socket.makefile('wb')
                self.connected = True
            except:
                time.sleep(1)
        
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
