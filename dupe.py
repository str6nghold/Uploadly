import os
import random
from PIL import Image


def get_folder():
    while True:
        folder = input("Enter the folder path: ").strip()
        if os.path.isdir(folder):
            return folder
        else:
            print("Invalid folder. Please try again.")
 
def edit_settings(settings):
    print("\n-- Edit Settings --")
    
    # Edit Mode
    mode = input(f"Enter mode (decal/model) [current: {settings['mode']}]: ").strip().lower()
    if mode in ['decal', 'model']:
        settings['mode'] = mode
    elif mode:
        print("Invalid mode. Keeping previous value.")
    
    # Edit Amount
    while True:
        amt_input = input(f"Enter amount (current: {settings['amount']}): ").strip()
        if not amt_input:
            break
        try:
            settings['amount'] = int(amt_input)
            break
        except ValueError:
            print("Amount must be an integer.")
    
    # Edit Pixel Count
    while True:
        pixel_count_input = input(f"Enter pixel count (current: {settings['pixel_count']}): ").strip()
        if not pixel_count_input:
            break
        try:
            settings['pixel_count'] = int(pixel_count_input)
            break
        except ValueError:
            print("Pixel count must be an integer.")
    
    print("Settings updated.\n")
 
def apply_effect(image, mode, output_name, pixel_count):
    img = image.copy().convert("RGBA")
    pixels = img.load()
    width, height = img.size
 
    if mode == "model":
        for x in range(width):
            for y in range(height):
                r, g, b, _ = pixels[x, y]
                pixels[x, y] = (r, g, b, 1)
 
    # Add random pixels
    for _ in range(pixel_count):
        rand_x = random.randint(0, width - 1)
        rand_y = random.randint(0, height - 1)
        rand_color = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
            255
        )
        pixels[rand_x, rand_y] = rand_color
 
    print(f"Created: {output_name}")
    print(f" - {pixel_count} random pixels added.")
    print(f" - Image size: {width}x{height}")
 
    return img
 
def run_program(folder, settings):
    print("\n-- Running Program --")
    mode = settings['mode']
    amount = settings['amount']
    pixel_count = settings['pixel_count']
 
    image_files = [f for f in os.listdir(folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if not image_files:
        print("No supported image files found in the folder.")
        return
 
    output_dir = os.path.join(folder, "output")
    os.makedirs(output_dir, exist_ok=True)
 
    for filename in image_files:
        img_path = os.path.join(folder, filename)
        try:
            image = Image.open(img_path)
            name, _ = os.path.splitext(filename)
            image = image.convert("RGBA")
 
            for i in range(amount):
                out_name = f"{name}_{mode}_{i+1}.png"
                out_path = os.path.join(output_dir, out_name)
                modified = apply_effect(image, mode, out_name, pixel_count)
                modified.save(out_path, format='PNG')
 
            print(f"Finished processing: {filename}")
        except Exception as e:
            print(f"Error processing {filename}: {e}")
 
    print("All done!\n")
 
def main():
    folder = get_folder()
    settings = {
        "mode": "decal",
        "amount": 3,
        "pixel_count": 5  # Default pixel count
    }
 
    while True:
        print("\nWhat would you like to do?")
        print("1. Run the program")
        print("2. Edit settings")
        print("3. Exit")
        choice = input("Enter choice (1/2/3): ").strip()
 
        if choice == '1':
            run_program(folder, settings)
        elif choice == '2':
            edit_settings(settings)
        elif choice == '3':
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Try again.")
 
if __name__ == "__main__":
    main()