import argparse
from typing import List, Tuple

def largest_rectangle_area(tuples: List[Tuple[int, int]]) -> int:
    """
    Find the largest area of an axis-aligned rectangle that can be formed
    using two points from the list of tuples as diagonal corners.
    
    Optimized for large lists by:
    - Only checking pairs of points (O(n²))
    - Simple area calculation without additional checks
    
    Args:
        tuples: List of (x, y) coordinate tuples
        
    Returns:
        The largest rectangle area, or 0 if no valid rectangle can be formed
    """
    if len(tuples) < 2:
        return 0
    
    max_area = 0
    
    # Try all pairs of points as potential diagonal corners
    for i in range(len(tuples)):
        x1, y1 = tuples[i]
        for j in range(i + 1, len(tuples)):
            x2, y2 = tuples[j]
            
            # For two points to form a rectangle, they must have different x and y
            if x1 == x2 or y1 == y2:
                continue
            
            # Calculate area (using absolute value to handle any ordering)
            # Add 1 to include both endpoints in the width and height
            width = abs(x2 - x1) + 1
            height = abs(y2 - y1) + 1
            area = width * height
            max_area = max(max_area, area)
    
    return max_area

def main():
    parser = argparse.ArgumentParser(description='Read tuples from file')
    parser.add_argument('file', type=str, help='Path to the input file')
    args = parser.parse_args()
    
    tuples = []
    
    with open(args.file, 'r') as f:
        for line in f:
            line = line.strip()
            if line:  # Skip empty lines
                parts = line.split(',')
                if len(parts) == 2:
                    # Convert to integers and create tuple
                    tuple_item = (int(parts[0]), int(parts[1]))
                    tuples.append(tuple_item)
    
    print(f"Read {len(tuples)} tuples:")
    for t in tuples:
        print(t)
    
    # Find and print the largest rectangle area
    area = largest_rectangle_area(tuples)
    print(f"\nLargest rectangle area: {area}")
    
    return tuples

if __name__ == "__main__":
    result = main()

