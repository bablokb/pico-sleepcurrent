#-----------------------------------------------------------------------------
# Combined test program pico-sleep modes
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pico-sleepcurrent
#-----------------------------------------------------------------------------

import time
import board
import microcontroller
from digitalio import DigitalInOut, Direction, Pull

try:
  import alarm
  ds_2nd = int(alarm.sleep_memory[0] > 0)
except:
  print("warning: no alarm-module: only SPIN/SLEEP/SLOW-tests available")
  ds_2nd = None

try:
  import wifi
  import socketpool
  from secrets import secrets
  HAVE_WIFI = True
  pool = socketpool.SocketPool(wifi.radio)
except:
  HAVE_WIFI = False

# --- constants   ------------------------------------------------------------

LED_TIME     = 1
WORK_TIME    = 10
INT_TIME     = 30 - WORK_TIME
WAKE_PIN     = board.GP16

SPIN         = 0x0
SLEEP        = 0x1
SLOW_SLEEP   = 0x2
LIGHT_SLEEP  = 0x3
DEEP_SLEEP   = 0x4

MODE_STR = {
  SPIN: "SPIN",
  SLEEP: "SLEEP",
  SLOW_SLEEP: "SLOW_SLEEP",
  LIGHT_SLEEP: "LIGHT_SLEEP",
  DEEP_SLEEP: "DEEP_SLEEP",
  }

CPU_FREQ_DEF   = microcontroller.cpu.frequency
CPU_FREQ_SLEEP =  25_000_000

# --- configuration   ----------------------------------------------------------

TOGGLE_WIFI = True

# tests: list of (sleep-mode,time-alarm,pin-alarm)
if ds_2nd:
  # deep-sleep second iteration after reset()
  TESTS = [(DEEP_SLEEP,False,True)]   # deep-sleep with pin-alarm
else:
  TESTS = [(SLEEP,None,None),
           (SLOW_SLEEP,None,None),
           (LIGHT_SLEEP,True,False),
           (LIGHT_SLEEP,False,True),
           (DEEP_SLEEP,True,False)]   # deep-sleep with time-alarm
  #TESTS = [(DEEP_SLEEP,True,False)]

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
  msg(f"working for {WORK_TIME}s, blinking every {LED_TIME}s ...")
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

# --- connect-helper   --------------------------------------------------------

def connect(ssid,password):
  state = wifi.radio.connected
  print(f"  connected: {state}")
  if state:
    return
  for _ in range(3):
    try:
      wifi.radio.connect(ssid,password)
      break
    except ConnectionError as ex:
      print(f"{ex}")
  print(f"  connected: {wifi.radio.connected}")
  if not wifi.radio.connected:
    raise ConnectionError(f"could not connect to {ssid}")

# --- create alarms   --------------------------------------------------------

def get_alarms(time_alarm,pin_alarm):
  alarms = []
  if time_alarm:
    alarms.append(
      alarm.time.TimeAlarm(monotonic_time=time.monotonic()+INT_TIME))
  if pin_alarm:
    alarms.append(
      alarm.pin.PinAlarm(WAKE_PIN,value=False,edge=True,pull=True))
  return alarms

# --- print message (to stdout and UDP)   ------------------------------------

def msg(msg):
  """ print message and send to UDP-socket """
  msg = f"{time.monotonic():9.3f}: {msg}"
  print(msg)
  if HAVE_WIFI and wifi.radio.enabled:
    try:
      with pool.socket(family=socketpool.SocketPool.AF_INET,
                       type=socketpool.SocketPool.SOCK_DGRAM) as socket:
        socket.sendto(
          bytes(f'{msg}\n',"UTF-8"),
          (secrets.udp_ip,secrets.udp_port))
    except Exception as ex:
      print(f"socket.sendto: exception: {ex}")

# --- main loop   ------------------------------------------------------------

if HAVE_WIFI:
  connect(secrets.ssid,secrets.password)

if ds_2nd is None:
  # no alarm-module, no sleep-memory
  pass
elif ds_2nd:
  # second pass, reset sleep-memory
  alarm.sleep_memory[0] = 0
else:
  alarm.sleep_memory[0] = 42  

while True:
  for mode,time_alarm,pin_alarm in TESTS:
    work()     # do some work

    if time_alarm or mode in [SPIN, SLEEP, SLOW_SLEEP]:
      msg(f"{MODE_STR[mode]} for {INT_TIME}s ...")
    if pin_alarm and mode in [LIGHT_SLEEP, DEEP_SLEEP]:
      msg(f"{MODE_STR[mode]} until pin-alarm ...")

    if mode == SPIN:
      next = time.monotonic() + INT_TIME
      while time.monotonic() < next:
        continue
    elif mode == SLEEP:
      time.sleep(INT_TIME)
    elif mode == SLOW_SLEEP:
      if HAVE_WIFI and TOGGLE_WIFI:
        msg("disabling WIFI")
        wifi.radio.enabled = False
      msg(f"cpu-frequency: {microcontroller.cpu.frequency}")
      microcontroller.cpu.frequency = CPU_FREQ_SLEEP
      msg(f"cpu-frequency slow: {microcontroller.cpu.frequency}")
      time.sleep(INT_TIME)
      microcontroller.cpu.frequency = CPU_FREQ_DEF
      if HAVE_WIFI and TOGGLE_WIFI:
        wifi.radio.enabled = True
        connect(secrets.ssid,secrets.password)
        msg("WIFI enabled")
    elif mode == LIGHT_SLEEP:
      if HAVE_WIFI and TOGGLE_WIFI:
        msg("disabling WIFI")
        wifi.radio.enabled = False
      alarm.light_sleep_until_alarms(*get_alarms(time_alarm,pin_alarm))
      if HAVE_WIFI and TOGGLE_WIFI:
        wifi.radio.enabled = True
        connect(secrets.ssid,secrets.password)
        msg("WIFI enabled")
      WORK_TIME *= 1.5
    elif mode == DEEP_SLEEP:
      alarm.exit_and_deep_sleep_until_alarms(*get_alarms(time_alarm,pin_alarm))
      WORK_TIME *= 1.5    # this should have no effect due to reset!
    msg(f"{MODE_STR[mode]} finished")
