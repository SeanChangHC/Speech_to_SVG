#!/usr/bin/env python3

import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from noise import reduce_noise_in_audio, evaluate_noise_reduction_pesq

def test_different_noise_reduction_levels(input_file, output_dir="noise_reduction_tests"):
    """
    Generate multiple versions of the same input file with different noise reduction settings.
    
    Args:
        input_file (str): Path to the input audio file
        output_dir (str): Directory to save the output files
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Test different prop_decrease values (how aggressively noise is reduced)
    prop_decrease_values = [0.1, 0.3, 0.5, 0.7, 0.9]
    
    # Generate output files with different noise reduction levels
    results = []
    
    print(f"Processing input file: {input_file}")
    
    for prop in prop_decrease_values:
        output_file = os.path.join(output_dir, f"reduced_prop_{prop:.1f}.wav")
        
        # Apply noise reduction with current prop_decrease value
        reduce_noise_in_audio(
            input_file_path=input_file,
            output_file_path=output_file,
            prop_decrease=prop,
            stationary=True
        )
        
        # Calculate PESQ score (comparing to original)
        try:
            pesq_score = evaluate_noise_reduction_pesq(input_file, output_file)
            results.append((prop, pesq_score, output_file))
            print(f"Prop_decrease: {prop:.1f}, PESQ Score: {pesq_score:.4f}, Output: {output_file}")
        except Exception as e:
            print(f"Error calculating PESQ for prop_decrease={prop}: {str(e)}")
    
    # Also test with non-stationary noise assumption
    output_file = os.path.join(output_dir, "reduced_nonstationary.wav")
    reduce_noise_in_audio(
        input_file_path=input_file,
        output_file_path=output_file,
        prop_decrease=0.5,  # middle value
        stationary=False
    )
    try:
        pesq_score = evaluate_noise_reduction_pesq(input_file, output_file)
        results.append((0.5, pesq_score, output_file))
        print(f"Non-stationary noise, Prop_decrease: 0.5, PESQ Score: {pesq_score:.4f}, Output: {output_file}")
    except Exception as e:
        print(f"Error calculating PESQ for non-stationary noise: {str(e)}")
    
    # Plot results if we have valid PESQ scores
    if results:
        props = [r[0] for r in results if "nonstationary" not in r[2]]
        scores = [r[1] for r in results if "nonstationary" not in r[2]]
        
        plt.figure(figsize=(10, 6))
        plt.plot(props, scores, 'o-')
        plt.xlabel('Noise Reduction Strength (prop_decrease)')
        plt.ylabel('PESQ Score')
        plt.title('Effect of Noise Reduction Strength on Audio Quality')
        plt.grid(True)
        plt.savefig(os.path.join(output_dir, 'pesq_scores.png'))
        print(f"Results plot saved to {os.path.join(output_dir, 'pesq_scores.png')}")
    
    return results

def advanced_noise_reduction_tests(input_file, output_dir="advanced_tests"):
    """
    Test different combinations of noise reduction parameters beyond just prop_decrease.
    
    Args:
        input_file (str): Path to the input audio file
        output_dir (str): Directory to save the output files
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Test combinations of different parameters
    test_configs = [
        # Mild reduction with different FFT window sizes
        {"prop_decrease": 0.3, "n_fft": 1024, "name": "mild_small_fft"},
        {"prop_decrease": 0.3, "n_fft": 4096, "name": "mild_large_fft"},
        
        # Moderate reduction with different smoothing settings
        {"prop_decrease": 0.5, "time_mask_smooth_ms": 50, "name": "mod_smooth_50ms"},
        {"prop_decrease": 0.5, "time_mask_smooth_ms": 200, "name": "mod_smooth_200ms"},
        
        # Strong reduction with different hop lengths
        {"prop_decrease": 0.7, "hop_length": 256, "name": "strong_hop_256"},
        {"prop_decrease": 0.7, "hop_length": 512, "name": "strong_hop_512"},
    ]
    
    print(f"\nAdvanced testing with input file: {input_file}")
    
    for config in test_configs:
        output_file = os.path.join(output_dir, f"{config['name']}.wav")
        
        # Get parameters for this test
        params = config.copy()
        del params['name']  # Remove name key from parameters
        
        # Apply noise reduction with current parameters
        # Note: This requires modifying the reduce_noise_in_audio function to accept these parameters
        # or wrapping the noisereduce call directly here
        try:
            # Assuming we've modified reduce_noise_in_audio to accept **kwargs
            # that get passed to nr.reduce_noise
            reduce_noise_in_audio(
                input_file_path=input_file,
                output_file_path=output_file,
                **params
            )
            
            print(f"Generated: {output_file} with params: {params}")
        except Exception as e:
            print(f"Error generating {output_file}: {str(e)}")

if __name__ == "__main__":
    # Replace with your input file path - needs to be a WAV audio file
    input_file = "recording_20250304-172320.wav"  # CHANGE THIS TO YOUR ACTUAL WAV FILE
    
    # Run basic noise reduction tests
    test_different_noise_reduction_levels(input_file)
    
    # Uncomment to run advanced tests (requires modifying reduce_noise_in_audio function)
    # advanced_noise_reduction_tests(input_file) 