import argparse
import re

def main():
    parser = argparse.ArgumentParser(description='Read numbers and operators from file')
    parser.add_argument('file', type=str, help='Path to the input file')
    args = parser.parse_args()
    
    numbers = []
    operators = []
    
    with open(args.file, 'r') as f:
        lines = f.readlines()
        
        # Process all lines except the last one as numbers
        for line in lines[:-1]:
            line = line.strip()
            # Split by whitespace and convert to ints for this line
            line_numbers = []
            for num_str in line.split():
                if num_str:  # Skip empty strings
                    line_numbers.append(int(num_str))
            if line_numbers:  # Only add non-empty lists
                numbers.append(line_numbers)
        
        # Process the last line as operators (strings)
        last_line = lines[-1].strip()
        for op_str in last_line.split():
            if op_str:  # Skip empty strings
                operators.append(op_str)
    
    return numbers, operators

def main_strings():
    parser = argparse.ArgumentParser(description='Read numbers and operators from file')
    parser.add_argument('file', type=str, help='Path to the input file')
    args = parser.parse_args()
    
    numbers = []
    operators = []
    import re
    
    with open(args.file, 'r') as f:
        lines = f.readlines()
        
        # First pass: find all numbers and their positions
        all_matches = []
        for line in lines[:-1]:
            line = line.rstrip('\n')
            matches = list(re.finditer(r'\d+', line))
            all_matches.append(matches)
        
        # Determine column boundaries by finding the leftmost start position for each column
        num_columns = max(len(matches) for matches in all_matches) if all_matches else 0
        column_starts = []
        for col_idx in range(num_columns):
            min_start = float('inf')
            for matches in all_matches:
                if col_idx < len(matches):
                    min_start = min(min_start, matches[col_idx].start())
            column_starts.append(int(min_start))
        
        # Also find where each column ends (rightmost end position)
        column_ends = []
        for col_idx in range(num_columns):
            max_end = 0
            for matches in all_matches:
                if col_idx < len(matches):
                    max_end = max(max_end, matches[col_idx].end())
            column_ends.append(max_end)
        
        # Second pass: extract numbers with their own leading/trailing spaces
        for line_idx, line in enumerate([l.rstrip('\n') for l in lines[:-1]]):
            number_strings = []
            matches = all_matches[line_idx]
            
            for col_idx, match in enumerate(matches):
                num_start = match.start()
                num_end = match.end()
                
                # Leading spaces: from column start (leftmost) to number start
                col_start = column_starts[col_idx]
                leading_spaces = line[col_start:num_start] if col_start < num_start else ''
                
                # Trailing spaces: from number end to next column start (or end of line for last column)
                if col_idx < len(column_starts) - 1:
                    next_col_start = column_starts[col_idx + 1]
                    # Take spaces up to next column start
                    trailing_end = min(next_col_start, len(line))
                else:
                    # Last column: take all trailing spaces to end of line
                    trailing_end = len(line)
                
                # Extract trailing spaces (only consecutive spaces after the number)
                trailing_spaces = ''
                for i in range(num_end, trailing_end):
                    if line[i] == ' ':
                        trailing_spaces += ' '
                    else:
                        break
                
                number_with_spaces = leading_spaces + line[num_start:num_end] + trailing_spaces
                number_strings.append(number_with_spaces)
            
            if number_strings:
                numbers.append(number_strings)
        
        # Process the last line as operators (strings)
        last_line = lines[-1].strip()
        for op_str in last_line.split():
            if op_str:
                operators.append(op_str)
    
    return numbers, operators

def operate(numbers : list[int], operator) -> int:
    result = 0 if operator == '+' else 1
    for number in numbers:
        if operator == '+':
            result += number
        elif operator == '*':
            result *= number
    return result


if __name__ == "__main__":
    numbers, operators = main()
    print(f"Numbers: {numbers}")
    print(f"Operators: {operators}")

    total = 0
    for i, operator in enumerate(operators):
        new_list = []
        for number in numbers:
            new_list.append(number[i])
        result = operate(new_list, operator)
        print(f"Result: {result, operator, numbers}")
        total += result
    print(f"Part 1 {total}")
    
    # Part 2: Read as strings and process columns right to left
    numbers_str, operators = main_strings()
    print(f"Numbers - Part 2: {numbers_str}")
    total2 = 0
    
    for i, operator in enumerate(operators):
        new_list = []
        # Get all numbers in this column
        col_numbers = []
        for row in numbers_str:
            if i < len(row):
                col_numbers.append(row[i])
        
        if not col_numbers:
            continue
        
        # Find maximum length (for right alignment)
        max_len = max(len(num) for num in col_numbers)
        
        # Build numbers by reading digits from right to left, one position at a time
        # Numbers are right-aligned, so we read from the rightmost position
        # Skip spaces - only include digits
        for pos in range(max_len):
            digits = []
            for num_str in col_numbers:
                # Get digit at position pos from the right (0 = rightmost)
                pos_from_right = len(num_str) - 1 - pos
                if pos_from_right >= 0:
                    char = num_str[pos_from_right]
                    # Only add if it's a digit, skip spaces
                    if char.isdigit():
                        digits.append(char)
            # Form number from these digits (top to bottom order)
            # Only create a number if we have at least one digit
            if digits:
                num = int(''.join(digits))
                new_list.append(num)
        
        result = operate(new_list, operator)
        print(f"Part 2 Column {i}: {new_list} {operator} = {result}")
        total2 += result
    print(f"Part 2 Total: {total2}")