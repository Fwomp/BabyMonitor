from Packages.Server import serverConnection
from Packages.Server import serverVideo
import sys
import time

if __name__ == "__main__":
    CONNECTION = serverConnection.Connection("192.168.1.242",49497)
    VIDEO = serverVideo.Video(CONNECTION)
    
    try:
        CONNECTION.start()
        VIDEO.start()
        
        while VIDEO.getRunning():
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("[-] Interrupt detected")
        pass
    finally:
        CONNECTION.stop()
        VIDEO.stop()
        
        sys.exit()
    