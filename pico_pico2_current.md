Light-Sleep/Deep-Sleep Current for RP2xxx
=========================================

All measurements at 5V with Nordic PPKII powering via USB
(i.e. USB-serial not connected).

Notes:

  - sleep: `time.sleep()`
  - s-sleep ("slow sleep"): `cpu.frequency = 25000000; time.sleep()`
  - LS: light-sleep
  - DS: deep-sleep
  - TA: TimeAlarm
  - PA: PinAlarm

Sleep and slow-sleep are not strictly reproducible when running from
within a loop. There is a range of a few mA from iteration to
iteration, probably due to background activities.


Pico (RP2040)
-------------

| type    | 9.2.3  | 9.2.3-PR |
|---------|--------|----------|
| sleep   | 18.6mA | 18.6mA   |
| s-sleep |  7.7mA |  7.7mA   |
| LS+TA   | 15.0mA |  1.6mA   |
| LS+PA   | 15.0mA |  1.2mA   |
| DS+TA   |  7.1mA |  1.6mA   |
| DS+PA   |  1.3mA |  1.2mA   |


Pico-W (RP2040)
---------------

Test-Setups:

  - (a): `import wifi` and connected as documented
  - (b): wifi not imported
  - (A): `import wifi`, CYW43 shutdown, manual reconnect
  - (B): wifi not imported, CYW43 shutdown


| type    | 9.2.3(a)| 9.2.3(b)| 9.2.3-PR(a) | 9.2.3-PR(b)| 9.2.3-PR(A)| 9.2.3-PR(B)|
|---------|---------|---------|-------------|------------|------------|------------|
| sleep   | 63.2mA¹ | 27.3mA  | 63.0mA      | 27.2mA     | 63.2mA¹    | 27.5mA     |
| s-sleep | failed¹ |         | failed¹     |            |            |            |
| s-sleep | 23.2mA² | 13.5mA  | 23.2mA²     | 13.5mA     | 23.4mA²    | 13.6mA     |
| LS+TA   | 59.8mA¹ |         | failed¹     |            |            |            |
| LS+TA   | 29.4mA² | 22.1mA  | 21.4mA²     | 11.4mA     |  1.8mA³    |  1.8mA     |
| LS+PA   | 59.8mA¹ |         | failed¹     |            |            |            |
| LS+PA   | 29.7mA² | 22.1mA  | 21.0mA²     | 11.0mA     |  1.3mA³    |  1.3mA     |
| DS+TA   |  6.0mA  |  6.1mA  |  1.8mA      |  1.8mA     |  1.8mA     |  1.8mA     |
| DS+PA   |  1.4mA  |  1.4mA  |  1.3mA      |  1.3mA     |  1.3mA     |  1.3mA     |

¹ connected
² `wifi.radio.enabled=False`
³ reconnect from user-code necessary


(Pico2) RP2350A
---------------

- Light/Deep-Sleep is 1% shorter than requested (0:59.50 vs. 1:00)

| type    | 9.2.3  | 9.2.3-PR |
|---------|--------|----------|
| sleep   | 15.1mA | 13.2mA   |
| s-sleep |  5.7mA |  5.7mA   |
| LS+TA   | n.a.   |  1.7mA   |
| LS+PA   | n.a.   |  1.7mA   |
| DS+TA   | n.a.   |  1.7mA   |
| DS+PA   | n.a.   |  1.7mA   |


(Pico2-W) RP2350A
-----------------

Test-Setups:

  - (a): `import wifi` and connected as documented
  - (b): wifi not imported
  - (A): `import wifi`, CYW43 shutdown, manual reconnect
  - (B): wifi not imported, CYW43 shutdown

- Light/Deep-Sleep is 8% longer than requested (1:05 vs. 1:00)


| type    | 9.2.3(a)| 9.2.3(b)| 9.2.3-PR(a)| 9.2.3-PR(b)| 9.2.3-PR(A)| 9.2.3-PR(B)|
|---------|---------|---------|------------|------------|------------|------------|
| sleep   | 60.6mA¹ | 20.1mA  | 60.2mA¹    | 20.7mA     | 58.7mA¹    | 18.9mA     |
| s-sleep | failed¹ |         | failed¹    |            |            |            |
| s-sleep | 24.2mA² | 11.3mA  | 24.2mA²    | 11.3mA     | 24.2mA²    | 14.8mA     |
| LS+TA   |   n.a.  |         | failed¹    |            |            |            |
| LS+TA   |   n.a.  |   n.a.  | 21.3mA²    | 11.9mA     |  1.9mA³    |  1.9mA     |
| LS+PA   |   n.a.  |         | failed¹    |            |            |            |
| LS+PA   |   n.a.  |   n.a.  | 21.3mA²    | 11.9mA     |  1.9mA³    |  1.9mA     |
| DS+TA   |   n,a.  |   n.a.  |  1.9mA     |  1.8mA     |  1.9mA     |  1.9mA     |
| DS+PA   |   n.a.  |   n.a.  |  1.9mA     |  1.8mA     |  1.9mA     |  1.9mA     |

¹ connected
² `wifi.radio.enabled=False`
³ reconnect from user-code necessary



Pimoroni Pico Plus 2 (RP2350B)
------------------------------

- Light/Deep-Sleep is 25% longer than requested (1:15 vs. 1:00)


| type    | 9.2.3  | 9.2.3-PR    |
|---------|--------|-------------|
| sleep   |        | 15.2mA      |
| s-sleep |        |  5.6mA      |
| LS+TA   | n.a.   |  1.4mA      |
| LS+PA   | n.a.   |  1.4mA      |
| DS+TA   | n.a.   |  1.4mA      |
| DS+PA   | n.a.   |  1.4mA      |



Pimoroni Pico Plus 2W (RP2350B)
-------------------------------

Test-Setups:

  - (A): `import wifi`, CYW43 shutdown, manual reconnect
  - (B): wifi not imported, CYW43 shutdown

- Light/Deep-Sleep is 17% longer than requested (1:10 vs. 1:00)

| type    | 9.2.1  | 9.2.3-PR(A) | 9.2.3-PR(B) |
|---------|--------|-------------|-------------|
| sleep   |        |             |             |
| s-sleep |        |             |             |
| LS+TA   | n.a.   | 1.7mA       |             |
| LS+PA   | n.a.   |             |             |
| DS+TA   | n.a.   |             |             |
| DS+PA   | n.a.   |             |             |
