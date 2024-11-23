# png2svg/converter.py
import numpy as np
from PIL import Image
import cv2
from sklearn.cluster import DBSCAN
import svgwrite
from collections import defaultdict

class PNG2SVG:
    def __init__(self):
        self.shapes = []
        self.gradients = {}
        
    def _format_color(self, color):
        """Convert color tuple to valid SVG RGB string."""
        return f"rgb({int(color[0])}, {int(color[1])}, {int(color[2])})"
        
    def detect_gradient(self, region):
        """Detect if a region contains a gradient and return gradient parameters."""
        unique_colors = np.unique(region.reshape(-1, region.shape[-1]), axis=0)
        if len(unique_colors) < 2:
            return None
            
        # Simple linear gradient detection
        y_coords, x_coords = np.where(np.all(region != region[0,0], axis=-1))
        if len(x_coords) == 0:
            return None
            
        # Determine gradient direction and colors
        start_color = tuple(map(int, region[0,0]))
        end_color = tuple(map(int, region[-1,-1]))
        
        angle = np.arctan2(np.mean(y_coords), np.mean(x_coords))
        return {
            'type': 'linear',
            'start_color': start_color,
            'end_color': end_color,
            'angle': angle
        }

    def group_by_color(self, image):
        """Group pixels by color."""
        height, width = image.shape[:2]
        colors = defaultdict(list)
        
        for y in range(height):
            for x in range(width):
                color = tuple(map(int, image[y, x]))  # Convert to regular integers
                if color[3] > 0:  # Only process non-transparent pixels
                    colors[color].append((x, y))
                    
        return colors

    def group_by_proximity(self, image):
        """Group pixels by proximity using DBSCAN clustering."""
        height, width = image.shape[:2]
        points = []
        colors = []
        
        for y in range(height):
            for x in range(width):
                if image[y, x][3] > 0:  # Only process non-transparent pixels
                    points.append([x, y])
                    colors.append(tuple(map(int, image[y, x])))  # Convert to regular integers
                    
        if not points:
            return {}, {}
            
        # Perform DBSCAN clustering
        clustering = DBSCAN(eps=5, min_samples=3).fit(points)
        labels = clustering.labels_
        
        # Group points by cluster
        clusters = defaultdict(list)
        cluster_colors = defaultdict(set)
        for point, color, label in zip(points, colors, labels):
            if label != -1:  # Ignore noise
                clusters[label].append(point)
                cluster_colors[label].add(color)
                
        return clusters, cluster_colors

    def create_svg_path(self, points):
        """Create SVG path from points."""
        if not points:
            return ""
            
        # Simple contour creation
        points = np.array(points)
        if len(points) < 3:
            return ""
            
        hull = cv2.convexHull(points.reshape(-1, 1, 2))
        path = f"M {hull[0][0][0]},{hull[0][0][1]}"
        
        for point in hull[1:]:
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
        
        # Add defs section for gradients if needed
        if enable_gradients:
            defs = dwg.defs  # Access defs as property, not method
        
        if grouping == 'color':
            color_groups = self.group_by_color(img)
            
            for color, points in color_groups.items():
                if enable_gradients:
                    # Check for gradients in region
                    region = np.zeros((height, width, 4), dtype=np.uint8)
                    for x, y in points:
                        region[y, x] = img[y, x]
                    gradient = self.detect_gradient(region)
                    
                    if gradient:
                        # Create gradient definition
                        grad_id = f"gradient_{len(self.gradients)}"
                        gradient_element = svgwrite.gradients.LinearGradient(id=grad_id)
                        gradient_element.add_stop_offset('0%', stop_color=self._format_color(gradient['start_color']))
                        gradient_element.add_stop_offset('100%', stop_color=self._format_color(gradient['end_color']))
                        
                        # Add gradient to defs
                        defs.add(gradient_element)
                        fill = f"url(#{grad_id})"
                    else:
                        fill = self._format_color(color[:3])
                else:
                    fill = self._format_color(color[:3])
                
                path = self.create_svg_path(points)
                if path:
                    dwg.add(dwg.path(d=path, fill=fill, fill_opacity=color[3]/255))
                    
        elif grouping == 'proximity':
            clusters, cluster_colors = self.group_by_proximity(img)
            
            for label, points in clusters.items():
                # Use average color of the cluster
                colors = list(cluster_colors[label])
                avg_color = tuple(map(int, np.mean(colors, axis=0)))
                
                path = self.create_svg_path(points)
                if path:
                    dwg.add(dwg.path(d=path, 
                                   fill=self._format_color(avg_color[:3]), 
                                   fill_opacity=avg_color[3]/255))
        else:
            # No grouping - process each pixel individually
            for y in range(height):
                for x in range(width):
                    color = tuple(map(int, img[y, x]))  # Convert to regular integers
                    if color[3] > 0:  # Only process non-transparent pixels
                        dwg.add(dwg.rect(insert=(x, y), size=(1, 1),
                                       fill=self._format_color(color[:3]), 
                                       fill_opacity=color[3]/255))
        
        # Save SVG
        dwg.save()
