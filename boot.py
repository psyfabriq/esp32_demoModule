
from machine import UART
from main.state import Context
import os
import gc
import esp

esp.osdebug(None)
context = Context()
gc.collect()
