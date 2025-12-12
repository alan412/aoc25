import argparse
import math
import heapq
from typing import List, Tuple, Set, Dict

class JunctionBox:
    def __init__(self, x: int, y: int, z: int):
        self.x = x
        self.y = y
        self.z = z
    
    def __repr__(self):
        return f"JunctionBox(x={self.x}, y={self.y}, z={self.z})"
    
    def distance_squared(self, other: 'JunctionBox') -> float:
        """
        Calculate the squared distance between this JunctionBox and another.
        """
        dx = other.x - self.x
        dy = other.y - self.y
        dz = other.z - self.z
        return dx * dx + dy * dy + dz * dz
    
    def __hash__(self):
        """Make JunctionBox hashable for use in sets."""
        return hash((self.x, self.y, self.z))
    
    def __eq__(self, other):
        """Equality comparison for JunctionBox."""
        if not isinstance(other, JunctionBox):
            return False
        return self.x == other.x and self.y == other.y and self.z == other.z

class CircuitManager:
    """
    Manages circuits (connected components) of junction boxes.
    Uses union-find data structure for efficient connectivity checks and merging.
    """
    
    def __init__(self):
        """Initialize an empty circuit manager."""
        # Union-find data structure: maps each box to its parent
        self.parent: Dict[JunctionBox, JunctionBox] = {}
        # Track the size of each circuit for union by rank optimization
        self.rank: Dict[JunctionBox, int] = {}
    
    def _find(self, box: JunctionBox) -> JunctionBox:
        """
        Find the root of the circuit containing this box (with path compression).
        """
        if box not in self.parent:
            self.parent[box] = box
            self.rank[box] = 0
            return box
        
        if self.parent[box] != box:
            # Path compression: make parent point directly to root
            self.parent[box] = self._find(self.parent[box])
        return self.parent[box]
    
    def _union(self, box1: JunctionBox, box2: JunctionBox) -> bool:
        """
        Merge the circuits containing box1 and box2.
        Returns True if they were in different circuits (merge occurred),
        False if they were already in the same circuit.
        """
        root1 = self._find(box1)
        root2 = self._find(box2)
        
        if root1 == root2:
            # Already in the same circuit
            return False
        
        # Union by rank: attach smaller tree under larger tree
        if self.rank[root1] < self.rank[root2]:
            self.parent[root1] = root2
        elif self.rank[root1] > self.rank[root2]:
            self.parent[root2] = root1
        else:
            self.parent[root2] = root1
            self.rank[root1] += 1
        
        return True
    
    def are_in_same_circuit(self, box1: JunctionBox, box2: JunctionBox) -> bool:
        """
        Check if two junction boxes are already in the same circuit.
        """
        return self._find(box1) == self._find(box2)
    
    def add_pairs(self, closest_pairs: List[Tuple[Tuple[JunctionBox, JunctionBox], float]]) -> int:
        """
        Add pairs from closest_pairs to circuits if they aren't already in the same circuit.
        
        Args:
            closest_pairs: List of tuples, each containing ((box1, box2), distance_squared)
            
        Returns:
            Number of pairs that were actually added (i.e., connected different circuits)
        """
        added_count = 0
        for (box1, box2), _ in closest_pairs:
            if self._union(box1, box2):
                added_count += 1
        return added_count
    
    def get_circuits(self) -> List[Set[JunctionBox]]:
        """
        Get all circuits as a list of sets of junction boxes.
        
        Returns:
            List of sets, where each set contains all junction boxes in that circuit
        """
        # Group boxes by their root
        circuits_dict: Dict[JunctionBox, Set[JunctionBox]] = {}
        
        # Collect all boxes that have been added
        all_boxes = set(self.parent.keys())
        
        for box in all_boxes:
            root = self._find(box)
            if root not in circuits_dict:
                circuits_dict[root] = set()
            circuits_dict[root].add(box)
        
        return list(circuits_dict.values())
    
    def get_circuit_count(self) -> int:
        """
        Get the number of distinct circuits.
        """
        roots = set()
        for box in self.parent.keys():
            roots.add(self._find(box))
        return len(roots)
    
    def get_top_3_circuit_lengths(self) -> List[int]:
        """
        Get the lengths (number of junction boxes) of the 3 biggest circuits.
        
        Returns:
            List of integers representing the lengths of the top 3 circuits,
            sorted in descending order. If there are fewer than 3 circuits,
            returns all circuit lengths. If there are no circuits, returns empty list.
        """
        circuits = self.get_circuits()
        if not circuits:
            return []
        
        # Get the sizes of all circuits
        circuit_sizes = [len(circuit) for circuit in circuits]
        
        # Use heapq.nlargest for efficiency (O(k log n) where k=3, n=number of circuits)
        # This is more efficient than sorting all circuits when we only need top 3
        top_3 = heapq.nlargest(3, circuit_sizes)
        
        return top_3
    
    def are_all_boxes_connected(self, all_boxes: List[JunctionBox]) -> bool:
        """
        Check if all boxes from the given list are in a single circuit.
        
        Args:
            all_boxes: List of all junction boxes that should be connected
            
        Returns:
            True if all boxes are in the same circuit, False otherwise
        """
        if not all_boxes:
            return True
        
        if len(all_boxes) == 1:
            return True
        
        # Check if all boxes are in the parent dict (have been added to circuits)
        for box in all_boxes:
            if box not in self.parent:
                return False
        
        # Check if all boxes have the same root
        first_root = self._find(all_boxes[0])
        for box in all_boxes[1:]:
            if self._find(box) != first_root:
                return False
        
        return True

def find_closest_pairs(junction_boxes: List[JunctionBox], n: int) -> List[Tuple[Tuple[JunctionBox, JunctionBox], float]]:
    """
    Find the n pairs of junction boxes that are closest together.
    
    This method is optimized for large lists by using a heap-based approach
    that avoids sorting all pairs. Time complexity: O(m² log n) where m is
    the number of junction boxes, which is better than O(m² log m²) for
    full sorting when n << m².
    
    Args:
        junction_boxes: List of JunctionBox objects
        n: Number of closest pairs to return
        
    Returns:
        List of tuples, each containing ((box1, box2), distance_squared)
        sorted by distance (closest first)
    """
    if len(junction_boxes) < 2:
        return []
    
    if n <= 0:
        return []
    
    # Generate all pairs with their distances
    # Use a generator to avoid storing all pairs in memory at once
    def pair_generator():
        for i in range(len(junction_boxes)):
            for j in range(i + 1, len(junction_boxes)):
                box1 = junction_boxes[i]
                box2 = junction_boxes[j]
                distance_sq = box1.distance_squared(box2)
                yield (distance_sq, (box1, box2))
    
    # Use heapq.nsmallest() which is optimized for finding n smallest items
    # This uses a heap internally and is more efficient than sorting all pairs
    closest = heapq.nsmallest(n, pair_generator(), key=lambda x: x[0])
    
    # Return as list of ((box1, box2), distance_squared) tuples
    return [((box1, box2), dist_sq) for dist_sq, (box1, box2) in closest]

def main():
    parser = argparse.ArgumentParser(description='Read junction boxes from file')
    parser.add_argument('file', type=str, help='Path to the input file')
    args = parser.parse_args()
    
    junction_boxes = []
    
    with open(args.file, 'r') as f:
        for line in f:
            line = line.strip()
            if line:  # Skip empty lines
                parts = line.split(',')
                if len(parts) == 3:
                    x = int(parts[0])
                    y = int(parts[1])
                    z = int(parts[2])
                    junction_boxes.append(JunctionBox(x, y, z))
    
    print(f"Read {len(junction_boxes)} junction boxes:")
    
    return junction_boxes

if __name__ == "__main__":
    boxes = main()
    
    # Find the closest pairs (using a large number to ensure we have enough)
    closest_pairs = find_closest_pairs(boxes, 6000)
    print(f"\nFound {len(closest_pairs)} closest pairs")
    
    # Process pairs incrementally to find when all boxes connect
    manager = CircuitManager()
    last_connection = None
    
    for (box1, box2), dist_sq in closest_pairs:
        # Check if all boxes are connected before adding this pair
        was_connected_before = manager.are_all_boxes_connected(boxes)
        
        # Add this pair to the circuit
        manager._union(box1, box2)
        
        # Check if all boxes are now in a single circuit
        is_connected_after = manager.are_all_boxes_connected(boxes)
        
        if not was_connected_before and is_connected_after:
            # This is the connection that completed the circuit
            last_connection = ((box1, box2), dist_sq)
            distance = math.sqrt(dist_sq)
            print(f"\nLast connection that completes the circuit:")
            print(f"  Box 1: {box1}")
            print(f"  Box 2: {box2}")
            print(f"  Distance: {distance:.2f} (squared: {dist_sq})")
            break
    
    # Create circuit manager and add pairs to circuits for part 1
    manager_part1 = CircuitManager()
    added_count = manager_part1.add_pairs(closest_pairs)
    print(f"\nAdded {added_count} pairs to circuits")
    
    # Get the lengths of the 3 longest circuits
    top_3_lengths = manager_part1.get_top_3_circuit_lengths()
    print(f"\nLengths of the 3 longest circuits: {top_3_lengths}")
    
    # Multiply them together for part 1 answer
    if len(top_3_lengths) == 3:
        answer = top_3_lengths[0] * top_3_lengths[1] * top_3_lengths[2]
        print(f"\nPart 1 answer: {answer}")
    else:
        print(f"\nWarning: Only {len(top_3_lengths)} circuits found, cannot compute part 1 answer")
    

