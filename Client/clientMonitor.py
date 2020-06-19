import clientConnection
import clientDHT
import clientVideo
import time

if __name__ == "__main__":
    DHT   = clientDHT.DHT(4,10)
    VIDEO = clientVideo.Video('VGA', 24)
    CONNECTION = clientConnection.Connection("192.168.1.242",49497)
        
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