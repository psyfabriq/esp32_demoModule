import _thread
import time
from machine import Pin

LED_PIN = Pin(2, Pin.OUT)
LED_SWITCH = False
TS = 0.5


def start_blink():
    global LED_SWITCH
    if not LED_SWITCH:
      LED_SWITCH = True
      _thread.start_new_thread(LED, ())

def stop_blink():
    global LED_SWITCH
    LED_SWITCH = False

def setIntervalBlink(ts:  float):
    global TS
    TS = ts

def LED():
    while LED_SWITCH:
        LED_PIN.value(1)
        time.sleep(TS)
        LED_PIN.value(0)
        time.sleep(TS)