import signal
from gpiozero import Button
from gpiozero.pins.lgpio import LGPIOFactory
import led_indicator
import threading
import time

# Initialize the pin factory
factory = LGPIOFactory()

# Define the GPIO pin for the button (adjust as needed)
BUTTON_PIN = 17

# Initialize the button with pull-up resistor
button = Button(BUTTON_PIN, pull_up=True, pin_factory=factory)

# Current state tracking
current_state = "ready"  # States: ready, recording, processing
active_thread = None

def handle_button_press():
    """Handle button press by cycling through LED states"""
    global current_state, active_thread
    
    # If there's an active thread, it will automatically stop due to the event flags
    
    if current_state == "ready":
        # Change to recording state
        current_state = "recording"
        print("State changed to: RECORDING")
        active_thread = threading.Thread(target=led_indicator.set_recording)
        active_thread.daemon = True
        active_thread.start()
        
    elif current_state == "recording":
        # Change to processing state
        current_state = "processing"
        print("State changed to: PROCESSING")
        active_thread = threading.Thread(target=led_indicator.set_processing)
        active_thread.daemon = True
        active_thread.start()
        
    elif current_state == "processing":
        # Change back to ready state
        current_state = "ready"
        print("State changed to: READY")
        led_indicator.set_ready_to_record()

# Handler for clean exit
def signal_handler(sig, frame):
    print("Cleaning up...")
    led_indicator.cleanup()
    exit(0)

# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)

# Assign the button press event handler
button.when_pressed = handle_button_press

# Initial state
print("Button test started. Press the button to cycle through LED states.")
print("Press Ctrl+C to exit.")
print("Current state: READY")
led_indicator.set_ready_to_record()

# Keep the program running
try:
    signal.pause()
except KeyboardInterrupt:
    pass
finally:
    led_indicator.cleanup() 