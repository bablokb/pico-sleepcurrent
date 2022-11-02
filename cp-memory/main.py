#-----------------------------------------------------------------------------
# Test program pico-sleep modes (sleep-memory/nvram/wake_alarm)
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pico-sleepcurrent
#-----------------------------------------------------------------------------

import time
import board
import alarm
import microcontroller
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

PIN_SDA  = board.GP18
PIN_SCL  = board.GP19
PIN_WAKE = board.GP20

displayio.release_displays()
i2c = busio.I2C(sda=PIN_SDA,scl=PIN_SCL,frequency=400000)
display_bus = displayio.I2CDisplay(i2c, device_address=OLED_ADDR)
display = adafruit_displayio_ssd1306.SSD1306(display_bus,
                                             width=OLED_WIDTH,
                                             height=OLED_HEIGHT)

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

group   = displayio.Group()
t_top = label.Label(FONT_S,text='0',color=FG_COLOR,
                    anchor_point=POS_MAP['NW'][0])
t_top.anchored_position = POS_MAP['NW'][1]
group.append(t_top)
t_bot = label.Label(FONT_S,text='0',color=FG_COLOR,
                    anchor_point=POS_MAP['SW'][0])
t_bot.anchored_position = POS_MAP['SW'][1]
group.append(t_bot)
t_slp = label.Label(FONT_S,text='',color=FG_COLOR,
                    anchor_point=POS_MAP['SE'][0])
t_slp.anchored_position = POS_MAP['SE'][1]
group.append(t_slp)
t_alm = label.Label(FONT_S,text='',color=FG_COLOR,
                    anchor_point=POS_MAP['NE'][0])
t_alm.anchored_position = POS_MAP['NE'][1]
group.append(t_alm)


# --- main   -----------------------------------------------------------------

try:
  if alarm.sleep_memory:
    mem_array = alarm.sleep_memory
    mem_type  = 'S'
except:
  mem_array = microcontroller.nvm
  mem_type  = 'N'

if not alarm.wake_alarm:          # reset
  counter = 0
  mem_type = mem_type + 'R'
  t_alm.text = "reset"
else:
  counter  = (int(mem_array[42])+1) % 256
  mem_type = mem_type + 'W'       # wakeup
  if isinstance(alarm.wake_alarm,alarm.time.TimeAlarm):
    t_alm.text = "time"
  else:
    t_alm.text = "pin"

print("wake_alarm: %r" % alarm.wake_alarm)
print("mem_type: %s" % mem_type)
print("counter:  %d" % counter)
t_top.text = mem_type
t_bot.text = "{0:d}".format(counter)
t_slp.text = "active"
display.show(group)
time.sleep(2)

mem_array[42] = counter
pin   = alarm.pin.PinAlarm(PIN_WAKE,value=False,edge=True,pull=True)
timer = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 10)

t_slp.text = "sleep"
display.show(group)
time.sleep(0.5)
alarm.exit_and_deep_sleep_until_alarms(timer,pin)
