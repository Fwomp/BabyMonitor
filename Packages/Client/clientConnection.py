import datetime
import enum
import pickle
from ..Common import monitorSocket
import socket
import sys
import threading
import time

def make_header(msg_type, payload):    
    return {
        "header" : {
            "time" : datetime.datetime.now().isoformat().ljust(32, ' '),
            "type" : msg_type.ljust(32, ' '),
            "size" : str(len(payload)).ljust(32, ' ')
        }
    }

class Connection(threading.Thread):    
    def __init__(self, S_IP, S_PORT):
        threading.Thread.__init__(self)
        self.running = False
        self.S_IP    = S_IP
        self.S_PORT  = S_PORT
        self.running = False
        self.socket  = monitorSocket.SktConnection(S_IP, S_PORT, monitorSocket.Endpoint.CLIENT)        
        
    def run(self):
        print("[+] Running Connection")
        self.running = True
        
        while self.running:
            if not self.socket.isConnected():
                self.socket.connect()
                
            time.sleep(1)
            
    def stop(self):
        print("[-] Stopping Connection")
        self.running = False
        
    def send(self, msg_type, payload):
        if self.socket.isConnected():            
            try:
                pickled_payload = pickle.dumps(payload)
                pickled_header  = pickle.dumps(make_header(msg_type, pickled_payload))
                
                self.socket.send_all(pickled_header)
                self.socket.send_all(pickled_payload)
                
            except:
                print("[!] Exception: ", sys.exc_info())
                print("[!] Error sending message")
                self.socket.close()
        else:
            time.sleep(1)
