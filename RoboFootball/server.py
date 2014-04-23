#!/usr/bin/python

import pygame
import Queue
from MessageManager import Message, MessageManager, Flags

pygame.init()


class RobotControl:
    joy_num = -1
    robot_id = -1
    joystick = 0
    controlData = {'forBack': 0, 'leftRight': 0}

    def __init__(self, joy_id, bot_id):
        self.joy_num = joy_id
        self.robot_id = bot_id
        try:
            self.joystick = pygame.joystick.Joystick(joy_id)
        except pygame.error:
            print "joystick with id: {} for robot: {} is not connected!".format(self.joy_num, self.robot_id)
            quit()
        self.joystick.init()

    @staticmethod
    def __translate(value, left_min=-1, left_max=1, right_min=-255, right_max=255):
        # Figure out how 'wide' each range is
        left_span = left_max - left_min
        right_span = right_max - right_min

        # Convert the left range into a 0-1 range (float)
        value_scaled = float(value - left_min) / float(left_span)

        # Convert the 0-1 range into a value in the right range.
        return abs(right_min + (value_scaled * right_span))

    def update_control(self):
        update_needed = False

        # first and third axes are left stick up/down and right stick left/right
        fb_control = self.joystick.get_axis(1)
        lr_control = self.joystick.get_axis(3)

        if fb_control != self.controlData['forBack']:
            self.controlData['forBack'] = fb_control
            update_needed = True

        if lr_control != self.controlData['leftRight']:
            self.controlData['leftRight'] = lr_control
            update_needed = True

        return update_needed

    def generate_message(self):
        # bitwise direction control flags

        message = Message(self.robot_id)

        # sets the robot control flags
        if self.controlData['forBack'] > 0:
            message.set_flag(Flags.LeftBack)
            message.set_flag(Flags.RightBack)
        else:
            message.set_flag(Flags.LeftForward)
            message.set_flag(Flags.RightForward)

        # third cell of the array is left motor speed
        # fourth cell of the array is right motor speed
        if self.controlData['leftRight'] > 0:
            left_speed = abs(self.__translate(self.controlData['forBack']))
            right_speed = abs(self.__translate(self.controlData['forBack'])) \
                - abs(self.__translate(self.controlData['leftRight']))
        else:
            left_speed = abs(self.__translate(self.controlData['forBack'])) \
                - abs(self.__translate(self.controlData['leftRight']))
            right_speed = abs(self.__translate(self.controlData['forBack']))

        if left_speed < 0:
            left_speed = 0

        if right_speed < 0:
            right_speed = 0

        message.set_left_speed(int(left_speed))
        message.set_right_speed(int(right_speed))

        return message


message_in_queue = Queue.LifoQueue()
messenger_thread = MessageManager(message_in_queue, '/dev/ttyACM0', 9600)

if __name__ == "__main__":
    messenger_thread.start()

    robots = [
        #RobotControl(1, 66),
        RobotControl(0, 65)
    ]

    while True:
        ev = pygame.event.wait()
        for r in robots:
            if r.update_control():
                message_in_queue.put(r.generate_message())