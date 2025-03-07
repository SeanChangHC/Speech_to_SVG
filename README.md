# Pulley Plotter Final Project CSE237a
We design a fully functional speech to transcription flow using TinyML models and stepper motors to sketch the converted text.

This project also demonstrates how to use buttons and RGB LEDs on a Raspberry Pi to create a simple state machine.

## Hardware Requirements

- Raspberry Pi
- Arduino Mega2560 for Repetier FW
- NEMA17 stepper motors
- Servo Motor
- A4988 Stepper Motor Drivers
- RGB LED (common cathode or common anode)
- Pushbutton
- Resistors (220-330Ω for LED, 10kΩ for button pull-up/down)
- Jumper wires

## Wiring

### RGB LED
RPI5 Pins
- Red LED pin → GPIO 16 (via 220Ω resistor)
- Green LED pin → GPIO 20 (via 220Ω resistor)
- Blue LED pin → GPIO 21 (via 220Ω resistor)
- Common pin → GND (for common cathode) or 3.3V (for common anode)

### Arduino Pins
- Servo - D4
- Driver 1 Dir    - D60
- Driver 1 Step   - D61 
- Driver 1 Enable - D56
- Driver 2 Dir    - D36
- Driver 2 Step   - D34
- Driver 2 Enable - D30
- Hardware MS1, MS2, MS3 to 5V for 1/16th microstep resolution

### Button
- One pin → GPIO 17
- Other pin → GND (with 10kΩ pull-up resistor to 3.3V)


## Software Requirements

```
pip install gpiozero lgpioy
```

Install Processing software at processing.org/download

## Files

- `control.py`: main function python file for full flowy
- `led_indicator.py`: Controls the RGB LED and defines different state indicators
- `button_test.py`: Tests button functionality and cycles through LED states

## Usage
1. Connect the hardware as described above
2. Run the button test

```
python button_test.py
```

Test Processing program compatibility and motor hookup, either launching the GUI or running terminal cmd
```
./processing-java --sketch=/home/michaelc/PenPlotter-master/PenPlotter --run
```

Run the full main function
```
python control.py
```


3. Press the button to cycle through states:
   - Green (solid): Ready to record
   - Red (blinking): Recording
   - Blue (blinking): Processing

4. Press Ctrl+C to exit and clean up GPIO resources
y
## State Machine Logic

The button test implements a simple state machine:
- Initial state: Ready (green LED)
- First button press: Recording (blinking red LED)y
- Second button press: Processing (blinking blue LED)y
- Third button press: Back to Ready (green LED)

## Customization

You can modify the GPIO pin numbers in both scripts if you need to use different pins:
- In default.properties.txt: input variables of plotter assembly i.e. motor vertical distance, horizontal distance, pixel size, etc.
- In `led_indicator.py`: Change the RGB LED pin numbers
- In `button_test.py`: Change the button pin number
