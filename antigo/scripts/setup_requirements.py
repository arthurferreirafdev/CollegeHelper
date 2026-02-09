"""
Setup script to install required packages for the ChatGPT integration
"""

import subprocess
import sys

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✓ Successfully installed {package}")
        return True
    except subprocess.CalledProcessError:
        print(f"✗ Failed to install {package}")
        return False

def main():
    """Install all required packages"""
    print("Setting up ChatGPT integration requirements...")
    print("=" * 50)
    
    required_packages = [
        "openai>=1.0.0",
        "python-dotenv"  # For environment variable management
    ]
    
    success_count = 0
    for package in required_packages:
        if install_package(package):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"Installation complete: {success_count}/{len(required_packages)} packages installed")
    
    if success_count == len(required_packages):
        print("\n✓ All packages installed successfully!")
        print("\nNext steps:")
        print("1. Get your OpenAI API key from: https://platform.openai.com/api-keys")
        print("2. Set the OPENAI_API_KEY environment variable or enter it when prompted")
        print("3. Run: python scripts/ai_cli_interface.py")
    else:
        print("\n✗ Some packages failed to install. Please check the errors above.")

if __name__ == "__main__":
    main()
