from freetype import Face
from svgpathtools import wsvg, Line, Path

def char_to_path(face, char):
    # Load the character
    face.load_char(char)
    
    # Extract the glyph outline
    outline = face.glyph.outline
    points = outline.points
    # If the glyph has no outline (e.g. space) return an empty path and zero width.
    if not points:
        return Path(), 0
    
    # Get font metrics
    # In FreeType, the baseline is at y=0, with positive y going up
    # We need to adjust coordinates to work with SVG where positive y goes down
    bearing_y = face.glyph.metrics.horiBearingY / 64.0  # Distance from baseline to top of glyph
    
    # Transform points: 
    # 1. Shift all points so that the baseline is at y=0 in our coordinate system
    # 2. Flip y coordinates for SVG (positive y goes down)
    outline_points = [(p[0], -p[1]) for p in points]
    
    # Normalize x coordinates: subtract the left bearing (left edge of the character)
    # This ensures the character starts at x=0
    min_x = min(pt[0] for pt in outline_points)
    outline_points = [(pt[0] - min_x, pt[1]) for pt in outline_points]
    
    # Create paths for all contours
    path = Path()
    start = 0
    for end in outline.contours:
        contour_points = outline_points[start:end + 1]
        # Create lines for the contour
        for i in range(len(contour_points) - 1):
            line = Line(
                start=contour_points[i][0] + 1j * contour_points[i][1],
                end=contour_points[i + 1][0] + 1j * contour_points[i + 1][1]
            )
            path.append(line)
        
        # Close the contour by connecting the last point to the first
        line = Line(
            start=contour_points[-1][0] + 1j * contour_points[-1][1],
            end=contour_points[0][0] + 1j * contour_points[0][1]
        )
        path.append(line)
        
        start = end + 1
    
    # Compute the visible width of the glyph
    glyph_width = max(pt[0] for pt in outline_points) if outline_points else 0
    
    return path, glyph_width

def create_marker(x, y, size=10):
    """Create a simple cross marker at the specified position"""
    path = Path()
    # Horizontal line
    path.append(Line(complex(x - size, y), complex(x + size, y)))
    # Vertical line
    path.append(Line(complex(x, y - size), complex(x, y + size)))
    return path

def sentence_to_path(face, sentence, char_spacing=200, word_spacing=400, max_width=2000, line_spacing=3000):
    """
    Converts a sentence (string) into a combined SVG path.
    Each character is drawn sequentially by translating it by the cumulative width of previous characters.
    Characters are aligned along the baseline (ground).
    Line breaks are automatically inserted when a line exceeds max_width.
    
    Args:
        face: The font face
        sentence: The text to render
        char_spacing: Spacing between individual characters (in units)
        word_spacing: Additional spacing to add between words (in units)
        max_width: Maximum width of a line before wrapping (in units)
        line_spacing: Vertical spacing between lines (in units)
    """
    # Debug - print input parameters
    print(f"Processing sentence: '{sentence}'")
    print(f"Using char_spacing={char_spacing}, word_spacing={word_spacing}, max_width={max_width}, line_spacing={line_spacing}")
    
    combined_path = Path()
    x_offset = 0
    
    # By default in SVG, y increases downward
    # The baseline in our coordinate system will be at y=0
    baseline_y = 0
    current_line = 0  # Track the current line number (0-based)
    
    # Split the sentence into words and manually handle the spacing
    words = sentence.split()
    print(f"Split into {len(words)} words: {words}")
    
    # Add a starting marker
    # combined_path.extend(create_marker(x_offset, baseline_y))
    x_offset += 50  # Offset from the initial marker
    
    # For tracking word boundaries at line break points
    line_break_before_word = False
    
    for word_idx, word in enumerate(words):
        # Check if this word might exceed the line width
        # We need to calculate the width of the word + spacing
        word_width = 0
        for char in word:
            face.load_char(char)
            if not face.glyph.outline.points:
                char_width = face.glyph.advance.x / 64.0
            else:
                _, char_width = char_to_path(face, char)
            word_width += char_width + char_spacing
        
        # Subtract the last character spacing as it doesn't apply to the last character
        if len(word) > 0:
            word_width -= char_spacing
        
        # Debug: print the word and its width
        print(f"Word: '{word}', Width: {word_width}, Current x_offset: {x_offset}")
        
        # Check if adding this word would exceed max_width
        # Include word spacing only if it's not the first word on the line
        word_spacing_to_add = word_spacing if x_offset > 50 and not line_break_before_word else 0
        
        # Only break line if BOTH:
        # 1. Adding this word would exceed max_width
        # 2. We're not at the start of a line (x_offset > 50)
        if x_offset + word_width + word_spacing_to_add > max_width and x_offset > 50:
            print(f"Line break triggered: x_offset ({x_offset}) + word_width ({word_width}) + word_spacing ({word_spacing_to_add}) > max_width ({max_width})")
            # Start a new line
            current_line += 1
            baseline_y = current_line * line_spacing
            x_offset = 50  # Reset x to beginning of line
            
            # Add line break markers - a horizontal line to clearly show line separation
            # line_width = 50  # Width of the horizontal line marker
            # line_marker = Line(complex(0, baseline_y - line_spacing/2), complex(line_width, baseline_y - line_spacing/2))
            # combined_path.append(line_marker)
            
            # Add a new line marker
            # combined_path.extend(create_marker(0, baseline_y))
            print(f"Line break inserted. New line y-position: {baseline_y}")
            
            # Flag that we just did a line break
            line_break_before_word = True
        else:
            line_break_before_word = False
        
        # Process each character in the word
        for char_idx, char in enumerate(word):
            # Load the character
            face.load_char(char)
            
            # Get the glyph path and its width (handle glyphs without outlines)
            if not face.glyph.outline.points:
                # For spaces or other characters without outlines
                glyph_width = face.glyph.advance.x / 64.0
                glyph_path = Path()
            else:
                glyph_path, glyph_width = char_to_path(face, char)
            
            # Translate and add to combined path
            translated_path = glyph_path.translated(complex(x_offset, baseline_y))
            combined_path.extend(translated_path)
            
            # Move to the end of the character
            x_offset += glyph_width
            
            # Add a character marker
            # combined_path.extend(create_marker(x_offset, baseline_y))
            
            # Add character spacing - now visual and explicit
            if char_idx < len(word) - 1:  # Not after the last character in the word
                x_offset += char_spacing
                # Add a spacing marker
                # combined_path.extend(create_marker(x_offset, baseline_y - 20))
        
        # After each word, add word spacing (except for the last word)
        if word_idx < len(words) - 1:
            # Add word spacing between words, even after a line break
            # This ensures space is added between words on new lines
            x_offset += word_spacing
            # Add a word spacing marker at a different height to distinguish it
            # combined_path.extend(create_marker(x_offset - word_spacing/2, baseline_y - 40))
            
            # If we're at the end of a line and the next word would exceed max_width,
            # we'll clear this word spacing in the next iteration when we do the line break
            
            # Reset the line break flag after we've processed a word
            line_break_before_word = False
    
    return combined_path

def tsvg(text_input, max_width=8000, line_spacing=3000):
    """
    Process the input text and convert it to SVG using the existing sentence_to_path function.
    
    Args:
        text_input (str): The text to be processed
        max_width (int): Maximum width of a line before wrapping
        line_spacing (int): The vertical spacing between lines when wrapped
        
    Returns:
        Path: The SVG path object representing the text
    """
    # Load the font and set the desired size
    face = Face('./Vera.ttf')
    face.set_char_size(24 * 64)  # Further reduced font size for more words per line
    
    # Clean up the input text if needed (e.g., handle newlines, remove special characters)
    # This is optional and depends on your needs
    clean_text = text_input.replace('\n', ' ').strip()
    
    # Convert the input text into a combined SVG path with line wrapping
    combined_svg_path = sentence_to_path(face, clean_text, char_spacing=40, word_spacing=100, max_width=max_width, line_spacing=line_spacing)
    
    # Return the path directly
    return combined_svg_path

if __name__ == '__main__':
    # Load the font and set the desired size.
    face = Face('./Vera.ttf')
    face.set_char_size(20 * 28)  # Using smaller font size
    
    # Test with a shorter string to clearly see spacing
    test_input = "Extreme Spacing Values: Using much larger values"
    
    # Use the direct sentence_to_path function with natural word wrapping settings
    result = sentence_to_path(face, test_input, char_spacing=40, word_spacing=200, max_width=8000, line_spacing=1000)
    
    # Export the combined path to an SVG file with a viewBox to ensure everything is visible
    wsvg(result, filename="sentence.svg")
    print(f"SVG saved to 'sentence.svg'")
    
    # Test with a long sentence that should wrap
    long_test = "Note that these widths are in font units, which depend on the font size and other attributes. Words should flow naturally to the next line when they reach the boundary."
    print("Creating a test with line wrapping...")
    # Using a max_width that should allow several words per line before wrapping
    result3 = sentence_to_path(face, long_test, char_spacing=40, word_spacing=200, max_width=8000, line_spacing=1000)
    wsvg(result3, filename="wrapped_text.svg")
    print(f"Wrapped text SVG saved to 'wrapped_text.svg'")
    