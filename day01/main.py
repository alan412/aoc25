import argparse


def turn_dial(direction: str, number: int, current_position: int) -> int:
    if direction == "left":
        current_position = (current_position - number) % 100
    else:
        current_position = (current_position + number) % 100
    return current_position

def turn_dial2(direction: str, number: int, current_position: int) -> int:
    crossings = 0
    print(f"Before: {current_position} - {direction} {number}")
    if direction == "left":
        while number > 0:
            if current_position == 0:
                number -= 1
                current_position = 99
                continue
            to_zero = min(number, current_position)
            number -= to_zero
            current_position -= to_zero
            if number > 0 and current_position == 0:
                crossings += 1
    else:
        while number > 0:
            to_zero = min(number, 99 - current_position)
            number -= to_zero
            current_position += to_zero
            if number > 0 and current_position == 0:
                crossings += 1
            if number > 0 and current_position == 99:
                number -= 1
                current_position = 0
                if number > 0:
                    crossings += 1
    print(f"After: {current_position} {crossings}")

    return current_position, crossings

def main():
    parser = argparse.ArgumentParser(description='Read and parse direction file')
    parser.add_argument('file', type=str, help='Path to the input file')
    args = parser.parse_args()
    
    data = []
    with open(args.file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            # Parse the direction and number
            direction = line[0].upper()
            number = int(line[1:])
            
            # Convert L/R to left/right
            direction_str = "left" if direction == "L" else "right"
            
            data.append((direction_str, number))
    
    return data

if __name__ == "__main__":
    result = main()
    current_position = 50
    times = 0
    total_crossings = 0
    for direction, number in result:
        current_position, crossings = turn_dial2(direction, number, current_position)
        total_crossings += crossings
        if current_position == 0:
            times += 1
    print(times)
    print(times + total_crossings)
