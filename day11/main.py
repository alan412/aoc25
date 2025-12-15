import argparse
from typing import List, Dict


def solve_pt1(data: Dict[str, List[str]], start: str = "you", end: str = "out") -> List[List[str]]:
    """
    Find all possible paths from start node to end node in the graph.
    
    Args:
        data: Dictionary mapping nodes to their neighbors
        start: Starting node (default: "you")
        end: Target node (default: "out")
    
    Returns:
        List of all paths, where each path is a list of nodes from start to end
    """
    all_paths = []
    
    def dfs(current: str, path: List[str], visited: set):
        """Depth-first search to find all paths from current to end."""
        # Add current node to path
        path = path + [current]
        
        # If we've reached the target, save this path
        if current == end:
            all_paths.append(path)
            return
        
        # If current node has no neighbors, we can't continue
        if current not in data:
            return
        
        # Explore all neighbors
        for neighbor in data[current]:
            # Avoid cycles by checking if we've already visited this neighbor
            if neighbor not in visited:
                visited.add(neighbor)
                dfs(neighbor, path, visited)
                visited.remove(neighbor)  # Backtrack
    
    # Start DFS from the start node
    visited = {start}
    dfs(start, [], visited)
    
    return all_paths


def main():
    parser = argparse.ArgumentParser(description='Read key-value pairs from file')
    parser.add_argument('file', type=str, help='Path to the input file')
    args = parser.parse_args()
    
    data = {}
    
    with open(args.file, 'r') as f:
        for line in f:
            line = line.strip()
            if line:  # Skip empty lines
                if ':' in line:
                    key, value_str = line.split(':', 1)
                    key = key.strip()
                    # Split the value string by spaces and filter out empty strings
                    values = [v.strip() for v in value_str.split() if v.strip()]
                    data[key] = values
    
    # Print the resulting dictionary
    print("Parsed data:")
    for key, values in data.items():
        print(f"  {key}: {values}")
    
    # Find all paths from "you" to "out"
    print("\nPart 1: Finding all paths from 'you' to 'out'")
    paths = solve_pt1(data)
    print(f"Found {len(paths)} path(s):")
    for i, path in enumerate(paths, 1):
        print(f"  {i}. {' -> '.join(path)}")
    print(f"Found {len(paths)} path(s):")

    return data


if __name__ == "__main__":
    result = main()

