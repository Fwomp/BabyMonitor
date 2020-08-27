import clientConnection
import clientDHT
import clientVideo
import faulthandler
import time

if __name__ == "__main__":
    faulthandler.enable()
    
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
