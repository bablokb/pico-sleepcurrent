import time
import board
import alarm
import microcontroller

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

PIN_SDA = board.GP18
PIN_SCL = board.GP19
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
  counter  = (int(mem_array[42])+1) % 256
else:
  counter  = (int(mem_array[42])+1) % 256
  mem_type = mem_type + 'W'       # wakeup

print("mem_type: %s" % mem_type)
print("counter:  %d" % counter)
t_top.text = mem_type
t_bot.text = "{0:d}".format(counter)
display.show(group)
time.sleep(5)

mem_array[42] = counter
timer = alarm.time.TimeAlarm(monotonic_time=time.monotonic() + 20)
alarm.exit_and_deep_sleep_until_alarms(timer)
