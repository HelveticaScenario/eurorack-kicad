#include <Arduino.h>
#include <Adafruit_NeoPixel.h>

#define NEOPIXEL_PIN 17 // On Trinket or Gemma, suggest changing this to 1
#define CLOCK_PIN 27

#define NUMPIXELS 11

Adafruit_NeoPixel pixels(NUMPIXELS, NEOPIXEL_PIN, NEO_GRB + NEO_KHZ800);

#define DELAYVAL 50 // Time (in milliseconds) to pause between pixels

bool toggle = false;
void setup()
{
  pinMode(CLOCK_PIN, INPUT_PULLDOWN);
  attachInterrupt(CLOCK_PIN, []()
                  { toggle = !toggle; }, RISING);

  pixels.begin(); // INITIALIZE NeoPixel strip object (REQUIRED)
}

void loop()
{
  pixels.clear(); // Set all pixel colors to 'off'

  // The first NeoPixel in a strand is #0, second is 1, all the way up
  // to the count of pixels minus one.
  for (int i = 0; i < NUMPIXELS; i++)
  { // For each pixel...

    // pixels.Color() takes RGB values, from 0,0,0 up to 255,255,255
    // Here we're using a moderately bright green color:
    pixels.setPixelColor(i, pixels.Color(0, toggle ? 20 : 0, 0));

    pixels.show(); // Send the updated pixel colors to the hardware.

    // delay(DELAYVAL); // Pause before next pass through loop
  }
  delay(1);
}