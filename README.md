# PNG2SVG

A Python library for converting PNG images to SVG format with advanced grouping options and gradient support.

## Installation

```bash
pip install git+https://github.com/heysarver/png2svg.git
```

## Features

- Convert PNG files to optimized SVG format
- Multiple grouping options:
  - Color-based grouping
  - Proximity-based grouping
  - No grouping (pixel-by-pixel)
- Gradient detection and creation
- Transparency support
- Command-line interface
- Python API

## Usage

### Command Line Interface

```bash
# Basic usage
png2svg input.png output.svg

# With options
png2svg input.png output.svg --grouping proximity --gradients
```

### Python API

```python
from png2svg import PNG2SVG

# Create converter instance
converter = PNG2SVG()

# Basic conversion
converter.convert('input.png', 'output.svg')

# Advanced options
converter.convert('input.png', 'output.svg', 
                 grouping='proximity', 
                 enable_gradients=True)
```

## Requirements

- Python 3.7+
- Pillow
- NumPy
- OpenCV
- scikit-learn
- svgwrite

## License

MIT License
