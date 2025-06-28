#!/usr/bin/env python3

import subprocess
import sys

def setup_playwright():
    """Playwrightの初期セットアップを実行"""
    try:
        print("Installing Playwright browsers...")
        result = subprocess.run([
            sys.executable, "-m", "playwright", "install", "chromium"
        ], check=True, capture_output=True, text=True)
        
        print("Playwright setup completed successfully!")
        print(result.stdout)
        
    except subprocess.CalledProcessError as e:
        print(f"Error during Playwright setup: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False
    
    return True

if __name__ == "__main__":
    success = setup_playwright()
    if not success:
        sys.exit(1)