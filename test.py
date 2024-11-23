#!/usr/bin/env python3
"""
Test script for PNG2SVG library
Save this as test_png2svg.py and run it to test different conversion options
"""

from png2svg import PNG2SVG
import numpy as np
from PIL import Image

def create_test_image(filename="test_input.png", size=(300, 300)):
    """Create a test PNG image with various shapes and colors"""
    # Create a new image with alpha channel (RGBA)
    image = Image.new('RGBA', size, (255, 255, 255, 0))
    pixels = image.load()
    
    # Draw a red circle
    center = (size[0]//4, size[1]//4)
    radius = 50
    for x in range(size[0]):
        for y in range(size[1]):
            if (x - center[0])**2 + (y - center[1])**2 < radius**2:
                pixels[x, y] = (255, 0, 0, 255)  # Red
    
    # Draw a blue rectangle
    for x in range(size[0]//2, size[0]//2 + 100):
        for y in range(size[1]//2, size[1]//2 + 60):
            pixels[x, y] = (0, 0, 255, 255)  # Blue
    
    # Draw a gradient triangle
    for x in range(size[0]):
        for y in range(size[1]):
            if y > size[1]/2 and x > y - size[1]/2 and x < size[1] - (y - size[1]/2):
                gradient = int((x / size[0]) * 255)
                pixels[x, y] = (0, gradient, 0, 255)  # Green gradient
    
    # Save the test image
    image.save(filename)
    return filename

def test_conversion():
    """Test PNG2SVG conversion with different options"""
    # Create test image
    input_file = create_test_image()
    converter = PNG2SVG()
    
    # Test 1: Basic conversion with color grouping
    print("Testing color grouping...")
    converter.convert(
        input_file,
        'output_color.svg',
        grouping='color',
        enable_gradients=False
    )
    
    # Test 2: Proximity grouping
    print("Testing proximity grouping...")
    converter.convert(
        input_file,
        'output_proximity.svg',
        grouping='proximity',
        enable_gradients=False
    )
    
    # Test 3: No grouping
    print("Testing without grouping...")
    converter.convert(
        input_file,
        'output_nogrouping.svg',
        grouping='none',
        enable_gradients=False
    )
    
    # Test 4: With gradients enabled
    print("Testing with gradients...")
    converter.convert(
        input_file,
        'output_gradients.svg',
        grouping='color',
        enable_gradients=True
    )
    
    print("\nTest files generated:")
    print("1. output_color.svg - Basic color grouping")
    print("2. output_proximity.svg - Proximity-based grouping")
    print("3. output_nogrouping.svg - No grouping")
    print("4. output_gradients.svg - With gradient detection")

if __name__ == "__main__":
    print("Starting PNG2SVG conversion tests...")
    test_conversion()
    print("\nTests completed! Check the generated SVG files.")
