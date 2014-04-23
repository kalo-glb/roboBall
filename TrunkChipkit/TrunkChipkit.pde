byte MotorsArray[4] = {5, 6, 10, 9};

#define LeftForward   MotorsArray[0]
#define LeftBack      MotorsArray[1]
#define RightForward  MotorsArray[2]
#define RightBack     MotorsArray[3]

byte message[4] = {0, 0, 0, 0};

#define RobotId      message[0]
#define ControlFlags message[1]
#define LMSpeed      message[2]
#define RMSpeed      message[3]

#define MessageLength sizeof(message)
#define ThisRobotId   2

#define FSTOP     0x01
#define LEFTKICK  0x02
#define RIGHTKICK 0x04
#define LMF       0x10
#define LMB       0x20
#define RMF       0x40
#define RMB       0x80

#define KickDelay 300

void setup()
{
  pinMode(LeftForward, OUTPUT);
  pinMode(LeftBack, OUTPUT);
  pinMode(RightForward, OUTPUT);
  pinMode(RightBack, OUTPUT);
  
  digitalWrite(LeftForward, LOW);
  digitalWrite(LeftBack, LOW);
  digitalWrite(RightForward, LOW);
  digitalWrite(RightBack, LOW);
  
  Serial.begin(9600);
}

void loop()
{
    //Serial.println(Serial.available());
    if(Serial.available() == MessageLength)
    {
        RobotId      = Serial.read();
        ControlFlags = Serial.read();
        LMSpeed      = Serial.read();
        RMSpeed      = Serial.read();

        if(ThisRobotId == RobotId)
        {
            if(0 != (ControlFlags & LEFTKICK))
            {
                PerformLeftKick();
            }
            else if(0 != (ControlFlags & RIGHTKICK))
            {
                PerformRightKick();
            }
            else if(0 == (ControlFlags & FSTOP))
            {
                SetRobotSpeed();
            }
            else
            {
                FullStop();
                Serial.flush();
            }
        }
        else
        {
            Serial.flush();
        }
    }
    else if(Serial.available() > MessageLength)
    {
        // FullStop();
        Serial.flush();
    }
}

void SetRobotSpeed()
{
    if(ControlFlags & LMF)
    {
        analogWrite(LeftForward, LMSpeed);
        analogWrite(LeftBack, 0);
    }
    else if(ControlFlags & LMB)
    {
        analogWrite(LeftBack, LMSpeed);
        analogWrite(LeftForward, 0);
    }

    if(ControlFlags & RMF)
    {
        analogWrite(RightForward, RMSpeed);
        analogWrite(RightBack, 0);
    }
    else if(ControlFlags & RMB)
    {
        analogWrite(RightBack, RMSpeed);
        analogWrite(RightForward, 0);
    }
}

void PerformLeftKick()
{
    analogWrite(LeftForward, 255);
    analogWrite(LeftBack, 0);
    
    analogWrite(RightForward, 0);
    analogWrite(RightBack, 0);
    
    delay(KickDelay);
    
    analogWrite(LeftForward, 0);
    analogWrite(LeftBack, 255);
    
    delay(KickDelay);
    
    FullStop();
}

void PerformRightKick()
{
    analogWrite(LeftForward, 0);
    analogWrite(LeftBack, 0);
    
    analogWrite(RightForward, 255);
    analogWrite(RightBack, 0);
    
    delay(KickDelay);
    
    analogWrite(RightForward, 0);
    analogWrite(RightBack, 255);
    
    delay(KickDelay);
    
    FullStop();
}

void FullStop()
{
    analogWrite(LeftForward,  0);
    analogWrite(LeftBack,     0);
    analogWrite(RightForward, 0);
    analogWrite(RightBack,    0);
}
