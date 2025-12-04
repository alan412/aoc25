import argparse

def main():
    parser = argparse.ArgumentParser(description='Read file and find @ locations')
    parser.add_argument('file', type=str, help='Path to the input file')
    args = parser.parse_args()
    
    floor = {}
    max_row = -1
    max_col = -1
    with open(args.file, 'r') as f:
        for row, line in enumerate(f):
            line = line.rstrip('\n')  # Remove newline but keep other whitespace if needed
            max_row = max(max_row, row)
            for col, char in enumerate(line):
                max_col = max(max_col, col)
                if char == '@':
                    floor[(col, row)] = char  # or store any value you need
    
    return floor, max_row, max_col

def fewer_than_four_rolls(floor: dict, col: int, row: int) -> bool:
    num_rolls = -1
    for new_col in range(col - 1, col + 2):
        for new_row in range(row - 1, row + 2):
            if (new_col, new_row) in floor:
                num_rolls += 1
    return num_rolls < 4

if __name__ == "__main__":
    result, max_row, max_col = main()
    print(result)
    num_accessible = 0
    for row in range(max_row + 1):
        for col in range(max_col + 1):
            if (col, row) in result:
                if fewer_than_four_rolls(result, col, row):
                    num_accessible += 1
    print(num_accessible)