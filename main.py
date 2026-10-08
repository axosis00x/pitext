import os
import subprocess
import sys
import tempfile

import pyperclip
import pytesseract
from PIL import Image


def select_region():
    """Select region using slurp (Wayland region selector)"""
    try:
        cmd = ["slurp", "-f", "%x,%y %wx%h"]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Slurp error: {result.stderr}")
            return None

        output = result.stdout.strip()
        if not output:
            return None

        coords, size = output.split(" ")
        x, y = map(int, coords.split(","))
        width, height = map(int, size.split("x"))

        return {"left": x, "top": y, "width": width, "height": height}

    except Exception as e:
        print(f"Error in region selection: {e}")
        return None


def capture_region(selection):
    """Capture the selected region using grim (Wayland screenshot tool)"""
    try:
        # Create temporary file for screenshot
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
            tmp_path = tmp_file.name

        cmd = [
            "grim",
            "-g",
            f"{selection['left']},{selection['top']} {selection['width']}x{selection['height']}",
            tmp_path,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Grim error: {result.stderr}")
            return None

        return tmp_path

    except Exception as e:
        print(f"Error capturing region: {e}")
        return None


def extract_text(image_path):
    """Extract text from image using OCR"""
    try:
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        print(f"Error extracting text: {e}")
        return None


def copy_to_clipboard(text):
    """Copy text to clipboard"""
    try:
        pyperclip.copy(text)
        return True
    except Exception as e:
        print(f"Error copying to clipboard: {e}")
        return False


def main():
    """Main function to capture region and extract text"""
    print("📸 Select a region to capture...")

    # Select region using slurp
    selection = select_region()

    if not selection:
        print("❌ Region selection cancelled")
        sys.exit(1)

    print("📷 Capturing region...")

    # Capture region
    image_path = capture_region(selection)
    if not image_path:
        print("❌ Failed to capture region")
        sys.exit(1)

    print("🔍 Extracting text...")

    # Extract text
    text = extract_text(image_path)

    # Clean up temporary file
    try:
        os.unlink(image_path)
    except:  # noqa: E722
        pass

    if not text:
        print("❌ No text found in the selected region")
        sys.exit(1)

    # Copy to clipboard
    if copy_to_clipboard(text):
        print(" Text extracted and copied to clipboard:")
        print("-" * 40)
        print(text)
        print("-" * 40)
    else:
        print("⚠️  Text extracted but clipboard copy failed:")
        print("-" * 40)
        print(text)
        print("-" * 40)


if __name__ == "__main__":
    main()
