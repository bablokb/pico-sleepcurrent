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
try:
  import alarm
  flip = int(alarm.sleep_memory[0] > 0)
except:
  print("warning: no alarm-module: only SPIN/SLEEP-tests available")
  flip = 0

from digitalio import DigitalInOut, Direction, Pull

LED_TIME     = 1
WORK_TIME    = 10
INT_TIME     = 30 - WORK_TIME

SPIN         = 0x1
SLEEP        = 0x2
LIGHT_SLEEP  = 0x3
DEEP_SLEEP   = 0x4
MODE         = LIGHT_SLEEP

CPU_FREQ_DEF = microcontroller.cpu.frequency
CPU_FREQ     =  25_000_000
CPU_FREQ     = None

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

if CPU_FREQ:
  freqs = [CPU_FREQ_DEF,CPU_FREQ]
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
    print(f"spinning for {INT_TIME}s ...")
    next = time.monotonic() + INT_TIME
    while time.monotonic() < next:
      continue
  elif MODE == SLEEP:
    print(f"sleeping for {INT_TIME}s ...")
    time.sleep(INT_TIME)
  elif MODE == LIGHT_SLEEP:
    print(f"light-sleeping for {INT_TIME}s ...")
    time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic()+INT_TIME)
    alarm.light_sleep_until_alarms(time_alarm)
    WORK_TIME *= 1.5
  elif MODE == DEEP_SLEEP:
    print(f"deep-sleeping for {INT_TIME}s ...")
    if CPU_FREQ:
      alarm.sleep_memory[0] = flip
    time_alarm = alarm.time.TimeAlarm(monotonic_time=time.monotonic()+INT_TIME)
    alarm.exit_and_deep_sleep_until_alarms(time_alarm)
    WORK_TIME *= 1.5    # this should have no effect due to reset!
