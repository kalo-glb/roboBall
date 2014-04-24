#define LeftForward   5
#define LeftBack      6
#define RightForward  10
#define RightBack     11

byte message[5] = {0, 0, 0, 0, 0};

#define RobotId      message[1]
#define ControlFlags message[2]
#define LMSpeed      message[3]
#define RMSpeed      message[4]

#define MessageLength sizeof(message)
#define ThisRobotId   (byte)65
#define StartByte     (byte)0x08

#define FSTOP     0x01
#define LMF       0x10
#define LMB       0x20
#define RMF       0x40
#define RMB       0x80

//#define KickDelay 300

void PositiveResponse(boolean type)
{
    byte response = (ThisRobotId - int('A')) << 6;
    response += (ControlFlags % 3) << 4;
    response += (LMSpeed + RMSpeed) % 16;
    
    if(false == type)
    {
        response = -ThisRobotId;
    }
    
    Serial.write(response);/*
    Serial.write(ControlFlags);
    Serial.write(LMSpeed);
    Serial.write(RMSpeed);*/
}

void setup()
{
    DDRD = 0;
    PORTD = 0;
    DDRB = 0;
    PORTB = 0;
      
    pinMode(LeftForward, OUTPUT);
    pinMode(LeftBack, OUTPUT);
    pinMode(RightForward, OUTPUT);
    pinMode(RightBack, OUTPUT);
      
    digitalWrite(LeftForward, LOW);
    digitalWrite(LeftBack, LOW);
    digitalWrite(RightForward, LOW);
    digitalWrite(RightBack, LOW);
      
    Serial.begin(115200);
}

void loop()
{
    if(Serial.available() >= MessageLength)
    {
        if(StartByte == Serial.read())
        {
            RobotId      = Serial.read();
            ControlFlags = Serial.read();
            LMSpeed      = Serial.read();
            RMSpeed      = Serial.read();
    
            if(ThisRobotId == RobotId)
            {
                if(0 == (ControlFlags & FSTOP))
                {
                    SetRobotSpeed();
                    PositiveResponse(true);
                }
                else
                {
                    FullStop();
                }
            }
        }
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

/*
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
*/

void FullStop()
{
    analogWrite(LeftForward,  0);
    analogWrite(LeftBack,     0);
    analogWrite(RightForward, 0);
    analogWrite(RightBack,    0);
}
