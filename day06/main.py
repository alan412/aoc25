import argparse

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

def operate(numbers : list[int], operator) -> int:
    result = 0
    for number in numbers:
        if operator == '+':
            result += number
        elif operator == '*':
            if result == 0:
                result = 1
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