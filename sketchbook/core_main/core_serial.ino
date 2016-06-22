void get_commands()
{
  if(Serial.available() > 0)
  {
    boolean possible_command_error = false;
    boolean command_error = false;
    int thousands = 0;
    int hundreds = 0;
    int tens = 0;
    int units = 0;
    int command_length = 0;
    command = "";
GET_MORE_DATA:// 'goto' to here to read any extra data that may have accumulated, if the current command appears to have not been read fully or if there is more data to read when the program gets to the bottom of this function.
    while(Serial.available() > 0)
    {
      possible_command_error = false;
      command += char(Serial.read());
    }
NEW_COMMAND: // If $command is more than one command in the same string eg "TS1200LMS29" then cycle through each command by going back to here and acting on the next command in $command
    if(command.startsWith("OK?")) // Pi poked the Duino to see if it's functioning properly.
    {
      Serial.print("DUINO-OK\r\n"); // Send an 'OK' reply through serial to the Pi.
      command_length = 3;
    }
    else if(command.startsWith("LMR")) // LMR == Left Motor 'Stepped' Ramped' to value specified, from previous value.
    {
      if(command.length() >= 5)
      {
        tens = int(command.charAt(3)) - 48; // Minus 48, as ASCII number values are N+48.
        units = int(command.charAt(4)) - 48;
        left_motor_aim = constrain(tens * 10 + units - 16, -16, 16);
        command_length = 5;
      }
      else // Error handling: Duino half-read command then started trying to handle it. Go back and re-check serial buffer for new data.
      {
        delay(15);
        goto GET_MORE_DATA;
      }
    }
    else if(command.startsWith("RMR")) // RMR == 'Right Motor Ramped' to value specified from previous value.
    {
      if(command.length() >= 5)
      {
        tens = int(command.charAt(3)) - 48;
        units = int(command.charAt(4)) - 48;
        right_motor_aim = constrain(tens * 10 + units - 16, -16, 16);
        command_length = 5;
      }
      else
      {
        delay(15);
        goto GET_MORE_DATA;
      }
    }
    else if(command.startsWith("BMR")) // BMR == 'Both Motors Ramped' to value specified from previous value.
    {
      if(command.length() >= 5)
      {
        tens = int(command.charAt(3)) - 48;
        units = int(command.charAt(4)) - 48;
        left_motor_aim = constrain(tens * 10 + units - 16, -16, 16);
        right_motor_aim = left_motor_aim;
        command_length = 5;
      }
      else
      {
        delay(15);
        goto GET_MORE_DATA;
      }
    }
    else if(command.startsWith("LMI")) // LMI == 'Left Motor Instantly' set to value specified.
    {
      if(command.length() >= 5)
      {
        tens = int(command.charAt(3)) - 48;
        units = int(command.charAt(4)) - 48;
        left_motor_aim = constrain(tens * 10 + units - 16, -16, 16);
        left_motor_value = left_motor_aim;
        instantly_update_motors = true;
        command_length = 5;
      }
      else
      {
        delay(15);
        goto GET_MORE_DATA;
      }
    }
    else if(command.startsWith("RMI")) // RMI == 'Right Motor Instantly' set to value specified.
    {
      if(command.length() >= 5)
      {
        tens = int(command.charAt(3)) - 48;
        units = int(command.charAt(4)) - 48;
        right_motor_aim = constrain(tens * 10 + units - 16, -16, 16);
        right_motor_value = right_motor_aim;
        instantly_update_motors = true;
        command_length = 5;
      }
      else
      {
        delay(15);
        goto GET_MORE_DATA;
      }
    }
    else if(command.startsWith("BMI")) // BMI == 'Both Motors Instantly' set to value specified.
    {
      if(command.length() >= 5)
      {
        tens = int(command.charAt(3)) - 48;
        units = int(command.charAt(4)) - 48;
        left_motor_aim = constrain(tens * 10 + units - 16, -16, 16);
        right_motor_aim = left_motor_aim;
        left_motor_value = left_motor_aim;
        right_motor_value = right_motor_aim;
        instantly_update_motors = true;
        command_length = 5;
      }
      else
      {
        delay(15);
        goto GET_MORE_DATA;
      }
    }
    else if(command.startsWith("PS")) // PS == set 'Pan Servo' angle with a 1000 to 2000 ms pulse.
    {
      if(command.length() >= 6)
      {
        thousands = int(command.charAt(2)) - 48;
        hundreds = int(command.charAt(3)) - 48;
        tens = int(command.charAt(4)) - 48;
        units = int(command.charAt(5)) - 48;
        pan_ms = constrain(thousands * 1000 + hundreds * 100 + tens * 10 + units, 1000, 2000);
        pan.writeMicroseconds(pan_ms);
        command_length = 6;
      }
      else
      {
        delay(15);
        goto GET_MORE_DATA;
      }
    }
    else if(command.startsWith("TS")) // TS == set 'Tilt Servo' angle with a 1000 to 2000 ms pulse.
    {
      if(command.length() >= 6)
      {
        thousands = int(command.charAt(2)) - 48;
        hundreds = int(command.charAt(3)) - 48;
        tens = int(command.charAt(4)) - 48;
        units = int(command.charAt(5)) - 48;
        tilt_ms = constrain(thousands * 1000 + hundreds * 100 + tens * 10 + units, 1000, 2000);
        tilt.writeMicroseconds(tilt_ms);
        command_length = 6;
      }
      else
      {
        delay(15);
        goto GET_MORE_DATA;
      }
    }
    else if (command.startsWith("LAC")) // Set whether the 'LAuncher is Connected' or not. (Dis)connects hardware.
    {
      if(command.length() >= 4)
      {
        units = int(command.charAt(3)) - 48;
        if(units == 1)
        {
          paddle_release.attach(paddle_servo);
          ball_guide.attach(guide_servo);
          launcher_connected = true;
        }
        else
        {
          paddle_release.detach();
          ball_guide.detach();
          launcher_connected = false;
        }
        command_length = 4;
      }
      else
      {
        delay(15);
        goto GET_MORE_DATA;
      }
    }
    else if(command.startsWith("LAP")) // Set the 'LAuncher Paddle' servo to specified ms angle.
    {
      if(command.length() >= 7)
      {
        thousands = int(command.charAt(3)) - 48;
        hundreds = int(command.charAt(4)) - 48;
        tens = int(command.charAt(5)) - 48;
        units = int(command.charAt(6)) - 48;
        paddle_ms = constrain(thousands * 1000 + hundreds * 100 + tens * 10 + units, 1000, 2000);
        paddle_release.writeMicroseconds(paddle_ms);
        command_length = 7;
      }
      else
      {
        delay(15);
        goto GET_MORE_DATA;
      }
    }
    else if(command.startsWith("LAG")) // Set the 'LAuncher ball Guide' servo to specified ms angle.
    {
      if(command.length() >= 7)
      {
        thousands = int(command.charAt(3)) - 48;
        hundreds = int(command.charAt(4)) - 48;
        tens = int(command.charAt(5)) - 48;
        units = int(command.charAt(6)) - 48;
        guide_ms = constrain(thousands * 1000 + hundreds * 100 + tens * 10 + units, 1000, 2000);
        ball_guide.writeMicroseconds(guide_ms);
        command_length = 7;
      }
      else
      {
        delay(15);
        goto GET_MORE_DATA;
      }
    }
    else if(command.startsWith("CAL")) // Pi specified the motor speed 'CALibration' for left and right motors. +CAL is added to right motor, -CAL is added to left motor.
    {
      if(command.length() >= 5)
      {
        tens = int(command.charAt(3)) - 48;
        units = int(command.charAt(4))- 48;
        motor_calibration = constrain((tens * 10) + units, 0, 98); // The max amount for a 2 digit number is 99, but constrain to 98 for a round number to halve.
        motor_calibration -= 46; // Create a (-/+) number out of a (+) number, and halve the number's range ((-46 to 46) instead of (0 to 98)).
        command_length = 5;
      }
      else
      {
        delay(15);
        goto GET_MORE_DATA;
      }
    }
    else if(command.startsWith("US?")) // US == Pi asked for 'Ultrasonic Sensor' proximity data (returns value in cm).
    {
      distance_cm = ultrasonic_distance();
      Serial.print("US");
      Serial.print(distance_cm);
      Serial.print("\r\n");
      command_length = 3;
    }
    else if(command.startsWith("BV?")) // BV == Pi asked for 'Battery Voltage' to see if voltage is still safe.
    {
      battery_voltage = analogRead(A0); // TODO: calculate proper voltage
      Serial.print("BV");
      Serial.print(battery_voltage);
      Serial.print("\r\n");
      command_length = 3;
    }
    else if(command.startsWith("SHUTDOWN")) // The Pi has said it is shutting down. The Duino LED will go out when it is safe to switch off the power.
    {
      pan.detach();
      tilt.detach();
      freeze_motors();
      digitalWrite(13, HIGH);
      delay(12000);
      digitalWrite(13, LOW);
      command_length = 8;
      while(true){delay(1000);} // Duino stays in this loop until switched off.
    }
    else // Error handling: command is none of the above. First re-check serial buffer, if there is no new data then tell the Pi there's a problem, and give it the bad command.
    {
      if(!possible_command_error)
      {
        possible_command_error = true;
        delay(15);
        goto GET_MORE_DATA;
      }
      else // There is no new data to make a complete command. Pi sent an incoherent message.
      {
        Serial.print("ERROR:["+ command +"]\r\n"); // Tell the Pi that the message did not make sense, and print what was received.
        while(Serial.available() > 0){Serial.read();} // Remove any old buffer data
        command_error = true;
        command = "";
        command_length = 0;
        possible_command_error = false;
      }
    }
    if(command.length() > command_length && !command_error)
    {
      command = command.substring(command_length); // Remove the old command (that has just been acted on) and re-run this function from NEW_COMMAND for the new command.
      command_length = 0;
      goto NEW_COMMAND;
    }
    // Re-check for serial data. Theory is that it makes the motors move
    // in sync always instead of sometimes having a slight delay between
    // each one changing. I'm not sure if the theory is correct though.
    if(Serial.available() > 0)
    {
      goto GET_MORE_DATA;
    }
  }
}
