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

def remove_fewer_than_four_rolls(floor: dict) -> (int, dict):
    to_delete = {}
    for col, row in floor:
        if fewer_than_four_rolls(floor, col, row):
            to_delete[(col, row)] = True
    for col, row in to_delete:
        del floor[(col, row)]
    return len(to_delete), floor

if __name__ == "__main__":
    spaces, max_row, max_col = main()

    num_accessible = 0
    total = 0
    (num_removed, spaces) = remove_fewer_than_four_rolls(spaces)
    print(num_removed)
    while (num_removed > 0):
        total += num_removed
        (num_removed, spaces) = remove_fewer_than_four_rolls(spaces)
        print(num_removed)
    print(total)