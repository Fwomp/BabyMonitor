import pickle
import socket
import sys
import threading
import time
        
def verify_data(data):
    return True

class Connection(threading.Thread):
    def recv_all(self, client, size):
        buffer = b''
        
        while len(buffer) < size:
            buffer += client.recv(size - len(buffer))
            
        return buffer
    
    def __init__(self, S_IP, S_PORT):
        threading.Thread.__init__(self)
        self.running = False
        self.rLock   = threading.Lock()
        self.S_IP    = S_IP
        self.S_PORT  = S_PORT
        self.socket  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = False
        self.connected = False
        self.dispatchers = dict()
        
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((self.S_IP, self.S_PORT))
        self.socket.listen()
        
    def run(self):
        print("[+] Running Connection")
        self.rLock.acquire()
        self.running = True
        self.rLock.release()
        
        while self.running:
            if not self.connected:
                client, address = self.socket.accept()
                client.settimeout(60.0)
                print("[*] New Connection: ", address)
                self.connected = True
            else:                
                try:
                    # receive and unpickle our 135 byte header
                    header_data = pickle.loads(self.recv_all(client, 135))
                    
                    # receive and unpickle our payload
                    payload_data = pickle.loads(self.recv_all(client, header_data['header']['size']))
                        
                    # get the message type
                    msg_type = header_data['header']['type'].rstrip()
                    
                    # dispatch with the recevied data
                    if msg_type in self.dispatchers:
                        self.dispatchers[msg_type].dispatch(payload_data['payload'])
                    else:
                        print("[!] Unknown URI received:", msg_type)
                except:
                    print("[!] Exception: ", sys.exc_info())
                    print("[!] Client disconnected!")
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