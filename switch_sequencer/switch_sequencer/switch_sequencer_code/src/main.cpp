#include <Arduino.h>
#include <Adafruit_NeoPixel.h>

#define MUX_D0_PIN 13
#define MUX_D1_PIN 14
#define MUX_D2_PIN 15

const int buttonPins[] = {12, 11, 10, 9, 19, 20, 21, 22, 16};
const int numButtons = sizeof(buttonPins) / sizeof(buttonPins[0]);
const unsigned long debounceDelay = 10; // Debounce time in milliseconds

PinStatus buttonStates[numButtons];          // Current state of each button
PinStatus lastButtonStates[numButtons];      // Previous state of each button
unsigned long lastDebounceTimes[numButtons]; // Timestamps for debounce

#define CLOCK_PIN 27
#define RESET_PIN 26

#define NEOPIXEL_PIN 17 // On Trinket or Gemma, suggest changing this to 1

#define NUMPIXELS 11

Adafruit_NeoPixel pixels(NUMPIXELS, NEOPIXEL_PIN, NEO_GRB + NEO_KHZ800);

#define DELAYVAL 50 // Time (in milliseconds) to pause between pixels

int8_t switch_state = 0;
#define SWITCH_COUNT 8

boolean modeButtonDown = false;

bool stepMask[8] = {true, true, true, true, true, true, true, true};

void set_switch_state()
{
  digitalWrite(MUX_D0_PIN, switch_state & 0x01);
  digitalWrite(MUX_D1_PIN, (switch_state & 0x02) >> 1);
  digitalWrite(MUX_D2_PIN, (switch_state & 0x04) >> 2);
}

bool clockHigh = false;
bool resetHigh = false;

void on_clock_change()
{
  Serial1.printf("Clock change \r\n");
  clockHigh = digitalRead(CLOCK_PIN) & HIGH == HIGH;
  if (clockHigh)
  {
    for (int i = 0; i < 8; i++)
    {
      switch_state++;
      if (switch_state >= SWITCH_COUNT)
      {
        switch_state = 0;
      }
      if (stepMask[switch_state])
      {
        break;
      }
    }
    set_switch_state();
  }
}

void on_reset_change()
{
  resetHigh = digitalRead(RESET_PIN) & HIGH == HIGH;
  Serial1.printf("Reset change %d\r\n", resetHigh);
  if (resetHigh)
  {
    switch_state = 0;
    set_switch_state();
  }
}

bool toggle = false;
void setup()
{
  Serial1.begin(115200);

  pinMode(MUX_D0_PIN, OUTPUT);
  pinMode(MUX_D1_PIN, OUTPUT);
  pinMode(MUX_D2_PIN, OUTPUT);

  pinMode(CLOCK_PIN, INPUT_PULLDOWN);
  clockHigh = digitalRead(CLOCK_PIN) & HIGH == HIGH;
  attachInterrupt(CLOCK_PIN, &on_clock_change, CHANGE);

  pinMode(RESET_PIN, INPUT_PULLDOWN);
  resetHigh = digitalRead(RESET_PIN) & HIGH == HIGH;
  attachInterrupt(RESET_PIN, &on_reset_change, CHANGE);

  set_switch_state();

  for (int i = 0; i < numButtons; i++)
  {
    pinMode(buttonPins[i], INPUT_PULLUP);
    buttonStates[i] = HIGH;
    lastButtonStates[i] = HIGH;
    lastDebounceTimes[i] = 0;
  }

  pixels.begin(); // INITIALIZE NeoPixel strip object (REQUIRED)
}

bool isButtonPressed(int pin)
{
  return digitalRead(pin) == HIGH;
}

int getActiveStepCount()
{
  int count = 0;
  for (int i = 0; i < 8; i++)
  {
    if (stepMask[i])
    {
      count++;
    }
  }
  return count;
}

void loop()
{
  for (int i = 0; i < numButtons; i++)
  {
    PinStatus reading = digitalRead(buttonPins[i]);
    if (reading != lastButtonStates[i])
    {
      Serial1.printf("Button %d: %d \r\n", i, reading);
      lastDebounceTimes[i] = millis();
    }

    if ((millis() - lastDebounceTimes[i]) > debounceDelay)
    {
      if (reading != buttonStates[i])
      {
        buttonStates[i] = reading;
        if (i < 8)
        {
          if (buttonStates[i] == LOW)
          {
            if (modeButtonDown)
            {
              if (getActiveStepCount() > 1)
              {
                stepMask[i] = !stepMask[i];
              }
            }
            else
            {
              switch_state = i;
              set_switch_state();
            }
          }
        }
        else if (buttonStates[i] == LOW)
        {
          modeButtonDown = true;
        }
        else
        {
          modeButtonDown = false;
        }
      }
    }
    lastButtonStates[i] = reading;
  }

  pixels.clear(); // Set all pixel colors to 'off'
  for (int i = 3; i < NUMPIXELS; i++)
  { // For each pixel...
    if (modeButtonDown)
    {
      if (stepMask[i - 3])
      {
        pixels.setPixelColor(i, pixels.Color(0x0f, 0x0f, 0x0f));
      }
      else
      {
        pixels.setPixelColor(i, pixels.Color(0x00, 0x00, 0x00));
      }
    }
    else
    {
      if (i == switch_state + 3)
      {
        pixels.setPixelColor(i, pixels.Color(0x0f, 0x0f, 0x0f));
      }
      else if (stepMask[i - 3])
      {
        pixels.setPixelColor(i, pixels.Color(0x02, 0x02, 0x02));
      }
      else
      {
        pixels.setPixelColor(i, pixels.Color(0x00, 0x00, 0x00));
      }
    }
  }
  if (modeButtonDown)
  {
    pixels.setPixelColor(0, pixels.Color(0x0f, 0x0f, 0x0f));
  }

  if (clockHigh)
  {
    pixels.setPixelColor(2, pixels.Color(0x0f, 0x0f, 0x0f));
  }
  if (resetHigh)
  {
    pixels.setPixelColor(1, pixels.Color(0x0f, 0x0f, 0x0f));
  }
  pixels.show(); // Send the updated pixel colors to the hardware.
  delay(1);
}