import serverConnection
import serverVideo
import time

if __name__ == "__main__":
    CONNECTION = serverConnection.Connection("192.168.1.242",49497)
    VIDEO = serverVideo.Video(CONNECTION)
    
    try:
        CONNECTION.start()
        VIDEO.start()
        
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[-] Interrupt detected")
        pass
    finally:
        CONNECTION.stop()
        VIDEO.stop()
    