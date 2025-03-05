import noisereduce as nr
from scipy.io import wavfile

def reduce_noise_in_audio(input_file_path, output_file_path, prop_decrease=0.75, stationary=True, **kwargs):
    """
    Reduces noise in an audio file and saves the result to a new file.
    
    Args:
        input_file_path (str): Path to the input audio file
        output_file_path (str): Path where the noise-reduced audio will be saved
        prop_decrease (float): How much to reduce the noise by (0.0 to 1.0)
                              Lower values preserve more of the original signal
        stationary (bool): Whether the noise is constant throughout the clip
        **kwargs: Additional parameters to pass to noisereduce.reduce_noise:
            - n_fft (int): FFT window size, default is 2048
            - win_length (int): Window length, default is n_fft
            - hop_length (int): Hop length, default is win_length//4
            - time_mask_smooth_ms (int): Time mask smoothing in milliseconds
            - freq_mask_smooth_hz (int): Frequency mask smoothing in Hz
            - n_std_thresh_stationary (float): Number of std devs for stationary noise threshold
            - n_std_thresh_nonstationary (float): Number of std devs for non-stationary noise threshold
            - use_tqdm (bool): Whether to show progress bar
    """
    # Load the audio file
    fs, data = wavfile.read(input_file_path)
    
    # Prepare parameters dictionary with default values
    params = {
        'y': data,
        'sr': fs,
        'prop_decrease': prop_decrease,
        'stationary': stationary
    }
    
    # Add any additional parameters passed in kwargs
    params.update(kwargs)
    
    # Reduce noise using noisereduce with the parameters
    reduced_noise = nr.reduce_noise(**params)
    
    # Write the cleaned audio to a new file
    wavfile.write(output_file_path, fs, reduced_noise)




import numpy as np
from scipy.io import wavfile
from pesq import pesq

def evaluate_noise_reduction_pesq(original_filepath, denoised_filepath):
    """
    Evaluate noise reduction performance using the PESQ metric.

    Parameters:
    - original_filepath (str): Path to the clean (original) audio file.
    - denoised_filepath (str): Path to the noise-reduced audio file.

    Returns:
    - float: PESQ score indicating the perceptual quality of the denoised audio.
    """
    # Load the audio files
    fs_orig, audio_orig = wavfile.read(original_filepath)
    fs_denoised, audio_denoised = wavfile.read(denoised_filepath)
    
    # Ensure both files have the same sampling rate
    if fs_orig != fs_denoised:
        raise ValueError("Sample rates of the two audio files do not match.")
    
    # Convert to mono if needed
    if audio_orig.ndim > 1:
        audio_orig = np.mean(audio_orig, axis=1)
    if audio_denoised.ndim > 1:
        audio_denoised = np.mean(audio_denoised, axis=1)
    
    # Truncate both signals to the same length
    min_len = min(len(audio_orig), len(audio_denoised))
    audio_orig = audio_orig[:min_len]
    audio_denoised = audio_denoised[:min_len]
    
    # Set the mode: 'wb' for wideband (>=16kHz) or 'nb' for narrowband (<16kHz)
    mode = 'wb' if fs_orig >= 16000 else 'nb'
    
    # Compute and return the PESQ score
    pesq_score = pesq(fs_orig, audio_orig, audio_denoised, mode)
    return pesq_score

# Example usage:
# if __name__ == "__main__":
#     score = evaluate_noise_reduction_pesq("output.wav", "my_audio_file_reduced.wav")
#     print(f"PESQ score: {score}")
    # PESQ score: 1.0977427959442139
