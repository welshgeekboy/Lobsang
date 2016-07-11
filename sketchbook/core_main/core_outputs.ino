// Motor control functions

// Stop the motors immediately and reset the motor's aim speeds etc. to 0.
void freeze_motors()
{
  digitalWrite(left_motor_enable, LOW);
  digitalWrite(right_motor_enable, LOW);
  left_motor_value = 0;
  right_motor_value = 0;
  left_motor_aim = 0;
  right_motor_aim = 0;
}

// If motor's speed != motor's aim speed, increment or decrement the motor'r current speed to bring it one step closer to the aim speed.
void step_left_motor_speed()
{
  int pwm = 0;
  if(left_motor_aim != left_motor_value)
  {
    if(left_motor_aim > left_motor_value)
    {
      left_motor_value ++;
    }
    else if(left_motor_aim < left_motor_value)
    {
      left_motor_value --;
    }
    if(left_motor_value > 0)
    {
      pwm = constrain(left_motor_value * 16 + motor_calibration, 0, 255);
      analogWrite(left_motor_enable, pwm);
      digitalWrite(left_motor_forward, HIGH);
      digitalWrite(left_motor_backward, LOW);
    }
    else if(left_motor_value < 0)
    {
      pwm = constrain(left_motor_value * -16 + motor_calibration, 0, 255);
      analogWrite(left_motor_enable, pwm);
      digitalWrite(left_motor_forward, LOW);
      digitalWrite(left_motor_backward, HIGH);
    }
    else // $left_motor_value is 0. Remove calibration or else the motor will buzz
    {
      digitalWrite(left_motor_enable, LOW);
      digitalWrite(left_motor_forward, LOW);
      digitalWrite(left_motor_backward, LOW);
    }
  }
}

// If motor's speed != motor's aim speed, increment or decrement the motor'r current speed to bring it one step closer to the aim speed.
void step_right_motor_speed()
{
  int pwm = 0;
  if(right_motor_aim != right_motor_value)
  {
    if(right_motor_aim > right_motor_value)
    {
      right_motor_value ++;
    }
    else if(right_motor_aim < right_motor_value)
    {
      right_motor_value --;
    }
    if(right_motor_value > 0)
    {
      pwm = constrain(right_motor_value * 16 - motor_calibration, 0, 255);
      analogWrite(right_motor_enable, pwm);
      digitalWrite(right_motor_forward, HIGH);
      digitalWrite(right_motor_backward, LOW);
    }
    else if(right_motor_value < 0)
    {
      pwm = constrain(right_motor_value * -16 - motor_calibration, 0, 255);
      analogWrite(right_motor_enable, pwm);
      digitalWrite(right_motor_forward, LOW);
      digitalWrite(right_motor_backward, HIGH);
    }
    else // $right_motor_value is 0. Remove calibration or else the motor will buzz.
    {
      digitalWrite(right_motor_enable, LOW);
      digitalWrite(right_motor_forward, LOW);
      digitalWrite(right_motor_backward, LOW);
    }
  }
}

// Set the motor's speed to value $left_speed instantly.
void set_left_motor(int left_speed)
{
  int pwm = 0;
  left_motor_value = left_speed;
  left_motor_aim = left_speed;
  if(left_speed > 0)
  {
    pwm = constrain(left_speed * 16 + motor_calibration, 0, 255);
    analogWrite(left_motor_enable, pwm);
    digitalWrite(left_motor_forward, HIGH);
    digitalWrite(left_motor_backward, LOW);
  }
  else if(left_speed < 0)
  {
    pwm = constrain(left_speed * -16 + motor_calibration, 0, 255);
    analogWrite(left_motor_enable, pwm);
    digitalWrite(left_motor_forward, LOW);
    digitalWrite(left_motor_backward, HIGH);
  }
  else // $left_motor_value is 0. Remove calibration or else the motor will buzz.
  {
    digitalWrite(left_motor_enable, LOW);
    digitalWrite(left_motor_forward, LOW);
    digitalWrite(left_motor_backward, LOW);
  }
}

// Set the motor's speed to value $right_speed instantly.
void set_right_motor(int right_speed)
{
  int pwm = 0;
  right_motor_value = right_speed;
  right_motor_aim = right_speed;
  if(right_speed > 0)
  {
    pwm = constrain(right_speed * 16 - motor_calibration, 0, 255);
    analogWrite(right_motor_enable, pwm);
    digitalWrite(right_motor_forward, HIGH);
    digitalWrite(right_motor_backward, LOW);
  }
  else if(right_speed < 0)
  {
    pwm = constrain(right_speed * -16 - motor_calibration, 0, 255);
    analogWrite(right_motor_enable, pwm);
    digitalWrite(right_motor_forward, LOW);
    digitalWrite(right_motor_backward, HIGH);
  }
  else // $right_motor_value is 0. Remove calibration or else the motor will buzz.
  {
    digitalWrite(right_motor_enable, LOW);
    digitalWrite(right_motor_forward, LOW);
    digitalWrite(right_motor_backward, LOW);
  }
}


// Sensors

// Find and return the distance in cm to the nearest object from the ultrasonic sensor on the head within a ~15 degree angle from where the sensor is pointing.
float ultrasonic_distance()
{
  float cm = 0;
  long elapsed_us = 0;
  for(int i = 0; i <= 4; i ++) // Loop four times for mean averaging (gives more accuracy but ~3x slower).
  {
    digitalWrite(ultrasonic_trigger, LOW);
    delayMicroseconds(2);
    digitalWrite(ultrasonic_trigger, HIGH);
    delayMicroseconds(10);
    digitalWrite(ultrasonic_trigger, LOW);
    elapsed_us = pulseIn(ultrasonic_echo, HIGH);
    cm += elapsed_us / 58.77; // Convert microseconds to centimetres and halve distance all in one go.
  }
  cm /= 4; // Finish off the mean averaging.
  return cm;
}
