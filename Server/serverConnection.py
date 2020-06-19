import socket
import threading
import time

class Connection(threading.Thread):
    def __init__(self, S_IP, S_PORT):
        threading.Thread.__init__(self)
        self.running = False
        self.rLock   = threading.Lock()
        self.S_IP    = S_IP
        self.S_PORT  = S_PORT
        self.socket  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = False
        self.connected = False
        # TODO: Need to setup re-use address on the socket
        
        self.socket.bind((self.S_IP, self.S_PORT))
        self.socket.listen()
        
    def run(self):
        print("[+] Running Connection")
        self.rLock.acquire()
        self.running = True
        self.rLock.release()
        
        while self.running:
            if not self.connected:
                self.client = self.socket.accept()
                print("[*] New Connection!")
                self.connected = True
            else:
                time.sleep(2)
        
    def stop(self):
        print("[-] Stopping Connection")
        self.running = False