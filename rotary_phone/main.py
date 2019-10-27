"""Rotary phone dialer"""

___title___        = "Rotary Phone Dialer"
___license___      = "MIT"
___dependencies___ = ["sleep", "app"]
___categories___   = ["EMF"]

import ugfx, utime, sim800
from machine import Pin
from homescreen import *





##### DIALING #####
dialing = False
calling = False
currentNumber = ""
lastDigit = -1


# for Rising/Falling see ti/boards/MSP_EXP432E401Y.c
pinDialStart = Pin(Pin.GPIO_JOYL, Pin.IN) # PullDown, BothEdges
pinDialPulse = Pin(Pin.GPIO_JOYR, Pin.IN) # PullUp, BothEdges
timeLastStart = utime.ticks_ms()
timeFirstPulse = utime.ticks_ms() 
timeLastPulse = utime.ticks_ms()   


def callbackDialPulse(p):
    global pinDialPulse, timeFirstPulse, timeLastPulse, dialing, lastDigit
    if(dialing and pinDialPulse.value() == 0):
        currentTime = utime.ticks_ms()
        if(lastDigit < 0):
            timeFirstPulse = currentTime
        # debounce
        if(currentTime - timeLastPulse > 40):
            lastDigit = lastDigit + 1
        timeLastPulse = currentTime
        
    
# empiric data, each range centered around mean/avg of empiric durations and is wider than 2 stdevs
# duration between the 1st pulse and the last
def digitByDuration(durationMs):
    if(durationMs < 20):
        return 1
    elif(durationMs < 105):
        return 2
    elif(durationMs < 200):
        return 3
    elif(durationMs < 280):
        return 4
    elif(durationMs < 375):
        return 5
    elif(durationMs < 460):
        return 6
    elif(durationMs < 535):
        return 7
    elif(durationMs < 625):
        return 8
    elif(durationMs < 695):
        return 9
    else:
        return 0



# external interrupts from the dialer
#pinDialStart.irq(handler=callbackDialStart)  # this is VERY NOISY, keeps getting triggered around pulses !
pinDialPulse.irq(handler=callbackDialPulse)

def updateDial(currentTimeMs):
    global timeFirstPulse, timeLastPulse, timeLastStart, dialing, currentNumber, lastDigit, hookStatus, calling
    if(currentTimeMs - timeLastStart > 300 and currentTimeMs - timeLastPulse > 200):
        if(pinDialStart.value() == 1 and dialing == False):
            dialing = True
            lastDigit = -1
            timeLastStart = currentTimeMs
        elif (pinDialStart.value() == 0 and dialing == True and lastDigit >= 0):
            dialing = False
            lastDigit = lastDigit + 1
            if(lastDigit >= 10):
                lastDigit = lastDigit - 10
            # check the digit
            digitDurationMs = timeLastPulse - timeFirstPulse
            durationBasedLastDigit = digitByDuration(digitDurationMs)
            # DURATION based digit is much more RELIABLE !  (all interrupts/callback code for not much... :) ) 
            currentNumber = currentNumber + str(durationBasedLastDigit)
            timeLastStart = currentTimeMs
            print("Dialled DIGIT: " + str(lastDigit))
            if(lastDigit != durationBasedLastDigit):
                print(" !!!! Digit mismatch. From duration: " + str(durationBasedLastDigit) + " / " + str(digitDurationMs) + "ms")

            print("# " + currentNumber)
            ugfx.area(5, 90, 120, 20, ugfx.WHITE)
            ugfx.text(5, 90, currentNumber, ugfx.RED)

    #returns 0=ready, 2=unknown, 3=ringing, 4=call in progress
    # after 3 secs from starting a number, take whatever we have and try dialing
    if ((not calling) and hookStatus and sim800.getstatus() == 0 and len(currentNumber) > 0 and currentTimeMs - timeLastStart > 3000):
        calling = True
        ugfx.area(120, 90, 240, 20, ugfx.WHITE)
        ugfx.text(120, 90, "Calling...", ugfx.RED)
        print("Calling... " + str(currentNumber))
        sim800.call(currentNumber)



##### RINGING #####
pinBellEnable = Pin(Pin.GPIO_ETHLED1, Pin.OUT)
pinBell = Pin(Pin.GPIO_ETHLED0, Pin.OUT)
timeLastBellMove = 0
timeLastFreqRefresh = 0
bellFreqHz1 = 60
bellFreqHz2 = 40
bellFreqHz = 0.1
ringBell = False
bellState = 0   # 0 - pause, 1 - ring freq1, 2 - ring freq2


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

    global bellState, timeLastFreqRefresh, bellFreqHz1, bellFreqHz2
    # change the frequency and update display rarely
    if(currentTimeMs - timeLastFreqRefresh > 1500):
        bellState = (bellState + 1) % 3
        if(bellState == 0):
            bellFreqHz = 0.1
        elif(bellState == 1):
            bellFreqHz = bellFreqHz1
        else:
            bellFreqHz = bellFreqHz2

        ugfx.area(150, 5, 90, 20, ugfx.WHITE)
        ugfx.text(150, 5, "Ring " + str(bellFreqHz) + "Hz" , ugfx.RED)
        timeLastFreqRefresh = currentTimeMs
    

# # Change freq of ring
# pinJoystickDown = Pin(Pin.GPIO_JOYD, Pin.IN) # PullDown, BothEdges       

# def callbackJoystickDown(p):
#     global bellFreqHz
#     if(bellFreqHz > 10):
#         bellFreqHz = bellFreqHz - 10
#     else:
#         bellFreqHz = 80

# # external interrupts from the Joystick
# pinJoystickDown.irq(handler=callbackJoystickDown)



##### PHONE #####
print("INIT PHONE START")

sim800.poweron()
sim800.btpoweron()

# Start the Bluetooth Headset IF necessary
if(not sim800.btconnected()):
    print("BT Headset not connected")
    pinBTHeadsetOnOff = Pin(Pin.GPIO_FET, Pin.OUT)
    pinBTHeadsetOnOff.off() # take that Pin DOWN same as if someone was pressing the power button on the headset
    utime.sleep(3)   #wait 3 secs for the BT Headset to start
    pinBTHeadsetOnOff.on() #that was all now

    sim800.btconnect(sim800.btPairedIdForName("S6"), 6)

print("INIT PHONE DONE")

def updatePhone():
    global ringBell, hookStatus, calling
    if sim800.isringing():
        ringBell = True
        if hookStatus:
            sim800.answer()
    else:
        ringBell = False
        # status == 4 means call in progress
        if ((not hookStatus) and (sim800.getstatus() == 4)):
            sim800.hangup()
            calling = False


##### General INFO : BATTERY & BT #####
timeLastInfoRefresh = 0
def updateGeneralInfo(currentTimeMs):
    global timeLastInfoRefresh, hookStatus
    if(currentTimeMs - timeLastInfoRefresh > 10000):
        ugfx.area(5, 5, 120, 20, ugfx.GRAY)
        ugfx.text(5, 5, "Batt " + str(battery()) + "%" , ugfx.WHITE)
        connBtDeviceNames = list(map(lambda e: e[1], sim800.btconnected()))
        ugfx.area(5, 30, 235, 20, ugfx.GRAY)
        ugfx.text(5, 30, "Bt Cn " + str(connBtDeviceNames), ugfx.WHITE)
        ugfx.text(120, 30, "Hk " + str(hookStatus), ugfx.WHITE)
        timeLastInfoRefresh = currentTimeMs
        


##### HOOK On/Off #####
pinHook = Pin(Pin.GPIO_JOYU, Pin.IN) # PullDown, BothEdges  
hookStatus = False
hookTimeLastToggle = 0
def updateHook(currentTimeMs):
    global hookStatus, hookTimeLastToggle, currentNumber
    if(currentTimeMs - hookTimeLastToggle > 100):
        newHookStatus = bool(pinHook.value())
        if(newHookStatus != hookStatus):
            hookStatus = newHookStatus
            
            currentNumber = ""  #reset number dialed
            ugfx.area(5, 90, 235, 20, ugfx.WHITE)

            hookTimeLastToggle = currentTimeMs
            print("Hook: " + str(hookStatus))
               



##### MAIN #####
# initialize screen
ugfx.init()
ugfx.clear()
ugfx.backlight(0)
ugfx.text(5, 60, "NUMBER", ugfx.BLACK)



# MAIN loop
while True:
    currentTimeMs = utime.ticks_ms()

    updateDial(currentTimeMs)

    updateBell(currentTimeMs)

    updatePhone()

    updateHook(currentTimeMs)
    
    updateGeneralInfo(currentTimeMs)

