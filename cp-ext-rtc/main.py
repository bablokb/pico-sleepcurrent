#-----------------------------------------------------------------------------
# Test program pico-sleep mode: PinAlarm via external RTC interrupt
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pico-sleepcurrent
#-----------------------------------------------------------------------------

import time
import board
import alarm
from digitalio import DigitalInOut, Direction, Pull

from adafruit_pcf8523 import PCF8523 as PCF_RTC
#from adafruit_pcf8563 import PCF8563 as PCF_RTC

LED_TIME = 1
INT_TIME = 30 - LED_TIME

WAKE_PIN = board.GP4   # connect to RTC-INT
SDA_PIN  = board.GP2   # connect to RTC-SDA
SCL_PIN  = board.GP3   # connect to RTC-SCL

LIGHT_SLEEP  = 0x3
DEEP_SLEEP   = 0x4
MODE         = DEEP_SLEEP

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

intpin           = DigitalInOut(WAKE_PIN)
intpin.direction = Direction.INPUT

i2c = busio.I2C(SCL_PIN,SDA_PIN)
rtc = PCF_RTC(i2c)

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

# --- reset rtc   ------------------------------------------------------------

def reset():
  rtc.timerA_enabled   = False
  rtc.timerA_interrupt = False
  rtc.timerA_status    = False
  rtc.timerA_frequency = rtc.TIMER_FREQ_1HZ
  rtc.timerA_value     = INT_TIME
  rtc.timerA_enabled   = True

# --- main loop   ------------------------------------------------------------

while True:
  reset()
  work()
  pin_alarm = alarm.pin.PinAlarm(WAKE_PIN,value=False,edge=True,pull=True)
  if MODE == LIGHT_SLEEP:
    alarm.light_sleep_until_alarms(pin_alarm)
  elif MODE == DEEP_SLEEP:
    alarm.exit_and_deep_sleep_until_alarms(pin_alarm)
