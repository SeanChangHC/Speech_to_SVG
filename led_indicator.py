from gpiozero import RGBLED
from gpiozero.pins.lgpio import LGPIOFactory
from time import sleep
import threading

# Initialize the pin factory
factory = LGPIOFactory()

# Initialize the RGB LED with the specified pins (red 16, Green 20, Blue 21)
rgb_led = RGBLED(red=16, green=20, blue=21, pin_factory=factory)

# Create threading events to control LED states
recording_active = threading.Event()
processing_active = threading.Event()

# Thread objects for LED control
recording_thread = None
processing_thread = None

def _recording_blinker():
    """LED blinking function for recording state - runs in its own thread"""
    while recording_active.is_set():
        rgb_led.color = (1, 0, 0)  # Red on
        sleep(0.5)
        rgb_led.color = (0, 0, 0)  # Off
        sleep(0.5)

def _processing_blinker():
    """LED blinking function for processing state - runs in its own thread"""
    while processing_active.is_set():
        rgb_led.color = (0, 0, 1)  # Blue on
        sleep(0.5)
        rgb_led.color = (0, 0, 0)  # Off
        sleep(0.5)

def set_ready_to_record():
    """Set LED to green to indicate ready to record"""
    # Clear all active flags first
    recording_active.clear()
    processing_active.clear()
    
    # Wait for any threads to finish
    global recording_thread, processing_thread
    if recording_thread and recording_thread.is_alive():
        recording_thread.join(1.0)  # Wait for thread with timeout
    if processing_thread and processing_thread.is_alive():
        processing_thread.join(1.0)  # Wait for thread with timeout
        
    rgb_led.color = (0, 1, 0)  # Green

def set_recording():
    """Set LED to red to indicate recording in progress"""
    # Clear all active flags first and set recording flag
    processing_active.clear()
    recording_active.set()
    
    # Start the recording LED blinker in a separate thread
    global recording_thread
    recording_thread = threading.Thread(target=_recording_blinker)
    recording_thread.daemon = True  # Thread will die when main program exits
    recording_thread.start()

def set_processing():
    """Set LED to blue to indicate processing in progress"""
    # Clear all active flags first and set processing flag
    recording_active.clear()
    processing_active.set()
    
    # Start the processing LED blinker in a separate thread
    global processing_thread
    processing_thread = threading.Thread(target=_processing_blinker)
    processing_thread.daemon = True  # Thread will die when main program exits
    processing_thread.start()

def cleanup():
    """Turn off LED and release resources"""
    # Clear all active flags
    recording_active.clear()
    processing_active.clear()
    
    # Wait for threads to finish
    global recording_thread, processing_thread
    if recording_thread and recording_thread.is_alive():
        recording_thread.join(1.0)  # Wait with a timeout
    if processing_thread and processing_thread.is_alive():
        processing_thread.join(1.0)  # Wait with a timeout
        
    rgb_led.color = (0, 0, 0)  # Off
    rgb_led.close()

# Initial state is ready to record
set_ready_to_record() 