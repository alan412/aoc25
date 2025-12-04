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
        jolts = calculate_jolts(battery)
        print(battery, jolts)
        total_jolts += jolts

    print(total_jolts)
