#-----------------------------------------------------------------------------
# Test program pico-sleep modes
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pico-sleepcurrent
#-----------------------------------------------------------------------------

import time
import board
import microcontroller
import alarm
from digitalio import DigitalInOut, Direction, Pull

LED_TIME     = 1
INT_TIME     = 30 - LED_TIME

SPIN         = 0x1
SLEEP        = 0x2
LIGHT_SLEEP  = 0x3
DEEP_SLEEP   = 0x4
MODE         = LIGHT_SLEEP

CPU_FREQ_DEF = 125000000
CPU_FREQ     =  40000000
#CPU_FREQ     = None

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

if CPU_FREQ:
  freqs = [CPU_FREQ_DEF,CPU_FREQ]
  flip = int(alarm.sleep_memory[0] > 0)
  print(f"cpu-frequency: {microcontroller.cpu.frequency}")

while True:
  # toggle frequency every second cycle
  if CPU_FREQ:
    microcontroller.cpu.frequency = freqs[flip]
    flip = 1 - flip
    print(f"cpu-frequency: {microcontroller.cpu.frequency}")

  # do some work
  work()

  # sleep
  if MODE == SPIN:
    next = time.monotonic() + INT_TIME
    while time.monotonic() < next:
      continue
  elif MODE == SLEEP:
    time.sleep(INT_TIME)
  elif MODE == LIGHT_SLEEP:
    time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic()+INT_TIME)
    alarm.light_sleep_until_alarms(time_alarm)
  elif MODE == DEEP_SLEEP:
    if CPU_FREQ:
      alarm.sleep_memory[0] = flip
    time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic()+INT_TIME)
    alarm.exit_and_deep_sleep_until_alarms(time_alarm)
