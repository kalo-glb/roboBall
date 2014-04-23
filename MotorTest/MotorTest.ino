byte MotorsArray[4] = {5, 11, 10, 6};

#define LeftForward   MotorsArray[0]
#define LeftBack      MotorsArray[1]
#define RightForward  MotorsArray[2]
#define RightBack     MotorsArray[3]

#define motorsOff() motorControll(LOW, LOW, LOW, LOW)

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
  
  motorsOff();
}

void loop()
{
  motorControll(HIGH, LOW, LOW, LOW);
  delay(3000);
  motorsOff();
  delay(1000);
  
  motorControll(LOW, HIGH, LOW, LOW);
  delay(3000);
  motorsOff();
  delay(1000);
  
  motorControll(LOW, LOW, HIGH, LOW);
  delay(3000);
  motorsOff();
  delay(1000);
  
  motorControll(LOW, LOW, LOW, HIGH);
  delay(3000);
  motorsOff();
  delay(1000);
}

void motorControll(byte dir1, byte dir2, byte dir3, byte dir4)
{
  digitalWrite(LeftForward, dir1);
  digitalWrite(LeftBack, dir2);
  digitalWrite(RightForward, dir3);
  digitalWrite(RightBack, dir4);
}
