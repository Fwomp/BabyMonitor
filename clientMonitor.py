from Packages.Client import clientConnection
from Packages.Client import clientDHT
from Packages.Client import clientVideo
import time

if __name__ == "__main__":    
    CONNECTION = clientConnection.Connection("192.168.1.242",49497)
    DHT   = clientDHT.DHT(4, 10, CONNECTION)
    VIDEO = clientVideo.Video((640,480), 24, CONNECTION)
        
    try:
        CONNECTION.start()
        DHT.start()
        VIDEO.start()
        
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[-] Interrupt detected")
        pass
    finally:
        CONNECTION.stop()
        DHT.stop()
        VIDEO.stop()
