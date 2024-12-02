import subprocess
import sys

def install(package, no_deps=False):
    """Install a package using pip."""
    command = [sys.executable, "-m", "pip", "install", package]
    if no_deps:
        command.append("--no-deps")
    subprocess.check_call(command)

try:
    # Install packages
    install("beautifulsoup4")
    install("dateparser")
    install("feedparser")
    install("pygooglenews", no_deps=True)  # Special case for --no-deps
    install("selenium")
    install("chromedrivermanager")
    install("webdriver_manager")
    print("All packages installed successfully!")
except subprocess.CalledProcessError as e:
    print(f"Error occurred during installation: {e}")