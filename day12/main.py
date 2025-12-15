import argparse


class Shape:
    def __init__(self, lines):
        """Initialize a Shape with an array of three strings."""
        if len(lines) != 3:
            raise ValueError("Shape must have exactly 3 lines")
        self.lines = lines
    
    def __repr__(self):
        return f"Shape({self.lines[0]}, {self.lines[1]}, {self.lines[2]})"


class Region:
    def __init__(self, width, length, numbers):
        """Initialize a Region with width, length, and a list of 6 numbers."""
        self.width = width
        self.length = length
        if len(numbers) != 6:
            raise ValueError("Region must have exactly 6 numbers")
        self.numbers = numbers
    
    def possibly_fits(self):
        area = int(self.width)//3 * int(self.length)//3
        totalboxes = sum(self.numbers)
        return area >= totalboxes
    
    def __repr__(self):
        return f"Region({self.width}x{self.length}: {self.numbers})"


def parse_file(filename):
    """Parse the input file and return shapes and regions."""
    shapes = []
    regions = []
    
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    i = 0
    # Parse shapes (should be 6 shapes, numbered 0-5)
    while i < len(lines) and len(shapes) < 6:
        line = lines[i].strip()
        if line.endswith(':'):
            # This is a shape header (e.g., "0:")
            shape_lines = []
            i += 1
            # Read the next 3 lines for the shape
            for j in range(3):
                if i < len(lines):
                    shape_lines.append(lines[i].strip())
                    i += 1
            shapes.append(Shape(shape_lines))
            # Skip empty line if present
            if i < len(lines) and lines[i].strip() == '':
                i += 1
        else:
            i += 1
    
    # Parse regions
    while i < len(lines):
        line = lines[i].strip()
        if 'x' in line and ':' in line:
            # Parse region header (e.g., "4x4:")
            parts = line.split(':')
            size_part = parts[0].strip()
            width, length = map(int, size_part.split('x'))
            
            # Parse the 6 numbers
            if len(parts) > 1 and parts[1].strip():
                # Numbers are on the same line
                numbers = list(map(int, parts[1].strip().split()))
            else:
                # Numbers might be on the next line
                i += 1
                if i < len(lines):
                    numbers = list(map(int, lines[i].strip().split()))
                else:
                    numbers = []
            
            if len(numbers) == 6:
                regions.append(Region(width, length, numbers))
        i += 1
    
    return shapes, regions


def main():
    parser = argparse.ArgumentParser(description='Parse shapes and regions from input file')
    parser.add_argument('input_file', help='Input file name')
    args = parser.parse_args()
    
    shapes, regions = parse_file(args.input_file)
    
    for i, shape in enumerate(shapes):
        print(f"Shape {i}:")
        print(shape)
    
    print(f"Parsed {len(regions)} regions:")
    for region in regions:
        print(region)
    print(f"Total number of regions: {len(regions)}")
    print(f"Total number of shapes: {len(shapes)}")

    total_fits = 0
    for region in regions:
        if region.possibly_fits():
            total_fits += 1
    print(f"Total number of regions that possibly fit: {total_fits}")


if __name__ == '__main__':
    main()

