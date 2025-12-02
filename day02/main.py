import argparse
from collections import namedtuple

Range = namedtuple('Range', ['first', 'last'])

def is_repeat(number: int) -> bool:
    # return True if the number can be made up of the same sequence of digits repeated only twice
    number_str = str(number)
    size = len(number_str)
    if size % 2 != 0:
        return False;
    if int(number_str[:size//2]) == int(number_str[size//2:]):
        if number_str[size//2] != '0':
            return True
    return False

def number_of_repeats(ranges: list[Range]) -> int:
    count = 0   
    # return the number of items in the range that can be made up of the same sequence of digits repeated only twice
    for test_range in ranges:
        for i in range(test_range.first, test_range.last + 1):
            if is_repeat(i):
                print(f"Found {i}")
                count += i
    return count

def main():
    parser = argparse.ArgumentParser(description='Read and parse range file')
    parser.add_argument('file', type=str, help='Path to the input file')
    args = parser.parse_args()
    
    data = []
    with open(args.file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            # Split by commas to get individual ranges
            ranges = line.split(',')
            for range_str in ranges:
                # Split by dash to get first and last
                parts = range_str.split('-')
                if len(parts) == 2:
                    first = int(parts[0])
                    last = int(parts[1])
                    data.append(Range(first=first, last=last))
    
    return data

if __name__ == "__main__":
    result = main()
    print(number_of_repeats(result))
