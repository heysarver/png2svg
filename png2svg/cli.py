# png2svg/cli.py
import argparse
from .converter import PNG2SVG

def main():
    parser = argparse.ArgumentParser(description='Convert PNG to SVG with various options')
    parser.add_argument('input', help='Input PNG file')
    parser.add_argument('output', help='Output SVG file')
    parser.add_argument('--grouping', choices=['color', 'proximity', 'none'],
                       default='color', help='Grouping method')
    parser.add_argument('--gradients', action='store_true',
                       help='Enable gradient detection and creation')
    
    args = parser.parse_args()
    
    converter = PNG2SVG()
    converter.convert(args.input, args.output, args.grouping, args.gradients)

if __name__ == "__main__":
    main()
