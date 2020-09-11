from enum import Enum
import socket
import threading

class Endpoint(Enum):
    SERVER = 1
    CLIENT = 2

class SktConnection():
    def __init__(self, Addr, Port, Endpoint):
        self.endpoint = Endpoint
        self.addr = Addr
        self.port = Port        
        self.socket = None
        self.cLock  = threading.RLock()
        
        if Endpoint is Endpoint.SERVER:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.settimeout(1.0)
            self.server.bind((self.addr, self.port))
            self.server.listen()
            
    def isConnected(self):
        self.cLock.acquire()
        connected = self.socket is not None
        self.cLock.release()
        
        return connected
            
    def connect(self):
        result = False
        
        if self.endpoint is Endpoint.SERVER:
            try:
                self.cLock.acquire()
                self.socket, address = self.server.accept()
                self.socket.settimeout(10.0)
                result = True
                print("[*] New Connection: ", address)
            except:
                pass
            finally:
                self.cLock.release()
                
        elif self.endpoint is Endpoint.CLIENT:
            try:
                self.cLock.acquire()
            
                # if we dont currently have a socket
                if not self.isConnected():
                    print("[*] Connecting to server...")
                        
                    # create the socket
                    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                
                    # connect the socket to the server
                    self.socket.connect((self.addr, self.port))
                
                    # create a stream from the socket
                    self.connection = self.socket.makefile('wb')
                    
                    # setup the result to the caller            
                    result = True
                
            except:
                self.socket.close()
                self.socket = None
            
            finally:
                if self.isConnected():
                    print("[*] Connected!")
                    
                self.cLock.release()
                
        return result
            
    def available(self, size):
        try:
            return len(self.socket.recv(size, socket.MSG_PEEK))
        except:
            self.close()
            return 0
    
    def recv_all(self, size):
        try:
            buffer = b''
        
            while len(buffer) < size:
                buffer += self.socket.recv(size - len(buffer))
            
            return buffer
        except:
            self.close()
            return buffer
    
    def send_all(self, data):
        try:
            if self.cLock.acquire(True):
                self.connection.write(data)
                self.cLock.release()
        except:
            self.close()
            self.cLock.release()
                
    def close(self):
        try:
            self.cLock.acquire()
            
            # if we have an socket
            if self.isConnected():
                print("[*] Disconnecting...")
                
                # close the socket
                self.socket.close()
                
                # clear the socket
                self.socket = None
        except:
            print("[!] Something went wrong disconnecting!")
            
        finally:
            if not self.isConnected():
                print("[*] Disconnected!")
                
            self.cLock.release()
    
        
