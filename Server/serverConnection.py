import json
import socket
import threading
import time
        
def verify_data(data):
    return True

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
        self.dispatchers = dict()
        
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
                print("[*] New Connection: ", address)
                self.connected = True
            else:
                data = json.loads(client.recv(1024).decode())
                
                if verify_data(data) and data['header']['type'] in self.dispatchers:
                    self.dispatchers[data['header']['type']].dispatch(data['payload'])
                else:
                    print("[!] Unknown URI received:", data['header']['type'])
        
    def stop(self):
        print("[-] Stopping Connection")
        self.running = False
        
    def register(self, dispatcher):
        if not dispatcher.get_URI() in self.dispatchers:
            self.dispatchers[dispatcher.get_URI()] = dispatcher
            print("[+] Registered URI: ", dispatcher.get_URI())
        else:
            print("[!] URI already registered: ", dispatcher.get_URI())