from gpiozero import Button, RGBLED
from gpiozero.pins.lgpio import LGPIOFactory
from time import sleep

# red 16, Green 20, Blue 21

# Set the pin factory to LGPIOFactory
factory = LGPIOFactory()

# Initialize the RGB LED with the specified pins
rgb_led = RGBLED(red=16, green=20, blue=21, pin_factory=factory)

def test_individual_colors():
    """Test each color of the RGB LED individually"""
    print("Testing Red...")
    rgb_led.red = 1  # Full red
    sleep(3)
    rgb_led.red = 0  # Off
    
    print("Testing Green...")
    rgb_led.green = 1  # Full green
    sleep(3)
    rgb_led.green = 0  # Off
    
    print("Testing Blue...")
    rgb_led.blue = 1  # Full blue
    sleep(3)
    rgb_led.blue = 0  # Off

def test_color_combinations():
    """Test various color combinations"""
    # Yellow (Red + Green)
    print("Testing Yellow (Red + Green)...")
    rgb_led.color = (1, 1, 0)
    sleep(3)
    
    # Purple (Red + Blue)
    print("Testing Purple (Red + Blue)...")
    rgb_led.color = (1, 0, 1)
    sleep(3)
    
    # Cyan (Green + Blue)
    print("Testing Cyan (Green + Blue)...")
    rgb_led.color = (0, 1, 1)
    sleep(3)
    
    # White (Red + Green + Blue)
    print("Testing White (Red + Green + Blue)...")
    rgb_led.color = (1, 1, 1)
    sleep(3)
    
    # Off
    rgb_led.color = (0, 0, 0)

def test_brightness_levels():
    """Test different brightness levels"""
    print("Testing brightness levels for Red...")
    for brightness in [0.2, 0.4, 0.6, 0.8, 1.0]:
        print(f"Brightness: {brightness}")
        rgb_led.red = brightness
        sleep(0.5)
    rgb_led.red = 0
    
    print("Testing brightness levels for all colors...")
    for brightness in [0.2, 0.4, 0.6, 0.8, 1.0]:
        print(f"Brightness: {brightness}")
        rgb_led.color = (brightness, brightness, brightness)
        sleep(0.5)
    rgb_led.color = (0, 0, 0)

def test_blinking():
    """Test blinking effect"""
    print("Testing blinking (Red)...")
    for _ in range(5):
        rgb_led.red = 1
        sleep(0.2)
        rgb_led.red = 0
        sleep(0.2)
    
    print("Testing blinking (All colors)...")
    for _ in range(5):
        rgb_led.color = (1, 1, 1)
        sleep(0.2)
        rgb_led.color = (0, 0, 0)
        sleep(0.2)

def cleanup():
    """Clean up and close the LED"""
    rgb_led.close()

if __name__ == "__main__":
    try:
        print("Starting LED test sequence...")
        test_individual_colors()
        test_color_combinations()
        test_brightness_levels()
        test_blinking()
        print("Test sequence completed!")
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    finally:
        cleanup()
        print("Cleaned up resources")