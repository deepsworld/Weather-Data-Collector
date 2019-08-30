# Required imports
import threading
from func import start_main, fetch_five_day_forecast

# Threading class to run different activities on different threads. 
class myThread(threading.Thread):
    def __init__(self, type):
        threading.Thread.__init__(self)
        self.type = type

    def run(self):
        start_main(self.type)

if __name__ == "__main__":
    try:
        # Three different threads for 3 tasks. 
        t1 = myThread('five_days')
        t1.start()
        t2 = myThread('sixteen_days')
        t2.start()
        t3 = myThread('weather_maps')
        t3.start()

        # the main thread will stop executing until the execution of joined thread is complete
        t1.join()
        t2.join()
        t3.join()

        fetch_five_day_forecast()
    except IOError as e:
        print(repr(e)) # printable representation of e object