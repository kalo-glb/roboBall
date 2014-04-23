        kick_left = self.joystick.get_button(4)  # l1
        kick_right = self.joystick.get_button(4)  # r1

        if kick_left and self.controlData['kikState'] != 'LeftKick':
            self.controlData['kikState'] = 'LeftKick'
            self.controlData['kickUpdate'] = True
            update_needed = True
        elif kick_right and self.controlData['kikState'] != 'RightKick':
            self.controlData['kikState'] = 'RightKick'
            self.controlData['kickUpdate'] = True
            update_needed = True