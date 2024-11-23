import numpy as np
from PIL import Image
import cv2
from sklearn.cluster import DBSCAN
import svgwrite
from collections import defaultdict
from scipy import ndimage
from typing import List, Dict, Tuple, Optional

class PNG2SVG:
    def __init__(self):
        self.shapes = []
        self.gradients = {}
        
    def _format_color(self, color):
        """Convert color tuple to valid SVG RGB string."""
        return f"rgb({int(color[0])}, {int(color[1])}, {int(color[2])})"
        
    def detect_gradient(self, image, mask):
        """
        Detect if a region contains a gradient and return gradient parameters.
        Uses the entire shape region for better gradient detection.
        """
        # Extract the region using the mask
        region = image.copy()
        region[~mask] = [0, 0, 0, 0]
        
        # Convert RGBA to BGRA for OpenCV
        region_cv = cv2.cvtColor(region, cv2.COLOR_RGBA2BGRA)
        
        # Get unique colors in the masked region
        valid_pixels = region[mask]
        if len(valid_pixels) < 2:
            return None
            
        # Find the gradient direction using Sobel
        gray = cv2.cvtColor(region_cv, cv2.COLOR_BGRA2GRAY)
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        
        # Calculate average gradient direction
        angle = np.arctan2(np.mean(sobel_y), np.mean(sobel_x))
        
        # Find start and end colors along gradient direction
        coords = np.where(mask)
        center = np.mean(coords, axis=1)
        
        # Project points onto gradient direction
        points = np.array(coords).T - center
        projections = points @ np.array([np.cos(angle), np.sin(angle)])
        
        start_idx = np.argmin(projections)
        end_idx = np.argmax(projections)
        
        start_color = tuple(map(int, valid_pixels[start_idx][:3]))
        end_color = tuple(map(int, valid_pixels[end_idx][:3]))
        
        return {
            'type': 'linear',
            'start_color': start_color,
            'end_color': end_color,
            'angle': angle
        }

    def find_shapes(self, image):
        """Find distinct shapes in the image using connected components."""
        # Create binary mask of non-transparent pixels
        alpha = image[:, :, 3] > 0
        
        # Find connected components
        labeled, num_features = ndimage.label(alpha)
        
        shapes = []
        for label in range(1, num_features + 1):
            mask = labeled == label
            if np.sum(mask) > 10:  # Minimum size threshold
                shapes.append(mask)
                
        return shapes

    def create_svg_path(self, mask):
        """Create SVG path from binary mask."""
        # Find contours
        mask_uint8 = mask.astype(np.uint8) * 255
        contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if not contours:
            return ""
            
        # Get the largest contour
        contour = max(contours, key=cv2.contourArea)
        
        # Create SVG path
        path = f"M {contour[0][0][0]},{contour[0][0][1]}"
        for point in contour[1:]:
            path += f" L {point[0][0]},{point[0][1]}"
        path += " Z"
        
        return path

    def convert(self, input_path, output_path, grouping='color', enable_gradients=True):
        """Convert PNG to SVG with specified options."""
        # Load image
        img = np.array(Image.open(input_path))
        height, width = img.shape[:2]
        
        # Create SVG document
        dwg = svgwrite.Drawing(output_path, size=(width, height))
        
        # Find shapes in the image
        shapes = self.find_shapes(img)
        
        for shape_idx, mask in enumerate(shapes):
            path = self.create_svg_path(mask)
            if not path:
                continue
                
            if enable_gradients:
                gradient = self.detect_gradient(img, mask)
                
                if gradient:
                    # Create gradient definition
                    grad_id = f"gradient_{shape_idx}"
                    x1 = "0%"
                    y1 = "0%"
                    x2 = f"{100 * np.cos(gradient['angle']):.1f}%"
                    y2 = f"{100 * np.sin(gradient['angle']):.1f}%"
                    
                    # Create gradient element
                    linear_gradient = dwg.linearGradient(
                        id=grad_id,
                        x1=x1, y1=y1,
                        x2=x2, y2=y2
                    )
                    
                    # Add gradient stops
                    linear_gradient.add_stop_color(
                        offset='0%',
                        color=self._format_color(gradient['start_color']),
                        opacity=1
                    )
                    linear_gradient.add_stop_color(
                        offset='100%',
                        color=self._format_color(gradient['end_color']),
                        opacity=1
                    )
                    
                    # Add gradient to defs
                    dwg.defs.add(linear_gradient)
                    
                    fill = f"url(#{grad_id})"
                else:
                    # Use average color if no gradient
                    color = tuple(map(int, np.mean(img[mask], axis=0)))
                    fill = self._format_color(color[:3])
            else:
                # Use average color
                color = tuple(map(int, np.mean(img[mask], axis=0)))
                fill = self._format_color(color[:3])
            
            # Add the path with appropriate fill
            opacity = np.mean(img[mask][:, 3]) / 255
            path_element = dwg.path(d=path, fill=fill, fill_opacity=opacity)
            dwg.add(path_element)
        
        # Save SVG
        dwg.save()
