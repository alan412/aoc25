import argparse
import re
from typing import List, Set
from itertools import product

class Machine:
    def __init__(self, desired_lights: str, switches: List[Set[int]], joltages: List[int]):
        """
        Initialize a Machine.
        
        Args:
            desired_lights: String representing desired indicator lights (. = off, # = on)
            switches: List of sets, where each set contains the light indices affected by that switch
            joltages: List of joltage values
        """
        self.desired_lights = desired_lights
        self.switches = switches
        self.joltages = joltages
    
    def __repr__(self):
        switches_str = ' '.join(f"({','.join(map(str, sorted(s)))})" for s in self.switches)
        joltages_str = '{' + ','.join(map(str, self.joltages)) + '}'
        return f"Machine(desired=[{self.desired_lights}], switches={switches_str}, joltages={joltages_str})"
    
    def part1(self) -> int:
        """
        Find the minimum number of switches that need to be pressed to achieve the desired lights.
        Starts with all lights off, and each switch can be pressed 0 or 1 times.
        Pressing a switch XORs the light states at the positions in that switch.
        
        Returns:
            Minimum number of switches to press, or -1 if impossible
        """
        num_lights = len(self.desired_lights)
        num_switches = len(self.switches)
        
        min_switches = float('inf')
        
        # Try all combinations of switches (each switch: 0 = not pressed, 1 = pressed)
        for switch_combination in product([0, 1], repeat=num_switches):
            # Start with all lights off
            light_state = ['.'] * num_lights
            
            # Apply each switch if it's pressed (value is 1)
            for switch_idx, is_pressed in enumerate(switch_combination):
                if is_pressed:
                    # XOR the lights at positions in this switch
                    for light_pos in self.switches[switch_idx]:
                        if 0 <= light_pos < num_lights:
                            # Toggle the light (XOR: . becomes #, # becomes .)
                            light_state[light_pos] = '#' if light_state[light_pos] == '.' else '.'
            
            # Check if this matches the desired state
            if ''.join(light_state) == self.desired_lights:
                num_pressed = sum(switch_combination)
                min_switches = min(min_switches, num_pressed)
        
        return min_switches if min_switches != float('inf') else -1

def parse_machine(line: str) -> Machine:
    """
    Parse a line into a Machine object.
    
    Format: [lights] (switch1) (switch2) ... {joltages}
    """
    line = line.strip()
    if not line:
        return None
    
    # Extract desired lights (between [])
    lights_match = re.search(r'\[([.#]+)\]', line)
    if not lights_match:
        raise ValueError(f"Could not find desired lights in: {line}")
    desired_lights = lights_match.group(1)
    
    # Extract switches (each in parentheses)
    switch_pattern = r'\(([^)]+)\)'
    switch_matches = re.findall(switch_pattern, line)
    switches = []
    for switch_str in switch_matches:
        # Parse comma-separated light indices
        light_indices = [int(x.strip()) for x in switch_str.split(',')]
        switches.append(set(light_indices))
    
    # Extract joltages (between {})
    joltages_match = re.search(r'\{([^}]+)\}', line)
    if not joltages_match:
        raise ValueError(f"Could not find joltages in: {line}")
    joltages_str = joltages_match.group(1)
    joltages = [int(x.strip()) for x in joltages_str.split(',')]
    
    return Machine(desired_lights, switches, joltages)

def main():
    parser = argparse.ArgumentParser(description='Read machines from file')
    parser.add_argument('file', type=str, help='Path to the input file')
    args = parser.parse_args()
    
    machines = []
    
    with open(args.file, 'r') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if line:  # Skip empty lines
                try:
                    machine = parse_machine(line)
                    if machine:
                        machines.append(machine)
                except Exception as e:
                    print(f"Error parsing line {line_num}: {e}")
                    print(f"  Line: {line}")
    
    print(f"Read {len(machines)} machines:")
    for i, machine in enumerate(machines, 1):
        print(f"  {i}. {machine}")
    
    # Part 1: Find minimum switches for each machine
    print("\nPart 1 results:")
    total = 0
    for i, machine in enumerate(machines, 1):
        result = machine.part1()
        print(f"  Machine {i}: {result} switches")
        if result != -1:
            total += result
    
    print(f"\nTotal (sum of minimum switches): {total}")
    
    return machines

if __name__ == "__main__":
    machines = main()

