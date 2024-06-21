import os
import sys
import time
import keyboard
import subprocess


def check_packer_installed() -> None:
    try:
        packer_check = subprocess.run(
            ["packer", "--version"], capture_output=True, text=True
        )
        print(f"Packer is installed. Version: {packer_check.stdout.strip()}")
    except FileNotFoundError:
        print("Packer is not installed.")
        print(
            "Please install packer and make it executable to be able to use this package."
        )
        sys.exit(1)


def main() -> None:
    check_packer_installed()

    package_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(package_dir, "../proxmoxtemplates/main.py")
    process = subprocess.Popen(["streamlit", "run", app_path])

    time.sleep(1)

    print()
    print("To quit the app, press 'strg + c'.")
    print()

    # Listen for 'strg+c' key press
    keyboard.add_hotkey("ctrl+c", lambda: process.terminate())

    # Wait for the Streamlit app process to complete
    process.wait()

    print("Streamlit app terminated.")


if __name__ == "__main__":
    main()
