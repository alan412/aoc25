import argparse


def find_highest_val(battery: str) -> (int, int):
    highest_val = '0'
    highest_pos = -1
    for i in range(len(battery)):
        if battery[i] > highest_val:
            highest_val = battery[i]
            highest_pos = i
    return highest_val, highest_pos

def calculate_jolts(battery: str) -> int:
    high_val, high_pos = find_highest_val(battery[:-1])  # Exclude last position
    next_val, next_pos = find_highest_val(battery[high_pos + 1:])
    return int(high_val) * 10 + int(next_val)

def calculate_jolts_2(battery: str) -> int:
    if len(battery) < 12:
        return 0
    
    result = []
    n = len(battery)
    k = 12
    start = 0
    
    # Greedily select digits: at each position, pick the largest digit
    # that still leaves enough digits to complete the selection
    for i in range(k):
        # We need to leave at least (k - i - 1) digits after this one
        end = n - (k - i - 1)
        # Find the maximum digit in the available range
        max_digit = '0'
        max_pos = start
        for j in range(start, end):
            if battery[j] > max_digit:
                max_digit = battery[j]
                max_pos = j
        result.append(max_digit)
        start = max_pos + 1
    
    return int(''.join(result))


def main():
    parser = argparse.ArgumentParser(description='Read numbers from file')
    parser.add_argument('file', type=str, help='Path to the input file')
    args = parser.parse_args()
    
    data = []
    with open(args.file, 'r') as f:
        for line in f:
            line = line.strip()
            if line:  # Only add non-empty lines
                data.append(line)
    
    return data

if __name__ == "__main__":
    result = main()
    total_jolts = 0
    for battery in result:
        jolts = calculate_jolts_2(battery)
        print(battery, jolts)
        total_jolts += jolts

    print(total_jolts)
