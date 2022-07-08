#-----------------------------------------------------------------------------
# Test program pico-sleep modes: RTC-behavior
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pico-sleepcurrent
#-----------------------------------------------------------------------------

import board

LIGHT_SLEEP_T = 0x1    # TimerAlarm
DEEP_SLEEP_T  = 0x2    # TimerAlarm
LIGHT_SLEEP_P = 0x3    # PinAlarm
DEEP_SLEEP_P  = 0x4    # PinAlarm
WAKE_PIN      = board.GP16
MODE          = DEEP_SLEEP_P

INT_TIME      = 30

import time
import rtc
import alarm
from digitalio import DigitalInOut, Direction, Pull

# output to OLED-display (deep-sleep won't work with usb-serial)
import busio
import displayio
import adafruit_displayio_ssd1306          # I2C-OLED display
OLED_ADDR   = 0x3C
OLED_WIDTH  = 128
OLED_HEIGHT = 64

from adafruit_display_text import label
from adafruit_bitmap_font import bitmap_font

# --- initialization   -------------------------------------------------------

# --- display ----

PIN_SDA = board.GP18
PIN_SCL = board.GP19
displayio.release_displays()
i2c = busio.I2C(sda=PIN_SDA,scl=PIN_SCL,frequency=400000)
display_bus = displayio.I2CDisplay(i2c, device_address=OLED_ADDR)
display = adafruit_displayio_ssd1306.SSD1306(display_bus,
                                             width=OLED_WIDTH,
                                             height=OLED_HEIGHT)

# --- texts ----

FONT_S   = bitmap_font.load_font("fonts/DejaVuSansMono-Bold-18-min.bdf")
FG_COLOR = 0xFFFFFF
POS_MAP = {
  'NW': ((0.0,0.0),(0,               0)),
  'NE': ((1.0,0.0),(display.width,   0)),
  'W':  ((0.0,0.5),(0,               display.height/2)),
  'C':  ((0.5,0.5),(display.width/2, display.height/2)),
  'E':  ((1.0,0.5),(display.width,   display.height/2)),
  'SW': ((0.0,1.0),(0,               display.height)),
  'SE': ((1.0,1.0),(display.width,   display.height)),
  }

group    = displayio.Group()
txt_time = label.Label(FONT_S,text='00:00',color=FG_COLOR,
                       anchor_point=POS_MAP['C'][0])
txt_time.anchored_position = POS_MAP['C'][1]
group.append(txt_time)

# --- RTC ----

board_rtc = rtc.RTC()
if time.localtime().tm_mon != 4:
  board_rtc.datetime = time.struct_time((2022, 4, 22, 12, 0, 0, 4, -1, -1))

# --- update clock   ---------------------------------------------------------

def update_clock():
  now           = time.localtime()
  txt_time.text = "{0:02d}:{1:02d}".format(now.tm_min,now.tm_sec)
  display.show(group)
  display.refresh()

# --- main loop   ------------------------------------------------------------

while True:
  start = time.monotonic()
  update_clock()
  if MODE == LIGHT_SLEEP_T:
    time_alarm = alarm.time.TimeAlarm(monotonic_time=INT_TIME+start)
    alarm.light_sleep_until_alarms(time_alarm)
  elif MODE == DEEP_SLEEP_T:
    time_alarm = alarm.time.TimeAlarm(monotonic_time=INT_TIME+start)
    displayio.release_displays()
    alarm.exit_and_deep_sleep_until_alarms(time_alarm)
  elif MODE == LIGHT_SLEEP_P:
    pin_alarm = alarm.pin.PinAlarm(WAKE_PIN,value=False,edge=True,pull=True)
    alarm.light_sleep_until_alarms(pin_alarm)
  elif MODE == DEEP_SLEEP_P:
    pin_alarm = alarm.pin.PinAlarm(WAKE_PIN,value=False,edge=True,pull=True)
    displayio.release_displays()
    alarm.exit_and_deep_sleep_until_alarms(pin_alarm)
