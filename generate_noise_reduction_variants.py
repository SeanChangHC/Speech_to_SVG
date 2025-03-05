#!/usr/bin/env python3

import os
import sys
from noise import reduce_noise_in_audio

def generate_noise_reduction_variants(input_file):
    """
    Generate multiple variants of noise-reduced audio from the same input file
    with different reduction strengths.
    
    Args:
        input_file (str): Path to the input audio file
    """
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist!")
        return
    
    # Create output directory
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_dir = f"{base_name}_variants"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Generating noise reduction variants for: {input_file}")
    print(f"Output files will be saved to: {output_dir}")
    
    # Generate variants with different noise reduction levels
    reduction_levels = [
        {"label": "very_light", "prop_decrease": 0.2},
        {"label": "light", "prop_decrease": 0.4},
        {"label": "medium", "prop_decrease": 0.6},
        {"label": "strong", "prop_decrease": 0.8},
        {"label": "very_strong", "prop_decrease": 0.95}
    ]
    
    for level in reduction_levels:
        output_file = os.path.join(output_dir, f"{base_name}_{level['label']}.wav")
        print(f"Generating {level['label']} reduction (prop_decrease={level['prop_decrease']})...")
        
        reduce_noise_in_audio(
            input_file_path=input_file,
            output_file_path=output_file,
            prop_decrease=level['prop_decrease'],
            stationary=True
        )
        print(f"  Saved to: {output_file}")
    
    # Also create a non-stationary noise variant with medium reduction
    output_file = os.path.join(output_dir, f"{base_name}_nonstationary.wav")
    print("Generating non-stationary noise reduction variant...")
    reduce_noise_in_audio(
        input_file_path=input_file,
        output_file_path=output_file,
        prop_decrease=0.6,
        stationary=False
    )
    print(f"  Saved to: {output_file}")
    
    print("\nAll variants have been generated!")
    print(f"Check the '{output_dir}' directory for the output files")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_noise_reduction_variants.py <input_wav_file>")
        print("ERROR: You must provide a path to a WAV audio file, not a Python script or other file type!")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    # Check if file exists and has .wav extension
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' does not exist!")
        sys.exit(1)
    
    if not input_file.lower().endswith('.wav'):
        print(f"Warning: '{input_file}' doesn't have a .wav extension. Are you sure it's a WAV audio file?")
        choice = input("Continue anyway? (y/n): ")
        if choice.lower() != 'y':
            sys.exit(1)
    
    generate_noise_reduction_variants(input_file) 