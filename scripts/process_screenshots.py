from PIL import Image
import os
from pathlib import Path

SCREENSHOTS_DIR = Path(__file__).parent / "screenshots"
OUTPUT_DIR = Path(__file__).parent / "processed"
OUTPUT_DIR.mkdir(exist_ok=True)

def load_screenshots():
    """Load all screenshots from the screenshots directory."""
    screenshots = []
    for file in SCREENSHOTS_DIR.glob("viewport_*.png"):
        img = Image.open(file)
        desc = file.stem.split('_')[1]  # Get position description (rightdown/leftup)
        screenshots.append((desc, img))
    return screenshots

def calculate_canvas_size(screenshots):
    """Calculate the size of the final canvas based on corner positions."""
    max_width = max(img.width for _, img in screenshots)
    max_height = max(img.height for _, img in screenshots)
    return max_width * 2, max_height * 2  # Double size to ensure coverage

def create_composite_image(screenshots):
    """Create a composite image from the screenshots."""
    if not screenshots:
        raise ValueError("No screenshots found")
    
    # Calculate canvas size
    canvas_width, canvas_height = calculate_canvas_size(screenshots)
    composite = Image.new('RGB', (canvas_width, canvas_height))
    
    # Position images based on their descriptions
    for desc, img in screenshots:
        if desc == 'rightdown':
            position = (canvas_width - img.width, canvas_height - img.height)
        elif desc == 'leftup':
            position = (0, 0)
        composite.paste(img, position)
    
    return composite

def main():
    """Main function to process screenshots into a complete visualization."""
    print("Loading screenshots...")
    screenshots = load_screenshots()
    
    print("Creating composite image...")
    composite = create_composite_image(screenshots)
    
    output_path = OUTPUT_DIR / "complete_visualization.png"
    composite.save(output_path)
    print(f"Saved complete visualization to: {output_path}")

if __name__ == "__main__":
    main()
