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
        self.S_IP    = S_IP
        self.S_PORT  = S_PORT
        self.socket  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = False
        self.connected = False
        self.dispatchers = dict()
        self.header_size = 175
        
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.settimeout(1.0)
        self.socket.bind((self.S_IP, self.S_PORT))
        self.socket.listen()
        
    def run(self):
        print("[+] Running Connection")
        self.running = True
        
        while self.running:
            if not self.connected:
                try:
                    client, address = self.socket.accept()
                    client.settimeout(10.0)
                    print("[*] New Connection: ", address)
                    self.connected = True
                except:
                    pass
            else:                
                try:
                    # check whether we have a full header available
                    if len(client.recv(self.header_size, socket.MSG_PEEK)):
                        # receive and unpickle our header
                        header_data = pickle.loads(self.recv_all(client, self.header_size))
                        
                        # get the message data
                        msg_type = header_data['header']['type'].rstrip()
                        msg_size = int(header_data['header']['size'].rstrip())
                    
                        # receive and unpickle our payload
                        payload_data = pickle.loads(self.recv_all(client, msg_size))
                         
                        # dispatch with the recevied data
                        if msg_type in self.dispatchers:
                            # TODO: Why is the payload increasing in size?
                            self.dispatchers[msg_type].dispatch(payload_data['payload'])
                        else:
                            print("[!] Unknown URI received:", msg_type)
                            
                    elif len(client.recv(self.header_size, socket.MSG_PEEK)) == 0:
                        print("[!] Client disconnected!")
                        client.close()
                        self.connected = False
                except:
                    print("[!] Exception: ", sys.exc_info())
                    print("[!] Client disconnected!")
                    client.close()
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