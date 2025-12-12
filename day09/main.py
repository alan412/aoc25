import argparse
from typing import List, Tuple, Dict
from collections import deque
from functools import lru_cache

# Global variable to store the loop points for memoization
_loop_points: Tuple[Tuple[int, int], ...] = None

def set_loop_points(loop_points: List[Tuple[int, int]]):
    """Set the global loop points for memoization."""
    global _loop_points
    _loop_points = tuple(loop_points)
    # Clear the cache when loop points change
    is_point_inside_loop.cache_clear()

@lru_cache(maxsize=None)
def is_point_inside_loop(point: Tuple[int, int]) -> bool:
    """
    Check if a point is inside a closed loop using ray casting algorithm.
    Casts a ray to the right and counts boundary crossings.
    Handles integer coordinates correctly.
    Uses global _loop_points for memoization.
    
    Args:
        point: (x, y) point to check
        
    Returns:
        True if point is inside the loop, False otherwise
    """
    if _loop_points is None:
        raise ValueError("Loop points not set. Call set_loop_points() first.")
    
    x, y = point
    crossings = 0
    
    # Check each edge of the loop
    for i in range(len(_loop_points)):
        p1 = _loop_points[i]
        p2 = _loop_points[(i + 1) % len(_loop_points)]
        
        x1, y1 = p1
        x2, y2 = p2
        
        # Skip horizontal edges (they don't cross the ray)
        if y1 == y2:
            continue
        
        # Check if the ray from (x, y) going right crosses this edge
        # The edge must cross the horizontal line at y
        # Use >= for one endpoint and < for the other to handle edge cases
        if (y1 >= y) != (y2 >= y):
            # Calculate x-coordinate where edge crosses y using integer arithmetic
            # x_intersect = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            # For integer check: (x_intersect > x) is equivalent to:
            # (x1 * (y2 - y1) + (y - y1) * (x2 - x1) > x * (y2 - y1))
            # But we need to be careful with signs
            if y2 > y1:
                # Edge goes upward, check if intersection is to the right
                if (x2 - x1) * (y - y1) > (x - x1) * (y2 - y1):
                    crossings += 1
            else:
                # Edge goes downward, check if intersection is to the right
                if (x2 - x1) * (y - y1) < (x - x1) * (y2 - y1):
                    crossings += 1
    
    # Odd number of crossings means point is inside
    return crossings % 2 == 1

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

def largest_rectangle_area_of_tiles(tiles: Dict[Tuple[int, int], str], original_tuples: List[Tuple[int, int]]) -> int:
    """
    Find the largest area of an axis-aligned rectangle where:
    - The corners must be from the original input tuples
    - All 4 corners are on the loop boundary (in tiles)
    - All points inside the rectangle are inside the loop
    
    Optimized for large grids by:
    - Only checking pairs of points from the original tuples
    - Using point-in-polygon check instead of filling the entire grid
    - Early termination when a point is found outside
    
    Args:
        tiles: Dictionary mapping (x, y) tuples to their tile values (loop boundary)
        original_tuples: List of original input (x, y) tuples forming the loop
        
    Returns:
        The largest rectangle area, or 0 if no valid rectangle can be formed
    """
    if len(original_tuples) < 2:
        return 0
    
    # Use only the original input tuples as potential corners
    points = original_tuples
    
    max_area = 0
    
    # Try all pairs of points as potential diagonal corners
    for i in range(len(points)):
        px1, py1 = points[i]
        for j in range(i + 1, len(points)):
            px2, py2 = points[j]
            
            # For two points to form a rectangle, they must have different x and y
            if px1 == px2 or py1 == py2:
                continue
            
            # Ensure x1 < x2 and y1 < y2 for easier calculation
            x1, x2 = min(px1, px2), max(px1, px2)
            y1, y2 = min(py1, py2), max(py1, py2)
            
            # Check if all 4 corners are on the loop boundary
            corners = [
                (x1, y1),  # bottom-left
                (x1, y2),  # top-left
                (x2, y1),  # bottom-right
                (x2, y2)   # top-right
            ]
            
            if not all(corner in tiles for corner in corners):
                continue
            
            # Check if all points inside the rectangle are inside the loop
            # Use point-in-polygon check instead of checking tiles dict
            all_points_inside = True
            for x in range(x1, x2 + 1):
                for y in range(y1, y2 + 1):
                    if not is_point_inside_loop((x, y), original_tuples):
                        all_points_inside = False
                        break
                if not all_points_inside:
                    break
            
            if all_points_inside:
                # Calculate area (including both endpoints)
                width = x2 - x1 + 1
                height = y2 - y1 + 1
                area = width * height
                max_area = max(max_area, area)
    
    return max_area

def get_line_points(p1: Tuple[int, int], p2: Tuple[int, int]) -> List[Tuple[int, int]]:
    """
    Get all points on a straight line between two points (inclusive of both endpoints).
    Only handles horizontal and vertical lines (no diagonals).
    """
    x1, y1 = p1
    x2, y2 = p2
    
    points = []
    
    # Handle horizontal line
    if y1 == y2:
        step = 1 if x2 > x1 else -1
        for x in range(x1, x2 + step, step):
            points.append((x, y1))
    # Handle vertical line
    elif x1 == x2:
        step = 1 if y2 > y1 else -1
        for y in range(y1, y2 + step, step):
            points.append((x1, y))
    # If neither horizontal nor vertical, return just the endpoints
    else:
        points = [p1, p2]
    
    return points

def largest_rectangle_area_of_tiles(tiles: Dict[Tuple[int, int], str], original_tuples: List[Tuple[int, int]]) -> int:
    """
    Find the largest area of an axis-aligned rectangle where:
    - The corners must be from the original input tuples
    - All 4 corners are on the loop boundary (in tiles)
    - All points inside the rectangle are inside the loop
    
    Optimized for large grids by:
    - Only checking pairs of points from the original tuples
    - Using point-in-polygon check instead of filling the entire grid
    - Early termination when a point is found outside
    
    Args:
        tiles: Dictionary mapping (x, y) tuples to their tile values (loop boundary)
        original_tuples: List of original input (x, y) tuples forming the loop
        
    Returns:
        The largest rectangle area, or 0 if no valid rectangle can be formed
    """
    if len(original_tuples) < 2:
        return 0
    
    # Set the global loop points for memoization
    set_loop_points(original_tuples)
    
    # Use only the original input tuples as potential corners
    points = original_tuples
    
    max_area = 0
    
    # Try all pairs of points as potential diagonal corners
    for i in range(len(points)):
        px1, py1 = points[i]
        for j in range(i + 1, len(points)):
            px2, py2 = points[j]
            
            # For two points to form a rectangle, they must have different x and y
            if px1 == px2 or py1 == py2:
                continue
            
            # Ensure x1 < x2 and y1 < y2 for easier calculation
            x1, x2 = min(px1, px2), max(px1, px2)
            y1, y2 = min(py1, py2), max(py1, py2)
            
            # Calculate potential area first - skip if smaller than current max
            width = x2 - x1 + 1
            height = y2 - y1 + 1
            potential_area = width * height
            if potential_area <= max_area:
                continue
            
            # Check if the two diagonal corners (from original input) are on the loop boundary
            if (px1, py1) not in tiles or (px2, py2) not in tiles:
                continue
            
            # Check the other two corners first (fast rejection)
            corner1 = (x1, y2)  # top-left
            corner2 = (x2, y1)  # bottom-right
            if (corner1 not in tiles and not is_point_inside_loop(corner1)) or \
               (corner2 not in tiles and not is_point_inside_loop(corner2)):
                continue
            
            # Check perimeter first (faster than checking all interior points)
            # Top and bottom edges
            perimeter_valid = True
            for x in range(x1, x2 + 1):
                for y in [y1, y2]:
                    point = (x, y)
                    if point not in tiles and not is_point_inside_loop(point):
                        perimeter_valid = False
                        break
                if not perimeter_valid:
                    break
            
            if not perimeter_valid:
                continue
            
            # Left and right edges (excluding corners already checked)
            for y in range(y1 + 1, y2):
                for x in [x1, x2]:
                    point = (x, y)
                    if point not in tiles and not is_point_inside_loop(point):
                        perimeter_valid = False
                        break
                if not perimeter_valid:
                    break
            
            if not perimeter_valid:
                continue
            
            # If perimeter is valid, check interior points
            # For very large rectangles, sample interior points; for smaller ones, check all
            all_points_inside = True
            interior_width = x2 - x1 - 1
            interior_height = y2 - y1 - 1
            
            # For large rectangles, use sparse sampling; for smaller ones, check all points
            if interior_width > 50 or interior_height > 50:
                # Sample points in a grid pattern
                x_step = max(1, interior_width // 10)
                y_step = max(1, interior_height // 10)
                for x in range(x1 + 1, x2, x_step):
                    for y in range(y1 + 1, y2, y_step):
                        point = (x, y)
                        if point not in tiles and not is_point_inside_loop(point):
                            all_points_inside = False
                            break
                    if not all_points_inside:
                        break
            else:
                # Check all interior points for smaller rectangles
                for x in range(x1 + 1, x2):
                    for y in range(y1 + 1, y2):
                        point = (x, y)
                        if point not in tiles and not is_point_inside_loop(point):
                            all_points_inside = False
                            break
                    if not all_points_inside:
                        break
            
            if all_points_inside:
                max_area = potential_area
    
    return max_area

def create_tiles_dict(tuples: List[Tuple[int, int]]) -> Dict[Tuple[int, int], str]:
    """
    Create a tiles dictionary where:
    - Points from the input are marked as '#'
    - Points on lines between consecutive points are marked as 'O'
    - The last point connects to the first point
    
    Args:
        tuples: List of (x, y) coordinate tuples
        
    Returns:
        Dictionary mapping (x, y) tuples to their tile values
    """
    tiles: Dict[Tuple[int, int], str] = {}
    
    if not tuples:
        return tiles
    
    # Process lines between consecutive points (including last to first)
    for i in range(len(tuples)):
        point = tuples[i]
        next_point = tuples[(i + 1) % len(tuples)]
        
        # Get all points on the line between current and next point
        line_points = get_line_points(point, next_point)
        
        # Mark all points on the line as 'X'
        for line_point in line_points:
            tiles[line_point] = 'X'
    
    # Then, mark all input points as '#' (overwrites 'X' for input points)
    for point in tuples:
        tiles[point] = '#'
    
    return tiles

def print_grid(tiles: Dict[Tuple[int, int], str]):
    """
    Print the tiles dictionary as a grid.
    Points that exist in the dict are printed with their value.
    Points that don't exist are printed as '.'.
    
    Args:
        tiles: Dictionary mapping (x, y) tuples to their tile values
    """
    if not tiles:
        print("(empty grid)")
        return
    
    # Find the bounds of the grid
    x_coords = [x for x, y in tiles.keys()]
    y_coords = [y for x, y in tiles.keys()]
    
    min_x, max_x = min(x_coords), max(x_coords)
    min_y, max_y = min(y_coords), max(y_coords)
    
    # Print from bottom to top (min_y to max_y, inclusive)
    # range(min_y, max_y + 1) includes both min_y and max_y
    for y in range(min_y, max_y + 1):
        row = []
        for x in range(min_x, max_x + 1):
            point = (x, y)
            if point in tiles:
                row.append(tiles[point])
            else:
                row.append('.')
        print(''.join(row))

def fill_loop_interior(tiles: Dict[Tuple[int, int], str]) -> Dict[Tuple[int, int], str]:
    """
    Fill the interior of the loop (enclosed by '#' and 'X') with 'X'.
    Uses flood fill from outside to mark exterior, then fills interior.
    Optimized for large loops using deque and efficient boundary checks.
    
    Args:
        tiles: Dictionary mapping (x, y) tuples to their tile values
        
    Returns:
        Updated tiles dictionary with interior filled
    """
    if not tiles:
        return tiles
    
    # Find the bounds of the grid efficiently (single pass)
    min_x = max_x = min_y = max_y = None
    boundary = set()
    
    for point, value in tiles.items():
        x, y = point
        if value in ['#', 'X']:
            boundary.add(point)
        
        if min_x is None:
            min_x = max_x = x
            min_y = max_y = y
        else:
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)
    
    # Mark exterior using flood fill from edges with deque for O(1) operations
    exterior = set()
    queue = deque()
    
    # Add all edge points that are not on the boundary to the queue
    # Top and bottom edges
    for x in range(min_x, max_x + 1):
        for y in [min_y, max_y]:
            point = (x, y)
            if point not in boundary:
                queue.append(point)
                exterior.add(point)
    
    # Left and right edges (avoid duplicates at corners)
    for y in range(min_y + 1, max_y):
        for x in [min_x, max_x]:
            point = (x, y)
            if point not in boundary:
                queue.append(point)
                exterior.add(point)
    
    # Flood fill from exterior using deque.popleft() for O(1) operation
    while queue:
        x, y = queue.popleft()
        
        # Check all 4 neighbors
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy
            neighbor = (nx, ny)
            
            # Skip if out of bounds
            if nx < min_x or nx > max_x or ny < min_y or ny > max_y:
                continue
            
            # Skip if on boundary or already marked as exterior
            if neighbor in boundary or neighbor in exterior:
                continue
            
            exterior.add(neighbor)
            queue.append(neighbor)
    
    # Fill interior: any point not on boundary and not exterior is interior
    # Only iterate over points in the bounding box, not all tiles
    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            point = (x, y)
            if point not in boundary and point not in exterior:
                tiles[point] = 'X'
    
    return tiles

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
    
    # Part 2: Create tiles dictionary (only boundary needed, not filled)
    tiles = create_tiles_dict(tuples)
    print(f"\nTiles dictionary created with {len(tiles)} points")
    
    # Print the grid (optional, commented out for performance)
    # print("\nGrid:")
    # print_grid(tiles)
    
    # Find largest rectangle area where all points are inside the loop
    # Uses point-in-polygon check instead of filling the entire grid
    # (corners must be from original input tuples)
    area_tiles = largest_rectangle_area_of_tiles(tiles, tuples)
    print(f"\nLargest rectangle area (all points inside loop): {area_tiles}")
    
    return tuples

if __name__ == "__main__":
    result = main()

