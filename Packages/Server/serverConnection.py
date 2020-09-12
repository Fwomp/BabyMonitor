from ..Common import monitorSocket
import pickle
import socket
import sys
import threading
import time
        
def verify_data(data):
    return True

class Connection(threading.Thread):    
    def __init__(self, S_IP, S_PORT):
        threading.Thread.__init__(self)
        self.running = False
        self.socket  = monitorSocket.SktConnection(S_IP, S_PORT, monitorSocket.Endpoint.SERVER)   
        self.running = False
        self.connected = False
        self.dispatchers = dict()
        self.header_size = 175
        
    def run(self):
        print("[+] Running Connection")
        self.running = True
        
        while self.running:
            if not self.socket.isConnected():
                self.socket.connect()
            else:                
                try:
                    # check whether we have a full header available
                    if self.socket.available(self.header_size):
                        # receive and unpickle our header
                        header_data = pickle.loads(self.socket.recv_all(self.header_size))
                        
                        # get the message data
                        msg_type = header_data['header']['type'].rstrip()
                        msg_size = int(header_data['header']['size'].rstrip())
                    
                        # receive and unpickle our payload
                        payload_data = pickle.loads(self.socket.recv_all(msg_size))
                         
                        # dispatch with the recevied data
                        if msg_type in self.dispatchers:
                            # TODO: Why is the payload increasing in size?
                            self.dispatchers[msg_type].dispatch(payload_data['payload'])
                        else:
                            print("[!] Unknown URI received:", msg_type)
                            
                    elif self.socket.available(self.header_size) == 0:
                        print("[!] Client disconnected!")
                        self.socket.close()
                        self.connected = False
                except:
                    print("[!] Exception: ", sys.exc_info())
                    print("[!] Client disconnected!")
                    self.socket.close()
                    self.connected = False
        
    def stop(self):
        print("[-] Stopping Connection")
        self.running = False
        
    def register(self, dispatcher):
        if not dispatcher.get_URI() in self.dispatchers:
            self.dispatchers[dispatcher.get_URI()] = dispatcher
            print("[+] Registered URI:", dispatcher.get_URI())
        else:
            print("[!] URI already registered:", dispatcher.get_URI())