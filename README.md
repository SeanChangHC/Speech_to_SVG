# LED and Button Test for Raspberry Pi

This project demonstrates how to use buttons and RGB LEDs on a Raspberry Pi to create a simple state machine.

## Hardware Requirements

- Raspberry Pi
- RGB LED (common cathode or common anode)
- Pushbutton
- Resistors (220-330Ω for LED, 10kΩ for button pull-up/down)
- Jumper wires

## Wiring

### RGB LED
- Red LED pin → GPIO 16 (via 220Ω resistor)
- Green LED pin → GPIO 20 (via 220Ω resistor)
- Blue LED pin → GPIO 21 (via 220Ω resistor)
- Common pin → GND (for common cathode) or 3.3V (for common anode)

### Button
- One pin → GPIO 17
- Other pin → GND (with 10kΩ pull-up resistor to 3.3V)

## Software Requirements

```
pip install gpiozero lgpio
```

## Files

- `led_indicator.py`: Controls the RGB LED and defines different state indicators
- `button_test.py`: Tests button functionality and cycles through LED states

## Usage

1. Connect the hardware as described above
2. Run the button test:

```
python button_test.py
```

3. Press the button to cycle through states:
   - Green (solid): Ready to record
   - Red (blinking): Recording
   - Blue (blinking): Processing

4. Press Ctrl+C to exit and clean up GPIO resources

## State Machine Logic

The button test implements a simple state machine:
- Initial state: Ready (green LED)
- First button press: Recording (blinking red LED)
- Second button press: Processing (blinking blue LED)
- Third button press: Back to Ready (green LED)

## Customization

You can modify the GPIO pin numbers in both scripts if you need to use different pins:
- In `led_indicator.py`: Change the RGB LED pin numbers
- In `button_test.py`: Change the button pin number 