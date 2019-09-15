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
from homescreen import *



##### DIALING #####
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
    currentTimeMs = utime.ticks_ms()
    # debounce
    if(currentTimeMs - timeLastStart > 300 and currentTimeMs - timeLastPulse > 100):
        if(pinDialStart.value() == 1 and dialing == False):
            dialing = True
            lastDigit = -1
            timeLastStart = currentTimeMs
            print("Dial START:  /  " + str(currentTimeMs))
        elif (pinDialStart.value() == 0 and dialing == True and lastDigit >= 0):
            dialing = False
            lastDigit = lastDigit + 1
            if(lastDigit >= 10):
                lastDigit = lastDigit - 10
            currentNumber = currentNumber + str(lastDigit)
            timeLastStart = currentTimeMs
            print("Dial STOP:  /  " + str(currentTimeMs))
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


def updateDial(currentTimeMs):
    global timeLastStart, dialing, currentNumber, lastDigit
    if(currentTimeMs - timeLastStart > 300 and currentTimeMs - timeLastPulse > 200):
        if(pinDialStart.value() == 1 and dialing == False):
            dialing = True
            lastDigit = -1
            timeLastStart = currentTimeMs
            print("Dial START:  /  " + str(currentTimeMs))
        elif (pinDialStart.value() == 0 and dialing == True and lastDigit >= 0):
            dialing = False
            lastDigit = lastDigit + 1
            if(lastDigit >= 10):
                lastDigit = lastDigit - 10
            currentNumber = currentNumber + str(lastDigit)
            timeLastStart = currentTimeMs
            print("Dial STOP:  /  " + str(currentTimeMs))

    ugfx.text(5, 60, currentNumber, ugfx.RED)


##### RINGING #####
pinBellEnable = Pin(Pin.GPIO_ETHLED1, Pin.OUT)
pinBell = Pin(Pin.GPIO_ETHLED0, Pin.OUT)
timeLastBellMove = 0
timeLastFreqRefresh = 0
bellFreqHz = 70
ringBell = False


# it would be so much easier to do this witn PWM or a Timer callback !
# however the former is set on given pins and the latter doesn't work 
def updateBell(currentTimeMs):
    global ringBell, timeLastBellMove, pinBellEnable, pinBell, bellFreqHz
    if ringBell:
        pinBellEnable.on()
        if (currentTimeMs - timeLastBellMove > (1000 / bellFreqHz)):
            pinBell.value(not pinBell.value())
            timeLastBellMove = currentTimeMs
    else:
        pinBellEnable.off()

    global timeLastFreqRefresh
    # change the frequency and update display rarely
    if(currentTimeMs - timeLastFreqRefresh > 2000):
        if(bellFreqHz > 50):
            bellFreqHz = bellFreqHz - 40
        else:
            bellFreqHz = bellFreqHz + 40

        ugfx.area(150, 5, 90, 20, ugfx.WHITE)
        ugfx.text(150, 5, "Ring " + str(bellFreqHz) + "Hz" , ugfx.RED)
        timeLastFreqRefresh = currentTimeMs
    

# Change freq of ring
pinJoystickUp = Pin(Pin.GPIO_JOYU, Pin.IN) # PullUp, RisingEdge
pinJoystickDown = Pin(Pin.GPIO_JOYD, Pin.IN) # PullUp, RisingEdge       

def callbackJoystickUp(p):
    global bellFreqHz
    if(bellFreqHz < 80):
        bellFreqHz = bellFreqHz + 1

def callbackJoystickDown(p):
    global bellFreqHz
    if(bellFreqHz > 1):
        bellFreqHz = bellFreqHz - 1
    

# external interrupts from the Joystick
pinJoystickUp.irq(handler=callbackJoystickUp)
pinJoystickDown.irq(handler=callbackJoystickDown)



##### PHONE #####
sim800.poweron()
def updatePhone():
    global ringBell
    if sim800.isringing():
        ringBell = True
    else:
        ringBell = False



##### BATTERY INFO #####
timeLastBatteryRefresh = 0
def updateBattery(currentTimeMs):
    global timeLastBatteryRefresh
    if(currentTimeMs - timeLastBatteryRefresh > 10000):
        ugfx.area(5, 5, 140, 20, ugfx.GRAY)
        ugfx.text(5, 5, "Batt " + str(battery()) + "%" , ugfx.BLUE)
        timeLastBatteryRefresh = currentTimeMs



##### MAIN #####
# initialize screen
ugfx.init()
ugfx.clear()
ugfx.text(5, 30, "NUMBER", ugfx.BLACK)



# MAIN loop
while True:
    currentTimeMs = utime.ticks_ms()

    updateDial(currentTimeMs)

    updateBell(currentTimeMs)

    updatePhone()

    updateBattery(currentTimeMs)
    



# closing
ugfx.clear()
app.restart_to_default()
