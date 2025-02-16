#include <stdio.h>
#include "pico/stdlib.h"
#include "hardware/pio.h"
#include "hardware/gpio.h"
#include "stdlib.h"
#include "ws2812.pio.h"

#define MUX_D0_PIN 13
#define MUX_D1_PIN 14
#define MUX_D2_PIN 15

#define BUTTON_1_PIN 12
#define BUTTON_2_PIN 11
#define BUTTON_3_PIN 10
#define BUTTON_4_PIN 9
#define BUTTON_5_PIN 19
#define BUTTON_6_PIN 20
#define BUTTON_7_PIN 21
#define BUTTON_8_PIN 22
#define BUTTON_9_PIN 16

#define CLOCK_PIN 27
#define RESET_PIN 26

#define WS2812_PIN 17

/**
 * NOTE:
 *  Take into consideration if your WS2812 is a RGB or RGBW variant.
 *
 *  If it is RGBW, you need to set IS_RGBW to true and provide 4 bytes per
 *  pixel (Red, Green, Blue, White) and use urgbw_u32().
 *
 *  If it is RGB, set IS_RGBW to false and provide 3 bytes per pixel (Red,
 *  Green, Blue) and use urgb_u32().
 *
 *  When RGBW is used with urgb_u32(), the White channel will be ignored (off).
 *
 */
#define IS_RGBW false
#define NUM_PIXELS 11

// Check the pin is compatible with the platform
#if WS2812_PIN >= NUM_BANK0_GPIOS
#error Attempting to use a pin>=32 on a platform that does not support it
#endif

static inline void put_pixel(PIO pio, uint sm, uint32_t pixel_grb)
{
    pio_sm_put_blocking(pio, sm, pixel_grb << 8u);
}

static inline uint32_t urgb_u32(uint8_t r, uint8_t g, uint8_t b)
{
    return ((uint32_t)(r) << 8) |
           ((uint32_t)(g) << 16) |
           (uint32_t)(b);
}

static inline uint32_t urgbw_u32(uint8_t r, uint8_t g, uint8_t b, uint8_t w)
{
    return ((uint32_t)(r) << 8) |
           ((uint32_t)(g) << 16) |
           ((uint32_t)(w) << 24) |
           (uint32_t)(b);
}

void pattern_snakes(PIO pio, uint sm, uint len, uint t)
{
    for (uint i = 0; i < len; ++i)
    {
        uint x = (i + (t >> 1)) % 64;
        if (x < 10)
            put_pixel(pio, sm, urgb_u32(0xff, 0, 0));
        else if (x >= 15 && x < 25)
            put_pixel(pio, sm, urgb_u32(0, 0xff, 0));
        else if (x >= 30 && x < 40)
            put_pixel(pio, sm, urgb_u32(0, 0, 0xff));
        else
            put_pixel(pio, sm, 0);
    }
}

void pattern_random(PIO pio, uint sm, uint len, uint t)
{
    if (t % 8)
        return;
    for (uint i = 0; i < len; ++i)
        put_pixel(pio, sm, rand());
}

void pattern_sparkle(PIO pio, uint sm, uint len, uint t)
{
    if (t % 8)
        return;
    for (uint i = 0; i < len; ++i)
        put_pixel(pio, sm, rand() % 16 ? 0 : 0xffffffff);
}

void pattern_greys(PIO pio, uint sm, uint len, uint t)
{
    uint max = 100; // let's not draw too much current!
    t %= max;
    for (uint i = 0; i < len; ++i)
    {
        put_pixel(pio, sm, t * 0x10101);
        if (++t >= max)
            t = 0;
    }
}

typedef void (*pattern)(PIO pio, uint sm, uint len, uint t);
const struct
{
    pattern pat;
    const char *name;
} pattern_table[] = {
    {pattern_snakes, "Snakes!"},
    {pattern_random, "Random data"},
    {pattern_sparkle, "Sparkles"},
    {pattern_greys, "Greys"},
};

/*Encoder GPIO*/
// GPIO 10 is Encoder phase A,
// GPIO 11 is Encoder phase B,
// GPIO 12 is the encoder push botton switch.
// change these as needed

int8_t switch_state = 0;
#define SWITCH_COUNT 8

#define ENC_A 10
#define ENC_B 11
#define ENC_SW 12

void set_switch_state()
{
    gpio_put(MUX_D0_PIN, switch_state & 0x01);
    gpio_put(MUX_D1_PIN, (switch_state & 0x02) >> 1);
    gpio_put(MUX_D2_PIN, (switch_state & 0x04) >> 2);
}

/* Encoder Callback*/
/*
        "LEVEL_LOW",  // 0x1
        "LEVEL_HIGH", // 0x2
        "EDGE_FALL",  // 0x4
        "EDGE_RISE"   // 0x8
*/
void encoder_callback(uint gpio, uint32_t events)
{

    uint32_t gpio_state = 0;

    gpio_state = (gpio_get_all() >> 10) & 0b0111; // get all GPIO them mask out all but bits 10, 11, 12
                                                  // This will need to change to match which GPIO pins are being used.

    static bool ccw_fall = 0; // bool used when falling edge is triggered
    static bool cw_fall = 0;

    uint8_t enc_value = 0;
    enc_value = (gpio_state & 0x03);

    if (gpio == ENC_A)
    {
        if ((!cw_fall) && (enc_value == 0b10)) // cw_fall is set to TRUE when phase A interrupt is triggered
            cw_fall = 1;

        if ((ccw_fall) && (enc_value == 0b00)) // if ccw_fall is already set to true from a previous B phase trigger, the ccw event will be triggered
        {
            cw_fall = 0;
            ccw_fall = 0;
            // do something here,  for now it is just printing out CW or CCW
            printf("CCW \r\n");
            switch_state--;
            if (switch_state < 0)
            {
                switch_state = SWITCH_COUNT - 1;
            }
        }
    }

    if (gpio == ENC_B)
    {
        if ((!ccw_fall) && (enc_value == 0b01)) // ccw leading edge is true
            ccw_fall = 1;

        if ((cw_fall) && (enc_value == 0b00)) // cw trigger
        {
            cw_fall = 0;
            ccw_fall = 0;
            // do something here,  for now it is just printing out CW or CCW
            printf("CW \r\n");

            switch_state++;
            if (switch_state >= SWITCH_COUNT)
            {
                switch_state = 0;
            }
        }
    }

    if (gpio == ENC_SW)
    {
        if (events == GPIO_IRQ_EDGE_FALL)
        {
            printf("SWITCH PRESSED \r\n");
            switch_state = 0;
        }
        else if (events == GPIO_IRQ_EDGE_RISE)
        {
            printf("SWITCH RELEASED \r\n");
        }
    }

    set_switch_state();

    printf("Switch State: %d \r\n", switch_state);
}

void on_pulse(uint gpio, uint32_t events)

{
    printf("Pulse \r\n");
    printf("gpio: %d \r\n", gpio);
    if (gpio == RESET_PIN)
    {
        printf("Reset \r\n");
        switch_state = 0;
        set_switch_state();
    }
    else if (gpio == CLOCK_PIN)
    {
        printf("Clock \r\n");
        switch_state++;
        if (switch_state >= SWITCH_COUNT)
        {
            switch_state = 0;
        }
        set_switch_state();
    }
}

//*************************************************************************************************************************************************
//*************************************************************************************************************************************************

int main()
{
    sleep_ms(500);
    stdio_init_all();
    printf("WS2812 Smoke Test, using pin %d\n", WS2812_PIN);

    // todo get free sm
    PIO pio;
    uint sm;
    uint offset;

    // This will find a free pio and state machine for our program and load it for us
    // We use pio_claim_free_sm_and_add_program_for_gpio_range (for_gpio_range variant)
    // so we will get a PIO instance suitable for addressing gpios >= 32 if needed and supported by the hardware
    bool success = pio_claim_free_sm_and_add_program_for_gpio_range(&ws2812_program, &pio, &sm, &offset, WS2812_PIN, 1, true);
    hard_assert(success);

    ws2812_program_init(pio, sm, offset, WS2812_PIN, 800000, IS_RGBW);

    // // GPIO Setup for Encoder
    // gpio_init(ENC_SW); // Initialise a GPIO for (enabled I/O and set func to GPIO_FUNC_SIO)
    // gpio_set_dir(ENC_SW, GPIO_IN);
    // gpio_pull_up(ENC_SW);

    // gpio_init(ENC_A);
    // gpio_set_dir(ENC_A, GPIO_IN);
    // gpio_disable_pulls(ENC_A);

    // gpio_init(ENC_B);
    // gpio_set_dir(ENC_B, GPIO_IN);
    // gpio_disable_pulls(ENC_B);

    // gpio_set_irq_enabled_with_callback(ENC_SW, GPIO_IRQ_EDGE_FALL | GPIO_IRQ_EDGE_RISE, true, &encoder_callback);
    // gpio_set_irq_enabled(ENC_A, GPIO_IRQ_EDGE_FALL, true);
    // gpio_set_irq_enabled(ENC_B, GPIO_IRQ_EDGE_FALL, true);

    gpio_init(MUX_D0_PIN);
    gpio_init(MUX_D1_PIN);
    gpio_init(MUX_D2_PIN);
    gpio_set_dir(MUX_D0_PIN, GPIO_OUT);
    gpio_set_dir(MUX_D1_PIN, GPIO_OUT);
    gpio_set_dir(MUX_D2_PIN, GPIO_OUT);

    gpio_init(CLOCK_PIN);
    gpio_set_dir(CLOCK_PIN, GPIO_IN);
    gpio_pull_down(CLOCK_PIN);
    gpio_set_irq_enabled_with_callback(CLOCK_PIN, GPIO_IRQ_EDGE_RISE, true, &on_pulse);

    gpio_init(RESET_PIN);
    gpio_set_dir(RESET_PIN, GPIO_IN);
    gpio_pull_down(RESET_PIN);
    gpio_set_irq_enabled(RESET_PIN, GPIO_IRQ_EDGE_RISE, true);
    // gpio_set_irq_enabled_with_callback(16, GPIO_IRQ_EDGE_RISE, true, &on_reset);

    set_switch_state();
    int count = 0;
    int t = 0;
    bool on = false;
    while (1)
    {
        // if (switch_state != t)
        // {
        //     t = switch_state;
        //     printf("Switch State: %d \r\n", switch_state);
        //     for (int i = 0; i < 8; ++i)
        //     {
        //         if (i == switch_state)
        //         {
        //             put_pixel(pio, sm, urgb_u32(0x0f, 0x0f, 0x0f));
        //         }
        //         else
        //         {
        //             put_pixel(pio, sm, 0);
        //         }
        //     }
        //     // pattern_table[t].pat(pio, sm, NUM_PIXELS, t);
        // }
        // int pat = rand() % count_of(pattern_table);
        // int dir = (rand() >> 30) & 1 ? 1 : -1;
        // puts(pattern_table[pat].name);
        // puts(dir == 1 ? "(forward)" : "(backward)");
        // for (int i = 0; i < 1000; ++i) {
        //     pattern_table[pat].pat(pio, sm, NUM_PIXELS, t);
        //     sleep_ms(10);
        //     t += dir;
        // }
        // count++;
        // if (count > 100)
        // {
        //     count = 0;
        //     on = !on;
        //     gpio_put(25, on);
        //     // if (on)
        //     // {
        //     //     switch_state = 0;
        //     // }
        //     // else
        //     // {
        //     //     switch_state = 1;
        //     // }
        //     // set_switch_state();
        // }
        // if (switch_state == 0)
        // {
        //     gpio_put(25, true);
        // }
        // else
        // {
        //     gpio_put(25, false);
        // }

        for (size_t i = 0; i < NUM_PIXELS; i++)
        {
            if (i == switch_state + 3)
            {
                put_pixel(pio, sm, urgb_u32(0x0f, 0x0f, 0x0f));
            }
            else
            {
                put_pixel(pio, sm, urgb_u32(0x00, 0x00, 0x00));
            }
      
        }
        // printf("Clock Pin State: %d \r\n", gpio_get(CLOCK_PIN));
        // t++;
        // if (t > 1)
        // {
        //     t = 0;
        //     switch_state++;
        //     if (switch_state >= SWITCH_COUNT)
        //     {
        //         switch_state = 0;
        //     }
        //     set_switch_state();
        // }
        sleep_ms(10);
    }
    // This will free resources and unload our program
    pio_remove_program_and_unclaim_sm(&ws2812_program, pio, sm, offset);
}