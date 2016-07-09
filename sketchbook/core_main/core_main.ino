//////
// core_main.ino, core_outputs.ino, core_serial.ino - RasPiO Duino Program for motor control, line following
//////

// Servo library & initialising head servos
#include <Servo.h>
Servo pan;
Servo tilt;
Servo ball_guide;
Servo paddle_release;

// kazillions of variables
const int master_enable = 2;
const int led_pin = 13;
const int left_motor_forward = 3;
const int left_motor_backward = 4;
const int left_motor_enable = 5;
const int right_motor_enable = 6;
const int right_motor_forward = 7;
const int right_motor_backward = 8;
const int pan_servo = 9;
const int tilt_servo = 10;
const int guide_servo = A2;
const int paddle_servo = A3;

const int loop_pause = 10; // Delay (ms) between: each loop cycle; jump to next stepped pwm value for left and right motor

int left_motor_value = 0;
int right_motor_value = 0;
int left_motor_aim = 0;
int right_motor_aim = 0;
int motor_calibration = 0; // Pi controls the motor calibration
boolean instantly_update_motors = false;

boolean launcher_connected = false;

int tilt_ms = 1200;
int pan_ms = 1430;
int guide_ms = 1500;
int paddle_ms = 1500;

boolean disabled = true;
boolean pi_ready = false;

// Pin to test battery voltage, scaled through a physical voltage divider
int battery_voltage_pin = A2;
int battery_voltage = 0;

const int ultrasonic_echo = 14; // A0
const int ultrasonic_trigger = 15; // A1
float distance_cm = 0;

int flash_time = 0;
int flash_delay = 30;

String command;

long start = 0;

void setup()
{
  Serial.begin(9600);
  command = String();
  for(int pin = 3; pin <= 8; pin++){pinMode(pin, OUTPUT);}
  pinMode(led_pin, OUTPUT);
  pinMode(ultrasonic_echo, INPUT);
  pinMode(ultrasonic_trigger, OUTPUT);
  pinMode(master_enable, INPUT);
  delay(500);
  if(digitalRead(master_enable)) // only do the nice flashing if the Duino is disabled. otherwise, hurry up by not flashing!
  {
    for(int i = 0; i <= 10; i++)
    {
      digitalWrite(led_pin, HIGH);
      delay(50);
      digitalWrite(led_pin, LOW);
      delay(50);
    }
  }
  Serial.print("DUINO-READY\r\n"); // Tell Pi the Duino ready to answer commands.
  while(digitalRead(master_enable)){delay(20);} // Wait until Pi sets Duino master enable pin to LOW (Duino enabled).
}

void loop()
{
  start = millis();
  if(!digitalRead(master_enable)) // Counter intuitive: LOW means enabled!
  {
    if(disabled) // Duino has not yet enabled everything. Happens once at the beginning of each period of Duino being enabled.
    {
      while(Serial.available() > 0){Serial.read();} // Clear all old buffer data that may have accumalated so we don't run out of date commands.
      pan.attach(pan_servo);
      pan.writeMicroseconds(pan_ms);
      tilt.attach(tilt_servo);
      tilt.writeMicroseconds(tilt_ms);
      digitalWrite(led_pin, HIGH);
      flash_time = 0;
      disabled = false;
    }
    get_commands(); // Get any commands sent by Duino and act on them.
    if(instantly_update_motors) // If get_commands() tells us to, set motor speeds to specified amount without ramping the motor enables. CAUTION: may create a voltage drop that resets Pi and Duino if used irresponsibly!
    {
      set_left_motor(left_motor_value);
      set_right_motor(right_motor_value);
      instantly_update_motors = false; // Only do it once
    }
    else // get_commands() tells us to use the standard (for this robot) motor ramping procedure.
    {
      step_left_motor_speed();
      step_right_motor_speed();
    }
    // This next line is for an interactive Duino LED- flash behaviour is different when Duino is enabled and disabled. Here (Duino enabled) the flash is a steady on/off.
    // The blink speed increases ($flash_delay decreases) when the Pi is backing up files to a plugged in USB drive.
    if(flash_time > flash_delay){digitalWrite(led_pin, !digitalRead(led_pin));flash_time = 0;}else{flash_time ++;} // toggle LED
  }
  else // Duino enable pin is HIGH- means Duino is disabled
  {
    while(Serial.available() > 0){Serial.read();} // clear any data that's accumalating.
    if(!disabled)
    {
      pan.detach();
      tilt.detach();
      digitalWrite(led_pin, LOW);
      flash_time = 0;
      disabled = true;
    }
    freeze_motors();
    // This next line is for an interactive Duino LED- flash behaviour is different when Duino is enabled and disabled. Here (Duino disabled) the flash is a brief blink then a long pause, so as to not be distracting.
    if(flash_time < 3){digitalWrite(led_pin, HIGH);flash_time ++;}else if(flash_time >= 500){flash_time = 0;}else{digitalWrite(led_pin, LOW);flash_time ++;}
  }
  delay(constrain((loop_pause - (millis() - start)), 0, loop_pause)); // Run the loop every $loop_pause milliseconds accurately. Calculate elapsed time since this loop run began and deduct from delay time. So hopefully (pseudocode) LOOP_RUN_TIME_IN_MS + THIS_ACTUAL_DELAY_IN_MS = $loop_pause
}
