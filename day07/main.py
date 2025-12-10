import argparse
from collections import deque

def beam(s_position: tuple[int, int], carets: dict, max_row: int, max_col: int) -> int:
    """
    Simulates a beam starting from S position going down.
    When it hits a '^', it splits into left and right beams.
    Returns the number of times the beam splits.
    """
    if s_position is None:
        return 0
    
    # Queue to track active beam positions
    queue = deque([s_position])
    # Set to track visited positions (only first visit matters)
    visited = set()
    split_count = 0
    
    while queue:
        row, col = queue.popleft()
        
        # Skip if already visited
        if (row, col) in visited:
            continue
        
        # Mark as visited
        visited.add((row, col))
        
        # Check if we're out of bounds
        if row >= max_row or col < 0 or col >= max_col:
            continue
        
        # Check if we hit a '^'
        if (row, col) in carets:
            split_count += 1
            # Split into left and right (both continue going down from their new positions)
            left_pos = (row, col - 1)
            right_pos = (row, col + 1)
            
            # Add left beam if in bounds and not visited
            if left_pos[1] >= 0 and left_pos not in visited:
                queue.append(left_pos)
            
            # Add right beam if in bounds and not visited
            if right_pos[1] < max_col and right_pos not in visited:
                queue.append(right_pos)
        else:
            # Continue going down if we didn't hit a '^'
            next_pos = (row + 1, col)
            if next_pos[0] < max_row and next_pos not in visited:
                queue.append(next_pos)
    
    return split_count


def main():
    parser = argparse.ArgumentParser(description='Parse grid file for S and ^ characters')
    parser.add_argument('file', type=str, help='Path to the input file')
    args = parser.parse_args()
    
    s_position = None
    carets = {}  # dict with key (row, col) and value '^'
    
    with open(args.file, 'r') as f:
        lines = f.readlines()
        
        max_row = len(lines)
        max_col = len(lines[0].rstrip('\n')) if lines else 0
        
        for row, line in enumerate(lines):
            line = line.rstrip('\n')
            for col, char in enumerate(line):
                if char == 'S':
                    s_position = (row, col)
                elif char == '^':
                    carets[(row, col)] = '^'
    
    print(f"S position: {s_position}")
    print(f"Carets: {carets}")
    
    # Call the beam method
    splits = beam(s_position, carets, max_row, max_col)
    print(f"Number of splits: {splits}")
    
    return s_position, carets

if __name__ == "__main__":
    s_pos, carets_dict = main()
