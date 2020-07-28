import datetime
import enum
import pickle
import socket
import sys
import threading
import time

def make_header(msg_type, payload):
    return {
        "header" : {
            "time" : datetime.datetime.now().isoformat(),
            "type" : msg_type.ljust(32, ' '),
            "size" : len(payload)
        }
    }

class Connection(threading.Thread):    
    def __init__(self, S_IP, S_PORT):
        threading.Thread.__init__(self)
        self.running = False
        self.rLock   = threading.Lock()
        self.cLock   = threading.Lock()
        self.sLock   = threading.Lock()
        self.S_IP    = S_IP
        self.S_PORT  = S_PORT
        self.socket  = None
        self.running = False
        self.connection = None
        
    def __isConnected(self):
        return self.socket is not None
        
    def __connect(self):
        try:
            self.cLock.acquire()
            
            # if we dont currently have a socket
            if not self.__isConnected():
                print("[*] Connecting to server...")
                
                # create the socket
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                
                # connect the socket to the server
                self.socket.connect((self.S_IP, self.S_PORT))
                
                # create a stream from the socket
                self.connection = self.socket.makefile('wb')
                
            self.cLock.release()
        except:
            self.socket.close()
            self.socket = None
            self.cLock.release()
        finally:
            if self.__isConnected():
                print("[*] Connected!")
            
    def __disconnect(self):
        try:
            self.cLock.acquire()
            
            # if we have an socket
            if self.__isConnected():
                print("[*] Disconnecting from server...")
                
                # close the socket
                self.socket.close()
                
                # clear the socket
                self.socket = None
        except:
            print("[!] Something went wrong disconnecting!")
            
        finally:
            if not self.__isConnected():
                print("[*] Disconnected!")
                
            self.cLock.release()
        
        
    def run(self):
        print("[+] Running Connection")
        self.rLock.acquire()
        self.running = True
        self.rLock.release()
        
        while self.running:
            if not self.__isConnected():
                self.__connect()
                
            time.sleep(1)
            
    def stop(self):
        print("[-] Stopping Connection")
        self.rLock.acquire()
        self.running = False
        self.rLock.release()
        
    def send(self, msg_type, payload):
        self.cLock.acquire()
        
        if self.__isConnected():
            try:
                pickled_payload = pickle.dumps(payload)
                pickled_header  = pickle.dumps(make_header(msg_type, pickled_payload))
                
                self.socket.sendall(pickled_header)
                self.socket.sendall(pickled_payload)
            except:
                print("[!] Exception: ", sys.exc_info())
                print("[!] Error sending message")
                self.__disconnect()
                self.cLock.release()
        
        self.cLock.release()
