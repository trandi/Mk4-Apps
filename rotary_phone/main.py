"""Rotary phone dialer"""

___title___        = "Rotary Phone Dialer"
___license___      = "MIT"
___dependencies___ = ["sleep", "app"]
___categories___   = ["EMF"]

import ugfx, sleep, app, sim800
from app import *
from dialogs import *
import ugfx
import ugfx_helper
from machine import Pin
import utime


#sim800.poweron()

dialing = False
currentNumber = ""
lastDigit = -1


# for Rising/Falling see ti/boards/MSP_EXP432E401Y.c
pinDialStart = Pin(Pin.GPIO_JOYL, Pin.IN) # PullDown, BothEdges
pinDialPulse = Pin(Pin.GPIO_JOYR, Pin.IN) # PullUp, BothEdges
timeLastStart = utime.ticks_ms()
timeLastPulse = utime.ticks_ms()

'''
def callbackDialStart(p):
    global pinDialStart, timeLastStart, timeLastPulse, dialing, currentNumber, lastDigit
    currentTime = utime.ticks_ms()
    # debounce
    if(currentTime - timeLastStart > 300 and currentTime - timeLastPulse > 100):
        if(pinDialStart.value() == 1 and dialing == False):
            dialing = True
            lastDigit = -1
            timeLastStart = currentTime
            print("Dial START:  /  " + str(currentTime))
        elif (pinDialStart.value() == 0 and dialing == True and lastDigit >= 0):
            dialing = False
            lastDigit = lastDigit + 1
            if(lastDigit >= 10):
                lastDigit = lastDigit - 10
            currentNumber = currentNumber + str(lastDigit)
            timeLastStart = currentTime
            print("Dial STOP:  /  " + str(currentTime))
'''        
    


def callbackDialPulse(p):
    global pinDialPulse, timeLastPulse, dialing, lastDigit
    if(dialing and pinDialPulse.value() == 0):
        currentTime = utime.ticks_ms()
        print("Pulse: " + str(currentTime))
        # debounce
        if(currentTime - timeLastPulse > 40):
            lastDigit = lastDigit + 1
        timeLastPulse = currentTime
    

# external interrupts from the dialer
#pinDialStart.irq(handler=callbackDialStart)  # this is VERY NOISY, keeps getting triggered around pulses !
pinDialPulse.irq(handler=callbackDialPulse)



#pBell = Pin(Pin.GPIO_FET)
#pBell.on()  # takes it to GND (whereas off() takes it to 3.3V)


# initialize screen
ugfx.init()
ugfx.clear()
# show text
ugfx.text(5, 5, "NUMBER", ugfx.BLACK)

# MAIN loop
while True:
    currentTime = utime.ticks_ms()

    if(currentTime - timeLastStart > 300 and currentTime - timeLastPulse > 200):
        if(pinDialStart.value() == 1 and dialing == False):
            dialing = True
            lastDigit = -1
            timeLastStart = currentTime
            print("Dial START:  /  " + str(currentTime))
        elif (pinDialStart.value() == 0 and dialing == True and lastDigit >= 0):
            dialing = False
            lastDigit = lastDigit + 1
            if(lastDigit >= 10):
                lastDigit = lastDigit - 10
            currentNumber = currentNumber + str(lastDigit)
            timeLastStart = currentTime
            print("Dial STOP:  /  " + str(currentTime))

    ugfx.text(5, 20, currentNumber, ugfx.RED)
    #utime.sleep_ms(100)


# closing
ugfx.clear()
app.restart_to_default()
