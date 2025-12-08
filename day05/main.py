import argparse

def main():
    parser = argparse.ArgumentParser(description='Read ranges and ingredients from file')
    parser.add_argument('file', type=str, help='Path to the input file')
    args = parser.parse_args()
    
    ranges = []
    ingredients = []
    
    with open(args.file, 'r') as f:
        # Read ranges until we hit a blank line
        for line in f:
            line = line.strip()
            if not line:
                break  # Blank line found, switch to ingredients
            
            # Parse range in format "start-end"
            parts = line.split('-')
            if len(parts) == 2:
                start = int(parts[0])
                end = int(parts[1])
                ranges.append((start, end))
        
        # Read ingredients (remaining lines)
        for line in f:
            line = line.strip()
            if line:
                ingredients.append(int(line))
    
    return ranges, ingredients

def is_ingredient_in_range(ingredient : int, range : tuple[int, int]) -> bool:
    return ingredient >= range[0] and ingredient <= range[1]

if __name__ == "__main__":
    ranges, ingredients = main()
    print(f"Ranges: {ranges}")
    print(f"Ingredients: {ingredients}")
    number_not_in_range = 0
    for ingredient in ingredients:
        for range in ranges:
            if is_ingredient_in_range(ingredient, range):
                print(f"Ingredient {ingredient} is in range {range}")
                break
        else:
            print(f"Ingredient {ingredient} is not in any range")
            number_not_in_range += 1
    print(f"Number of ingredients not in range: {number_not_in_range}")
    print(f"Total: {len(ingredients) - number_not_in_range}")