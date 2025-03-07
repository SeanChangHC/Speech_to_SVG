import subprocess
import os
import time
import threading

# Import the necessary libraries
from gpiozero import Button
from gpiozero.pins.lgpio import LGPIOFactory

# Import the record_audio function from record.py
from record import record_audio

# Import the necessary functions from revise.py for transcript revision
from revise import correct_and_rephrase, save_transcript

# Import the necessary functions from txt_svg module
from txt_svg.tsvg import sentence_to_path, Face
from svgpathtools import wsvg
from freetype import Face
from noise import reduce_noise_in_audio  # Import the noise reduction function

# Import LED indicator functions
from led_indicator import set_ready_to_record, set_recording, set_processing, cleanup

# Create a pin factory using lgpio
pin_factory = LGPIOFactory()

# Create a button connected to GPIO pin 17 using the lgpio factory
button = Button(17, pin_factory=pin_factory)

# Global variables to track recording state
recording = False
recording_thread = None
stop_recording_flag = threading.Event()
latest_filename = None
recordings_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recordings")
# Fixed SVG output filename
svg_output_filename = "output.svg"

# Ensure recordings directory exists
os.makedirs(recordings_dir, exist_ok=True)

# Create and set up the font face
font_face = Face('./txt_svg/PrettyNeat.ttf')
font_face.set_char_size(20 * 28)  # Font size similar to the tsvg.py example

def convert_text_to_svg(text_content, output_filename=None):
    """
    Convert the transcription text string to an SVG path and save it
    
    Args:
        text_content: The text content to convert (string)
        output_filename: Optional filename to save the SVG to. If None, a filename will be generated.
    """
    print("Converting transcription to SVG")
    try:
        # Clean up the text if needed
        clean_text = text_content.strip()
        
        # Generate the SVG path
        svg_path = sentence_to_path(font_face, clean_text, 
                                   char_spacing=40, 
                                   word_spacing=200, 
                                   max_width=8000, 
                                   line_spacing=1000)
        
        # If output filename is provided, save the SVG file
        if output_filename:
            # Save the SVG file
            wsvg(svg_path, filename=output_filename)
            print(f"SVG visualization saved to {output_filename}")
        
        return svg_path
        
    except Exception as e:
        print(f"Error converting text to SVG: {str(e)}")
        return None

def transcribe_audio(filename):
    """
    Transcribe the recorded audio file using whisper.cpp and convert to SVG directly
    without saving intermediate text files
    """
    print(f"Transcribing {filename}...")
    try:
        process = subprocess.Popen(
            ["./whisper.cpp/build/bin/whisper-cli", "-f", filename, "-m", "./whisper.cpp/models/ggml-tiny.en.bin", "-nt", "-np"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        
        if process.returncode == 0:
            print("Transcription complete")
            
            # Instead of saving to a file, we have the transcription in the stdout variable
            transcription_text = stdout
            
            # Revise the transcript using the correct_and_rephrase function
            revised_text = correct_and_rephrase(transcription_text)
            
            # Use the fixed SVG output filename
            if revised_text:
                print("Transcript revised successfully")
                # Convert the revised transcription directly to SVG
                convert_text_to_svg(revised_text, svg_output_filename)
                
                # For debugging/logging purposes, we can still save the revised text if needed
                # print(f"Revised transcript: {revised_text}")
            else:
                print("Using original transcript")
                # If revision fails, convert the original transcription to SVG
                convert_text_to_svg(transcription_text, svg_output_filename)
            
            return transcription_text
        else:
            print(f"Transcription failed with error: {stderr}")
            return None
    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        return None

def toggle_recording():
    global recording, recording_thread, stop_recording_flag, latest_filename
    
    if not recording:
        # Start recording - set LED to red
        print("Starting recording...")
        set_recording()  # Turn LED red during recording
        recording = True
        stop_recording_flag.clear()
        recording_thread = threading.Thread(target=start_recording)
        recording_thread.start()
    else:
        # Stop recording
        print("Stopping recording...")
        recording = False
        stop_recording_flag.set()
        if recording_thread:
            recording_thread.join()
        print("Recording stopped")
        
        # Set LED to blue to indicate processing
        set_processing()  # Turn LED blue during processing
        
        # Apply noise reduction to the recorded audio
        if latest_filename:
            # Check if the file exists
            if not os.path.exists(latest_filename):
                print(f"ERROR: Recording file not found at {latest_filename}")
                set_ready_to_record()
                return
                
            print(f"File exists: {latest_filename}")
            
            # Create the noise-reduced filename
            noise_reduced_filename = latest_filename.replace('.wav', '_reduced.wav')
            print(f"Reducing noise in recording: {latest_filename}")
            
            try:
                reduce_noise_in_audio(latest_filename, noise_reduced_filename, prop_decrease=0.75)
                print(f"Noise reduction complete. Output saved to: {noise_reduced_filename}")
                
                # Check if the reduced file exists
                if not os.path.exists(noise_reduced_filename):
                    print(f"ERROR: Noise-reduced file not found at {noise_reduced_filename}")
                    set_ready_to_record()
                    return
                    
                # Transcribe the noise-reduced audio
                transcribe_audio(noise_reduced_filename)
                
                # Set LED back to green to indicate ready for next recording
                set_ready_to_record()  # Turn LED green when ready
            except Exception as e:
                print(f"Error during processing: {str(e)}")
                set_ready_to_record()
        else:
            print("No recording file available")
            set_ready_to_record()

def start_recording():
    # Using a timestamp to create unique filenames
    global latest_filename
    
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"recording_{timestamp}.wav"
    # Create full path for the recording
    full_path = os.path.join(recordings_dir, filename)
    
    # Ensure recordings directory exists again (just to be safe)
    os.makedirs(recordings_dir, exist_ok=True)
    
    # Print full path for debugging
    print(f"Will save recording to: {full_path}")
    
    # Initialize PyAudio
    import pyaudio
    import wave
    
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16,
                        channels=1,
                        rate=16000,
                        input=True,
                        frames_per_buffer=1024)
    
    frames = []
    
    # Record until stop flag is set
    try:
        while not stop_recording_flag.is_set():
            data = stream.read(1024)
            frames.append(data)
    finally:
        # Clean up
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        # Save the recorded audio
        if frames:
            try:
                wave_file = wave.open(full_path, 'wb')
                wave_file.setnchannels(1)
                wave_file.setsampwidth(audio.get_sample_size(pyaudio.paInt16))
                wave_file.setframerate(16000)
                wave_file.writeframes(b''.join(frames))
                wave_file.close()
                print(f"Audio saved to {full_path}")
                
                # Verify the file exists and set latest_filename only after successful save
                if os.path.exists(full_path):
                    print(f"Verified file exists: {full_path}")
                    latest_filename = full_path
                else:
                    print(f"ERROR: File was not saved properly: {full_path}")
            except Exception as e:
                print(f"Error saving audio file: {str(e)}")
        else:
            print("No audio data was recorded")

# Set up button press event
button.when_pressed = toggle_recording

# Keep the script running
print("Press the button to start/stop recording. Press Ctrl+C to exit.")
try:
    # Initially set LED to green to indicate ready to record
    set_ready_to_record()
    
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    print("Exiting...")
    # Ensure recording is stopped before exiting
    if recording:
        stop_recording_flag.set()
        if recording_thread:
            recording_thread.join()
    
    # Clean up LED resources
    cleanup()
