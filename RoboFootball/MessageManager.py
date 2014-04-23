import serial
import threading
from enum import IntEnum
import time
import Queue


class DummySerial:
    written_messages = 0

    def __init__(self):
        pass

    def write(self, message):
        self.written_messages += 1
        DummySerial.write(message)

        print('\n')

    @staticmethod
    def write(message):
        for m in message:
            print ord(m)

    def read(self, count=1):
        self.written_messages -= 1
        return 'A'

    def inWaiting(self):
        return self.written_messages


class Flags(IntEnum):
    NoFlags = 0x00
    FullStop = 0x01
    LeftKick = 0x02
    RightKick = 0x04
    DoNotUse = 0x08
    LeftForward = 0x10
    LeftBack = 0x20
    RightForward = 0x40
    RightBack = 0x80


class Message:
    robot_id = 0
    control_flags = 0
    left_motor_speed = 0
    right_motor_speed = 0
    __start_byte = Flags.DoNotUse

    # control flag 1 is for full stop
    def __init__(self, robot_id=0, control_flag=Flags.NoFlags, left_motor_speed=0, right_motor_speed=0):
        self.set_id(robot_id)
        self.set_flag(control_flag)
        self.set_left_speed(left_motor_speed)
        self.set_right_speed(right_motor_speed)

    def __str__(self):
        string_message = ''\
            .join([
                chr(self.__start_byte),
                chr(self.robot_id),
                chr(self.control_flags),
                chr(self.left_motor_speed),
                chr(self.right_motor_speed)])

        return string_message

    def set_flag(self, flag=Flags.FullStop):
        if flag == self.__start_byte:
            raise ValueError("Do not use this flag. It is the communication protocol start byte")

        if flag not in Flags:
            raise TypeError("given flag {} is not supported".format(flag))
        else:
            if 0 == self.control_flags & flag:
                self.control_flags += flag

        if self.control_flags < 0 or self.control_flags > 255:
            raise Exception("flags have an illegal value: {} (negative or over 255)".format(self.control_flags))

    def clear_flag(self, flag):
        if flag not in Flags:
            raise TypeError("given flag {} is not supported".format(flag))
        else:
            if flag == self.control_flags & flag:
                self.control_flags -= flag

        if self.control_flags < 0 or self.control_flags > 255:
            raise Exception("flags have an illegal value: {} (negative or over 255)".format(self.control_flags))

    def set_left_speed(self, speed=0):
        if not isinstance(speed, int):
            raise ValueError("speed must be integer")

        if self.__start_byte == speed:
            speed = self.__start_byte + 1

        if 0 <= speed <= 255:
            self.left_motor_speed = speed
        else:
            raise ValueError("The speed must be between 0 and 255 inclusive. {} is not".format(speed))

    def set_right_speed(self, speed=0):
        if not isinstance(speed, int):
            raise ValueError("speed must be integer")

        if self.__start_byte == speed:
            speed = self.__start_byte + 1

        if 0 <= speed <= 255:
            self.right_motor_speed = speed
        else:
            raise ValueError("The speed must be between 0 and 255 inclusive. {} is not".format(speed))

    def set_id(self, robot_id):
        if ord('A') <= robot_id <= ord('Z'):
            self.robot_id = robot_id
        else:
            raise ValueError("Robot od must be the ASCII code of an english capital letter. Value given is: {}"
                             .format(robot_id))


class MessageWrapper:
    message = None
    robot_id = 0

    received_at = 0
    last_sent_at = 0
    message_resend_delay = 0.03  # 30 ms

    message_sent_successfully = False
    expected_response = 0

    def __init__(self, message):
        self.set_message(message)

    def set_message(self, message):
        if isinstance(message, Message):
            if message.robot_id != self.robot_id and 0 != self.robot_id:
                raise ValueError("This wrapper is used for a different robot with id: {} and not {}"
                                 .format(self.robot_id, message.robot_id))
            else:
                self.message = message
                self.robot_id = message.robot_id
                self.received_at = time.time()
                self.last_sent_at = 0
                self.message_sent_successfully = False
                self.expected_response = self._generate_expected_response()
        else:
            raise TypeError("The message for the message wrapper needs to be of class Message")

    def is_message_ready(self):
        current_time = time.time()
        result = False
        if not self.message_sent_successfully:
            if current_time > (self.last_sent_at + self.message_resend_delay):
                result = True

        return result

    def parse_message(self):
        return str(self.message)

    def receive_response(self, response):
        if response == self.expected_response:
            self.message_sent_successfully = True

    def force_send(self):
        self.message_sent_successfully = False
        self.last_sent_at = 0

    def _generate_expected_response(self):
        response = (self.message.robot_id - ord('A')) << 6
        response += (self.message.control_flags % 3) << 4
        response += (self.message.left_motor_speed + self.message.right_motor_speed) % 16

        return response



class MessageManager(threading.Thread):
    ser = serial.Serial()
    messages = dict()
    in_queue = Queue.LifoQueue()
    stoprequest = threading.Event()
    send_needed = dict()

    def __init__(self, in_queue, port_id='/dev/ttyACM0', baud_rate=9600):
        super(MessageManager, self).__init__()
        self.in_queue = in_queue
        self.stoprequest = threading.Event()
        try:
            self.ser = serial.Serial(port_id, baud_rate)
        except serial.serialutil.SerialException:
            print("Port at: {} with baud rate: {} cannot be opened".format(port_id, baud_rate))
            quit()

    def set_robot_message(self, message):
        if isinstance(message, Message):
            self.messages[message.robot_id] = str(message)
        else:
            raise TypeError("message must be of type Message")

    def run(self):
        while not self.stoprequest.isSet():
            # check for new data
            if not self.in_queue.empty():
                new_message = self.in_queue.get(False)
                self.set_robot_message(new_message)
                self.send_needed[new_message.robot_id] = True

            # send if new data or negative response
            for m in self.messages:
                if self.send_needed[m]:
                    self.ser.write(str(self.messages[m]))

            # check response
            if self.ser.inWaiting() > 0:
                response = ord(self.ser.read(1))
                if response in self.send_needed:
                    self.send_needed[response] = False

            #time.sleep(0.001)

    def join(self, timeout=None):
        self.ser.close()
        self.stoprequest.set()
        super(MessageManager, self).join(timeout)