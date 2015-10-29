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

import Leap, alsaaudio, math
from time import sleep
from subprocess import Popen, PIPE
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture

limiter = 15
mixer = alsaaudio.Mixer()
volume = int(mixer.getvolume()[0])
lastSeen = 0
threshold = 22
def main():
    print "\n\n\n\n\n\n"
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
        global mixer, volume, lastSeen
        frame = controller.frame()


        for hand in frame.hands:
            #check if hands haven't been seen in .5 seconds. if so, wait a bit
            m = int(round(time.time() * 1000))
            if m - lastSeen > 3000:
                sleep(.5)
                lastSeen = m
                break

            lastSeen = m
            normal = hand.palm_normal
            direction = hand.direction
            pitch = direction.pitch * Leap.RAD_TO_DEG
            roll = normal.roll * Leap.RAD_TO_DEG
            handType = "\033[31mLeft\033[0m " if hand.is_left else "\033[32mRight\033[0m"

            x = hand.palm_position[0]
            y = hand.palm_position[1]
            z = hand.palm_position[2]

            if hand.grab_strength > .9:
                media("pause")
                sleep(.5)

            if hand.palm_velocity.x > 500:
                media("next")
                sleep(1)

            if hand.palm_velocity.x < -500:
                media("prev")
                sleep(1)

            if abs(roll) > threshold:
                if self.volumeController == limiter:
                    delta = (1 if roll > threshold else -1) * (abs(int(roll)) - threshold) / 3.0
                    delta = math.ceil(delta) if roll > 0 else math.floor(delta)
                    delta = int(delta)
                    #print "%f" % delta
                    volume -= delta
                    volume = 0 if volume < 0 else volume
                    volume = 100 if volume > 100 else volume
                    mixer.setvolume(volume)
                    #print "Setting volume to %d (%d)" % (volume, -1 * delta)
                    self.volumeController = 0
                else:
                    self.volumeController += 1


        def state_string(self, state):
            if state == Leap.Gesture.STATE_START:
                return "STATE_START"

            if state == Leap.Gesture.STATE_UPDATE:
                return "STATE_UPDATE"

            if state == Leap.Gesture.STATE_STOP:
                return "STATE_STOP"

            if state == Leap.Gesture.STATE_INVALID:
                return "STATE_INVALID"

def media(cmd):
    if cmd is "pause":
        keyDown("Control_L")
        keyDown("Insert")
        keyUp("Insert")
        keyUp("Control_L")
    elif cmd is "next":
        keyDown("Control_L")
        keyDown("Prior")
        keyUp("Prior")
        keyUp("Control_L")
    elif cmd is "prev":
        keyDown("Control_L")
        keyDown("Home")
        keyUp("Home")
        keyUp("Control_L")

def keyDown(key):
    sequence = "keydown %s\n" % (key)
    p = Popen(['xte'], stdin = PIPE)
    p.communicate(input = sequence)

def keyUp(key):
    sequence = "keyup %s\n" % (key)
    p = Popen(['xte'], stdin = PIPE)
    p.communicate(input = sequence)

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
