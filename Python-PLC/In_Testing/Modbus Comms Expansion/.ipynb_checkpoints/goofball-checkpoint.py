import os
import time
sleep_time = 0.10
while True:
    os.system('mode con: cols=120 lines=40')
    os.system('color 01')
    print('GG WP')
    time.sleep(sleep_time)
    os.system('mode con: cols=40 lines=120')
    os.system('color 12')
    print('GG WP'*2)
    time.sleep(sleep_time)
    os.system('mode con: cols=120 lines=120')
    os.system('color 23')
    print('GG WP'*3)
    time.sleep(sleep_time)
    os.system('mode con: cols=100 lines=100')
    os.system('color 34')
    print('GG WP'*4)
    time.sleep(sleep_time/3)
    os.system('mode con: cols=80 lines=80')
    os.system('color 45')
    print('GG WP'*5)
    time.sleep(sleep_time/3)
    os.system('mode con: cols=60 lines=60')
    os.system('color 56')
    print('GG WP'*6)
    time.sleep(sleep_time/3)
    os.system('mode con: cols=80 lines=40')
    os.system('color 67')
    print('GG WP'*7)
    time.sleep(sleep_time/3)
    os.system('mode con: cols=120 lines=40')
    os.system('color 78')
    print('GG WP'*8)