#-----------------------------------------------------------------------------
# Test program pico-sleep modes: Use an external driver for the 3V3_EN pin
#
# The example setup is with the TPL5111 enable-timer breakout from
# Adafruit, see https://adafru.it/3573.
# 
# Wiring:
#   ENout -> 3V3_EN (pin 37 of the pico)
#   Done  <- GP28
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pico-sleepcurrent
#-----------------------------------------------------------------------------

import board

LED_TIME = 1
DONE_PIN = board.GP28

import time
from digitalio import DigitalInOut, Direction, Pull

# --- initialization   -------------------------------------------------------

# --- LED ----

if hasattr(board,'NEOPIXEL'):
  import neopixel_write
  led                 = DigitalInOut(board.NEOPIXEL)
  led.direction       = Direction.OUTPUT
  led_power           = DigitalInOut(board.NEOPIXEL_POWER)
  led_power.direction = Direction.OUTPUT
  led_value           = bytearray([255,0,0])  # GRB
else:
  led           = DigitalInOut(board.LED)
  led.direction = Direction.OUTPUT

# --- DONE_PIN ----

power_off           = DigitalInOut(DONE_PIN)
power_off.pull      = Pull.DOWN
power_off.direction = Direction.OUTPUT
power_off.value     = False

# --- simulate work   --------------------------------------------------------

def work():
  if hasattr(board,'NEOPIXEL'):
    led_power.value = 1
    neopixel_write.neopixel_write(led,led_value)
    time.sleep(LED_TIME)
    led_power.value = 0
  else:
    led.value = 1
    time.sleep(LED_TIME)
    led.value = 0

# --- main loop   ------------------------------------------------------------

work()
power_off.value = True
