import argparse
import re
from typing import List, Set
from itertools import product
try:
    import z3
    from z3 import Int, Optimize, Sum, sat
except ImportError:
    raise ImportError("z3 is required. Install with: pip install z3-solver")

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
    
    def part2(self) -> int:
        """
        Find the minimum number of switches that need to be pressed to achieve the target joltages.
        Each press of a switch increases the joltage at the positions mentioned in the switch.
        Uses z3 to solve the system of equations and minimize the sum.
        
        Returns:
            Minimum number of switches to press, or -1 if impossible
        """
        num_positions = len(self.joltages)
        num_switches = len(self.switches)
        
        # Create z3 integer variables for each switch (number of times to press it)
        switches = [Int(f'switch_{i}') for i in range(num_switches)]
        
        # Create optimizer (better for minimization than regular solver)
        opt = Optimize()
        
        # Add constraints: each switch must be non-negative
        for switch in switches:
            opt.add(switch >= 0)
        
        # Add constraints: for each position, sum of presses of switches affecting it = target joltage
        for pos in range(num_positions):
            # Sum of presses for switches that affect this position
            affecting_switches = [switches[i] for i in range(num_switches) 
                                 if pos in self.switches[i]]
            if affecting_switches:
                opt.add(Sum(affecting_switches) == self.joltages[pos])
            else:
                # No switches affect this position, so target must be 0
                if self.joltages[pos] != 0:
                    return -1
        
        # Minimize the sum of all switch presses
        total_presses = Sum(switches)
        opt.minimize(total_presses)
        
        # Check if system is satisfiable
        if opt.check() != sat:
            return -1
        
        # Get the optimized solution
        model = opt.model()
        solution = [model[switch].as_long() for switch in switches]
        
        return sum(solution)
    
    def _solve_linear_system(self, A: List[List[int]], b: List[int]) -> List[int] | None:
        """
        Solve the system of linear equations Ax = b over integers.
        Uses a more robust approach that handles underdetermined systems better.
        Returns the solution vector x, or None if no solution exists.
        """
        n = len(A)  # number of equations (positions)
        m = len(A[0]) if A else 0  # number of variables (switches)
        
        if n == 0 or m == 0:
            return [0] * m if m > 0 else []
        
        # For underdetermined systems (more switches than positions), use a different approach
        # Try to find a solution by searching or using a simpler method
        if m > n:
            # Use a search-based approach for underdetermined systems
            return self._solve_underdetermined(A, b)
        
        # For determined or overdetermined systems, use Gaussian elimination
        # Create augmented matrix [A|b]
        aug = [row[:] + [b[i]] for i, row in enumerate(A)]
        
        # Track which columns have been used as pivots
        used_cols = set()
        pivot_rows = []  # (row, col) pairs
        
        # Gaussian elimination with row reduction
        for col in range(m):
            # Find a row with non-zero entry in this column
            for row in range(n):
                if row in [r for r, _ in pivot_rows]:
                    continue
                if aug[row][col] != 0:
                    pivot_rows.append((row, col))
                    used_cols.add(col)
                    
                    # Normalize pivot row (make pivot = 1 if possible, or keep as is)
                    pivot = aug[row][col]
                    
                    # Eliminate this column in other rows
                    for r in range(n):
                        if r != row and aug[r][col] != 0:
                            factor = aug[r][col]
                            # Use integer elimination: row_r = row_r * pivot - row * factor
                            for c in range(m + 1):
                                aug[r][c] = aug[r][c] * pivot - aug[row][c] * factor
                    break
        
        # Check for inconsistency - must check all rows, not just pivot rows
        for r in range(n):
            all_zero_coeffs = all(aug[r][c] == 0 for c in range(m))
            if all_zero_coeffs:
                if aug[r][m] != 0:
                    return None  # Inconsistent: 0 = non-zero
                # Otherwise 0 = 0, which is consistent (redundant equation)
        
        # Initialize solution
        x = [0] * m
        
        # Back substitution
        # Process pivot rows in reverse order
        for row, col in reversed(pivot_rows):
            rhs = aug[row][m]
            for c in range(col + 1, m):
                rhs -= aug[row][c] * x[c]
            
            if aug[row][col] == 0:
                if rhs != 0:
                    return None
                continue
            
            # Check divisibility
            if rhs % aug[row][col] != 0:
                return None
            
            x[col] = rhs // aug[row][col]
        
        # If we have free variables (not enough pivots), try to find a solution
        # by setting free variables and solving
        pivot_cols = {col for _, col in pivot_rows}
        free_vars = [c for c in range(m) if c not in pivot_cols]
        
        if free_vars:
            # We have free variables, need to search for a solution
            return self._solve_with_free_vars(A, b, aug, pivot_rows, free_vars, x)
        
        # Verify solution
        for i in range(n):
            total = sum(A[i][j] * x[j] for j in range(m))
            if total != b[i]:
                return None
        
        # If solution has negative values, try to find non-negative solution
        if any(val < 0 for val in x):
            null_space = self._find_null_space(A)
            adjusted = self._make_non_negative(x, null_space)
            if adjusted is None:
                return None
            
            # Verify adjusted solution
            for i in range(n):
                total = sum(A[i][j] * adjusted[j] for j in range(m))
                if total != b[i]:
                    return None
            
            return adjusted
        
        return x
    
    def _solve_with_free_vars(self, A: List[List[int]], b: List[int], aug: List[List[int]], 
                              pivot_rows: List[tuple], free_vars: List[int], partial_x: List[int]) -> List[int] | None:
        """
        Solve system when there are free variables after elimination.
        """
        m = len(A[0])
        max_target = max(b) if b else 0
        # Adaptive bounds based on number of free variables
        if len(free_vars) <= 2:
            max_free_val = min(200, max_target)
        elif len(free_vars) <= 4:
            max_free_val = min(100, max_target)
        else:
            max_free_val = min(50, max_target)
        
        from itertools import product
        
        # Try combinations of free variables
        for free_vals in product(range(max_free_val + 1), repeat=len(free_vars)):
            x = partial_x[:]
            
            # Set free variables
            for i, free_var in enumerate(free_vars):
                x[free_var] = free_vals[i]
            
            # Re-solve for pivot variables with new free variable values
            valid = True
            for row, col in reversed(pivot_rows):
                rhs = aug[row][m]
                for c in range(col + 1, m):
                    rhs -= aug[row][c] * x[c]
                
                if aug[row][col] == 0:
                    if rhs != 0:
                        valid = False
                        break
                    continue
                
                if rhs % aug[row][col] != 0:
                    valid = False
                    break
                
                x[col] = rhs // aug[row][col]
                
                if x[col] < 0:
                    valid = False
                    break
            
            if not valid:
                continue
            
            # Verify solution
            if all(val >= 0 for val in x):
                verify = True
                for i in range(len(A)):
                    if sum(A[i][j] * x[j] for j in range(m)) != b[i]:
                        verify = False
                        break
                if verify:
                    return x
        
        return None
    
    def _solve_underdetermined(self, A: List[List[int]], b: List[int]) -> List[int] | None:
        """
        Solve an underdetermined system (more variables than equations).
        Uses Gaussian elimination to reduce the system, then searches for solutions.
        """
        n = len(A)
        m = len(A[0])
        
        # Use Gaussian elimination to reduce the system
        # Create augmented matrix
        aug = [row[:] + [b[i]] for i, row in enumerate(A)]
        
        # Perform elimination to get row echelon form
        pivot_rows = []
        used_cols = set()
        
        for col in range(m):
            # Find pivot
            for row in range(n):
                if row in [r for r, _ in pivot_rows]:
                    continue
                if aug[row][col] != 0:
                    pivot_rows.append((row, col))
                    used_cols.add(col)
                    pivot = aug[row][col]
                    
                    # Eliminate
                    for r in range(n):
                        if r != row and aug[r][col] != 0:
                            factor = aug[r][col]
                            for c in range(m + 1):
                                aug[r][c] = aug[r][c] * pivot - aug[row][c] * factor
                    break
        
        # Check consistency
        for r in range(n):
            all_zero = all(aug[r][c] == 0 for c in range(m))
            if all_zero and aug[r][m] != 0:
                return None
        
        # Identify free variables (columns not used as pivots)
        pivot_cols = [col for _, col in pivot_rows]
        free_vars = [c for c in range(m) if c not in pivot_cols]
        
        # If no free variables, solve normally
        if not free_vars:
            x = [0] * m
            for row, col in reversed(pivot_rows):
                rhs = aug[row][m]
                for c in range(col + 1, m):
                    rhs -= aug[row][c] * x[c]
                if aug[row][col] == 0:
                    if rhs != 0:
                        return None
                    continue
                if rhs % aug[row][col] != 0:
                    return None
                x[col] = rhs // aug[row][col]
            
            # Verify
            for i in range(n):
                if sum(A[i][j] * x[j] for j in range(m)) != b[i]:
                    return None
            return x if all(val >= 0 for val in x) else None
        
        # For underdetermined systems, try setting free variables and solving
        # Use adaptive bounds based on target values
        max_target = max(b) if b else 0
        # Try values up to the maximum target, but limit search space
        # For many free variables, use smaller bounds to avoid explosion
        if len(free_vars) <= 3:
            max_free_val = min(100, max_target)
        elif len(free_vars) <= 5:
            max_free_val = min(50, max_target)
        else:
            max_free_val = min(20, max_target)
        
        from itertools import product
        
        # Try combinations of free variables, prioritizing smaller sums
        # Try increasing total bounds
        max_total = max_target * 2  # Reasonable upper bound
        
        # Try combinations of free variables
        for free_vals in product(range(max_free_val + 1), repeat=len(free_vars)):
            # Skip if sum is too large (heuristic to find smaller solutions first)
            if sum(free_vals) > max_total:
                continue
            # Set free variables
            x = [0] * m
            for i, free_var in enumerate(free_vars):
                x[free_var] = free_vals[i]
            
            # Solve for pivot variables
            valid = True
            for row, col in reversed(pivot_rows):
                rhs = aug[row][m]
                for c in range(col + 1, m):
                    rhs -= aug[row][c] * x[c]
                
                if aug[row][col] == 0:
                    if rhs != 0:
                        valid = False
                        break
                    continue
                
                if rhs % aug[row][col] != 0:
                    valid = False
                    break
                
                x[col] = rhs // aug[row][col]
                
                if x[col] < 0:
                    valid = False
                    break
            
            if not valid:
                continue
            
            # Verify solution
            if all(val >= 0 for val in x):
                verify = True
                for i in range(n):
                    if sum(A[i][j] * x[j] for j in range(m)) != b[i]:
                        verify = False
                        break
                if verify:
                    return x
        
        return None
    
    def _find_null_space(self, A: List[List[int]]) -> List[List[int]]:
        """
        Find a basis for the null space of A (solutions to Ax = 0).
        Returns a list of basis vectors.
        """
        n = len(A)
        m = len(A[0]) if A else 0
        
        if m == 0:
            return []
        
        # Build augmented matrix for Ax = 0
        aug = [row[:] for row in A]
        
        # Gaussian elimination
        row = 0
        pivot_cols = []
        
        for col in range(m):
            # Find pivot
            pivot_row = None
            for r in range(row, n):
                if aug[r][col] != 0:
                    pivot_row = r
                    break
            
            if pivot_row is None:
                continue
            
            if pivot_row != row:
                aug[row], aug[pivot_row] = aug[pivot_row], aug[row]
            
            pivot = aug[row][col]
            pivot_cols.append(col)
            
            # Eliminate
            for r in range(row + 1, n):
                if aug[r][col] != 0:
                    factor = aug[r][col]
                    for c in range(col, m):
                        aug[r][c] = aug[r][c] * pivot - aug[row][c] * factor
            
            row += 1
        
        # Find free variables (columns not in pivot_cols)
        free_vars = [c for c in range(m) if c not in pivot_cols]
        
        null_space = []
        for free_var in free_vars:
            # Set this free variable to 1, others to 0, solve for pivot variables
            vec = [0] * m
            vec[free_var] = 1
            
            # Back substitute
            for r in range(len(pivot_cols) - 1, -1, -1):
                pivot_col = pivot_cols[r]
                rhs = -sum(aug[r][c] * vec[c] for c in range(pivot_col + 1, m))
                if aug[r][pivot_col] == 0:
                    continue
                if rhs % aug[r][pivot_col] != 0:
                    continue  # Skip if not integer
                vec[pivot_col] = rhs // aug[r][pivot_col]
            
            # Verify it's in null space
            if all(sum(A[i][j] * vec[j] for j in range(m)) == 0 for i in range(n)):
                null_space.append(vec)
        
        return null_space
    
    def _minimize_solution(self, A: List[List[int]], b: List[int], initial_solution: List[int]) -> List[int] | None:
        """
        Find the solution with minimum sum by exploring the null space.
        """
        null_space = self._find_null_space(A)
        
        if not null_space:
            # No null space, initial solution is unique
            return initial_solution if all(x >= 0 for x in initial_solution) else None
        
        # Start with initial solution
        best = initial_solution if all(x >= 0 for x in initial_solution) else None
        best_sum = sum(initial_solution) if best else float('inf')
        
        # Search through null space combinations to minimize sum
        # Use a more systematic approach: try linear combinations of null space vectors
        num_null = len(null_space)
        
        # Start with initial solution (make it non-negative first if needed)
        if not all(x >= 0 for x in initial_solution):
            initial_solution = self._make_non_negative(initial_solution, null_space)
            if initial_solution is None:
                return None
            best = initial_solution
            best_sum = sum(initial_solution)
        
        # Try combinations of null space vectors to reduce sum
        # Limit the search space by bounding the coefficients
        max_coeff = 20  # Reasonable bound
        
        # Try all combinations within bounds
        for coeffs in product(range(-max_coeff, max_coeff + 1), repeat=min(num_null, 2)):
            if sum(abs(c) for c in coeffs) > max_coeff * 2:  # Skip if too large
                continue
            
            candidate = initial_solution[:]
            for i, coeff in enumerate(coeffs):
                if i < num_null:
                    for j in range(len(candidate)):
                        candidate[j] += coeff * null_space[i][j]
            
            # Check if valid (non-negative and satisfies equations)
            if all(x >= 0 for x in candidate):
                # Verify it still satisfies Ax = b
                valid = True
                for i in range(len(A)):
                    total = sum(A[i][j] * candidate[j] for j in range(len(candidate)))
                    if total != b[i]:
                        valid = False
                        break
                
                if valid:
                    total_sum = sum(candidate)
                    if total_sum < best_sum:
                        best = candidate
                        best_sum = total_sum
        
        return best
    
    def _make_non_negative(self, x: List[int], null_space: List[List[int]]) -> List[int] | None:
        """
        Try to adjust solution x using null space vectors to make it non-negative.
        Returns adjusted solution or None if not possible.
        """
        if all(val >= 0 for val in x):
            return x
        
        if not null_space:
            # No null space, can't adjust
            return None
        
        # Try to find coefficients to add to null space vectors
        # We want: x + sum(alpha_i * null_space[i]) >= 0 for all components
        # And minimize sum(x + ...)
        
        # For simplicity, try small integer combinations
        # This is a heuristic - a full implementation would use integer linear programming
        best = None
        best_sum = float('inf')
        
        # Try combinations of null space vectors
        max_tries = 1000  # Limit search
        tries = 0
        
        # Try adding/subtracting null space vectors
        for signs in product([-1, 0, 1], repeat=min(len(null_space), 3)):  # Limit to 3 null space vectors
            if tries >= max_tries:
                break
            tries += 1
            
            adjusted = x[:]
            for i, sign in enumerate(signs):
                if i < len(null_space) and sign != 0:
                    for j in range(len(adjusted)):
                        adjusted[j] += sign * null_space[i][j]
            
            # Check if non-negative
            if all(val >= 0 for val in adjusted):
                total = sum(adjusted)
                if total < best_sum:
                    best = adjusted
                    best_sum = total
        
        return best

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
    
    # Part 2: Find minimum switches for joltages using linear algebra
    print("\nPart 2 results:")
    total2 = 0
    for i, machine in enumerate(machines, 1):
        result = machine.part2()
        print(f"  Machine {i}: {result} switches")
        if result != -1:
            total2 += result
    
    print(f"\nTotal (sum of minimum switches): {total2}")
    
    return machines

if __name__ == "__main__":
    machines = main()

