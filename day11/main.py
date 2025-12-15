import argparse
from typing import List, Dict
from functools import cache


def solve_pt1(data: Dict[str, List[str]], start: str = "you", end: str = "out") -> List[List[str]]:
    """
    Find all possible paths from start node to end node in the graph.
    Uses memoization to cache paths from each node to the end.
    
    Args:
        data: Dictionary mapping nodes to their neighbors
        start: Starting node (default: "you")
        end: Target node (default: "out")
    
    Returns:
        List of all paths, where each path is a list of nodes from start to end
    """
    # Memoization cache: (current_node, frozenset(visited_nodes)) -> list of path suffixes
    # Each cached path is a list of nodes from current to end (inclusive)
    memo = {}
    
    def dfs(current: str, visited: set) -> List[List[str]]:
        """
        Returns all paths from current to end (as list of node lists).
        Each path includes current and end nodes.
        """
        # Create a key for memoization (using frozenset for visited nodes)
        memo_key = (current, frozenset(visited))
        
        # Check memoization cache
        if memo_key in memo:
            return memo[memo_key]
        
        all_paths = []
        
        # If we've reached the target, return a path with just the end node
        if current == end:
            all_paths.append([end])
            memo[memo_key] = all_paths
            return all_paths
        
        # If current node has no neighbors, we can't continue
        if current not in data:
            memo[memo_key] = []
            return []
        
        # Explore all neighbors
        for neighbor in data[current]:
            # Avoid cycles by checking if we've already visited this neighbor
            if neighbor not in visited:
                visited.add(neighbor)
                # Get all paths from neighbor to end
                neighbor_paths = dfs(neighbor, visited)
                visited.remove(neighbor)  # Backtrack
                
                # Prepend current node to each path from neighbor
                for neighbor_path in neighbor_paths:
                    all_paths.append([current] + neighbor_path)
        
        # Cache the results
        memo[memo_key] = all_paths
        return all_paths
    
    # Start DFS from the start node
    visited = {start}
    result_paths = dfs(start, visited)
    
    return result_paths

connections = {}

@cache
def dfs_with_requirements(device: str, fft: bool, dac: bool) -> int:
    if device == "out":
        return 1 if fft and dac else 0
    if (outputs := connections.get(device)) is None:
        return 0
    if device == "fft":
        fft = True
    if device == "dac":
        dac = True
    return sum(dfs_with_requirements(output, fft, dac) for output in outputs)

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

    # Part 2: Count paths from "svr" to "out" that visit both "dac" and "fft"
    print(f"\nPart 2: Counting paths from 'svr' to 'out' that visit both 'dac' and 'fft'")
    global connections
    connections = data
    dac_fft_count = dfs_with_requirements("svr", False, False)
    print(f"Paths visiting both 'dac' and 'fft': {dac_fft_count}")
    return data


if __name__ == "__main__":
    result = main()

