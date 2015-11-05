################################################################################
# Copyright (C) 2012-2013 Leap Motion, Inc. All rights reserved.               #
# Leap Motion proprietary and confidential. Not for distribution.              #
# Use subject to the terms of the Leap Motion SDK Agreement available at       #
# https://developer.leapmotion.com/sdk_agreement, or another agreement         #
# between Leap Motion and you, your company or other organization.             #
################################################################################
import os, sys, thread, time, inspect
import struct, fcntl, termios, readline, time

sys.path.insert(0, "lib/")

import Leap, math
import Menu
from Menu import MenuItem
from time import sleep
from subprocess import Popen, PIPE
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture

lastSeen = 0
limits = {"x": 100, "y": 300, "z": 100}

menu =  MenuItem("Main Menu",
            MenuItem("Environment",
                MenuItem("Temperature",
                    65, 66, 67, 68, 69, 70
                ),
                MenuItem("Fan Speed",
                    1, 2, 3, 4, 5
                )
            ),
            MenuItem("Music",
                MenuItem("Radio",
                    "AM",
                    "FM"
                ),
                MenuItem("Volume",
                    1, 2, 3, 4, 5
                )
            ),
            MenuItem("Other Settings",
                MenuItem("Test One",
                    1, 2, 3, 4, 5, 6, 7, 8, 9
                )
            )
        )
currentMenu = menu
#print currentMenu.getCursor().data.getNodeNames()
#print menu.show()

def main():
    print "\n\n"
    # Create a sample listener and controller
    listener = SampleListener()
    controller = Leap.Controller()

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)

    # Keep this process running until Enter is pressed
    print "Press Enter to quit..."
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        # Remove the sample listener when done
        controller.remove_listener(listener)

class SampleListener(Leap.Listener):
    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
    state_names = ['STATE_INVALID', 'STATE_START', 'STATE_UPDATE', 'STATE_END']
    volumeController = 0;

    def on_init(self, controller):
        print "Initialized"

    def on_connect(self, controller):
        print "Connected"
        os.system('clear')

        # Enable gestures
        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE);
        controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE);

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "Disconnected"

    def on_exit(self, controller):
        print "Exited"

    def on_frame(self, controller):
        # Get the most recent frame and report some basic information
        global menu, currentMenu, lastSeen
        frame = controller.frame()

        if len(frame.hands) is 0:
            return

        hand = frame.hands[0]

        #check if hands haven't been seen in .5 seconds. if so, wait a bit
        m = int(round(time.time() * 1000))
        if m - lastSeen > 5000:
            currentMenu = menu
            os.system('clear')
            print currentMenu.getNodeNames()
            os.system('play --no-show-progress --null --channels 1 synth %s sine %f' % (.5, 300))
            sleep(.5)
            lastSeen = m
            return

        lastSeen = m
        normal = hand.palm_normal
        direction = hand.direction
        pitch = direction.pitch * Leap.RAD_TO_DEG
        roll = normal.roll * Leap.RAD_TO_DEG
        handType = "\033[31mLeft\033[0m " if hand.is_left else "\033[32mRight\033[0m"

        x = hand.palm_position[0]
        y = hand.palm_position[1]
        z = hand.palm_position[2]

        if abs(x) > limits["x"] or y > limits["y"] or abs(z) > limits["z"]:
            return

        if hand.grab_strength > .9:
            if type(currentMenu.getCursor().data) == MenuItem:
                currentMenu = currentMenu.getCursor().data
                print currentMenu.getNodeNames()
                speak = currentMenu.getCursor().data if not (type(currentMenu.getCursor().data) == MenuItem) else currentMenu.getCursor().data.getName()
                say(speak)
            else:
                deleteLine()
                say("Selected %s" % (currentMenu.getCursor().data))
                currentMenu = currentMenu.getParent()

            sleep(1)

        if hand.palm_velocity.x > 300:
            currentMenu.next()
            deleteLine()
            print currentMenu.getNodeNames()
            speak = currentMenu.getCursor().data if not (type(currentMenu.getCursor().data) == MenuItem) else currentMenu.getCursor().data.getName()
            say(speak)
            sleep(.5)

        if hand.palm_velocity.x < -300:
            currentMenu.prev()
            deleteLine()
            print currentMenu.getNodeNames()
            speak = currentMenu.getCursor().data if not (type(currentMenu.getCursor().data) == MenuItem) else currentMenu.getCursor().data.getName()
            say(speak)
            sleep(.5)

        if hand.palm_velocity.y > 300:
            if currentMenu.getParent() is None:
                return
            currentMenu = currentMenu.getParent()
            deleteLine()
            deleteLine()
            print currentMenu.getNodeNames()
            say(currentMenu.getCursor().data.getName())
            sleep(.5)

        def state_string(self, state):
            if state == Leap.Gesture.STATE_START:
                return "STATE_START"

            if state == Leap.Gesture.STATE_UPDATE:
                return "STATE_UPDATE"

            if state == Leap.Gesture.STATE_STOP:
                return "STATE_STOP"

            if state == Leap.Gesture.STATE_INVALID:
                return "STATE_INVALID"

def say(str):
    speed = 150
    pitch = 50
    os.system("echo \"%s\" | espeak -s %d -p %d" % (str, speed, pitch))

def deleteLine():
	# Next line said to be reasonably portable for various Unixes
	(rows,cols) = struct.unpack('hh', fcntl.ioctl(sys.stdout, termios.TIOCGWINSZ,'1234'))

	text_len = len(readline.get_line_buffer())+2

	# ANSI escape sequences (All VT100 except ESC[0G)
	sys.stdout.write('\x1b[1A')                         # Move cursor up
	sys.stdout.write('\x1b[0G')                         # Move to start of line
	sys.stdout.write('\x1b[2K')                         # Clear current line

if __name__ == "__main__":
    main()
