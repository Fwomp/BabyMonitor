import serverConnection
import time

if __name__ == "__main__":
    CONNECTION = serverConnection.Connection("192.168.1.242",49497)
    
    try:
        CONNECTION.start()
        
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[-] Interrupt detected")
        pass
    finally:
        CONNECTION.stop()
    