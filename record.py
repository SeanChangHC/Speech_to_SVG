import pyaudio
import wave
import sys
import signal
import time

def record_audio(output_filename="output.wav", format=pyaudio.paInt16, channels=1, rate=16000, chunk=1024):
    """
    Record audio from microphone until manually stopped with Ctrl+C.
    
    Parameters:
    - output_filename: name of the output WAV file
    - format: audio format (default: 16-bit)
    - channels: number of audio channels (default: 1 for mono)
    - rate: sampling rate in Hz (default: 16000)
    - chunk: number of frames per buffer (default: 1024)
    """
    # Initialize the PyAudio object
    audio = pyaudio.PyAudio()
    
    # Open the audio stream for capturing input
    stream = audio.open(format=format,
                        channels=channels,
                        rate=rate,
                        input=True,
                        frames_per_buffer=chunk)
    
    print("Recording... Press Ctrl+C to stop.")
    
    frames = []
    recording = True
    
    # Set up signal handler for clean exit on Ctrl+C
    def signal_handler(sig, frame):
        nonlocal recording
        recording = False
        print("\nStopping recording...")
    
    # Register the signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    # Record until stopped
    try:
        while recording:
            data = stream.read(chunk)
            frames.append(data)
    except KeyboardInterrupt:
        pass
    finally:
        # Stop and close the stream properly, then terminate PyAudio
        print("Finished recording.")
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        # Save the recorded frames as a WAV file
        wave_file = wave.open(output_filename, 'wb')
        wave_file.setnchannels(channels)
        wave_file.setsampwidth(audio.get_sample_size(format))
        wave_file.setframerate(rate)
        wave_file.writeframes(b''.join(frames))
        wave_file.close()
        
        print(f"Audio saved to {output_filename}")
        
        return output_filename

# Example usage
if __name__ == "__main__":
    record_audio()
