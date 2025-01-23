#-----------------------------------------------------------------------------
# Test program pico-sleep modes (PinAlarm)
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pico-sleepcurrent
#-----------------------------------------------------------------------------

import time
import board
import alarm
from digitalio import DigitalInOut, Direction, Pull

LED_TIME    = 1
WORK_TIME   = 10
WAKE_PIN    = board.GP16

LIGHT_SLEEP = 0x3
DEEP_SLEEP  = 0x4
MODE        = LIGHT_SLEEP

# --- create objects   --------------------------------------------------------

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

# --- simulate work   --------------------------------------------------------

def work():
  print(f"working for {WORK_TIME}s, blinking every {LED_TIME}s ...")
  start = time.monotonic()
  end = start + WORK_TIME-2*LED_TIME
  while time.monotonic() < end:
    if hasattr(board,'NEOPIXEL'):
      led_power.value = 1
      neopixel_write.neopixel_write(led,led_value)
      time.sleep(LED_TIME)
      led_power.value = 0
    else:
      led.value = 1
      time.sleep(LED_TIME)
      led.value = 0
    time.sleep(LED_TIME)

# --- main loop   ------------------------------------------------------------

while True:
  work()
  pin_alarm = alarm.pin.PinAlarm(WAKE_PIN,value=False,edge=True,pull=True)
  if MODE == LIGHT_SLEEP:
    print(f"light-sleeping until pin-alarm ...")
    alarm.light_sleep_until_alarms(pin_alarm)
    WORK_TIME *= 1.5
  elif MODE == DEEP_SLEEP:
    print(f"deep-sleeping until pin-alarm ...")
    alarm.exit_and_deep_sleep_until_alarms(pin_alarm)
    WORK_TIME *= 1.5    # this should have no effect due to reset!
