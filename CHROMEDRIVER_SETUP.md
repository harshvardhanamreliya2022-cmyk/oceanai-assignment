# ChromeDriver Setup Guide (Offline/Restricted Networks)

This guide helps you set up ChromeDriver when you can't use WebDriver Manager due to network restrictions.

## Quick Start (Windows)

### Step 1: Check Your Chrome Version

1. Open Google Chrome
2. Go to: `chrome://version`
3. Note the version number (e.g., `120.0.6099.109`)

### Step 2: Download ChromeDriver

**Option A: Chrome for Testing (Recommended)**
1. Visit: https://googlechromelabs.github.io/chrome-for-testing/
2. Find your Chrome version
3. Download `chromedriver-win64.zip` or `chromedriver-win32.zip`

**Option B: ChromeDriver Archive**
1. Visit: https://chromedriver.chromium.org/downloads
2. Click on the version matching your Chrome
3. Download `chromedriver_win32.zip`

### Step 3: Extract and Install

**Easy Method (Recommended):**
```cmd
# Create directory
mkdir C:\chromedriver

# Extract chromedriver.exe to C:\chromedriver\
# You should have: C:\chromedriver\chromedriver.exe
```

**Alternative Method (Add to PATH):**
```cmd
# Extract to C:\Windows\
# You should have: C:\Windows\chromedriver.exe
# (This folder is already in PATH)
```

### Step 4: Verify Installation

```cmd
# Test if ChromeDriver is accessible
chromedriver --version

# Expected output: ChromeDriver 120.0.6099.109 (...)
```

## Using ChromeDriver in Scripts

### Method 1: Specify Path Directly

Edit your test script and set the path:

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

# Set your ChromeDriver path
service = Service(executable_path=r"C:\chromedriver\chromedriver.exe")
driver = webdriver.Chrome(service=service)
```

### Method 2: Use the Offline Script

We've created `test_script_offline.py` that automatically finds ChromeDriver:

```bash
python test_data/test_script_offline.py
```

It checks these locations automatically:
- `C:\Windows\chromedriver.exe`
- `C:\chromedriver\chromedriver.exe`
- Current directory
- PATH environment variable

## Troubleshooting

### Error: "chromedriver.exe is not a valid Win32 application"

**Solution:** You downloaded the wrong architecture
- For 64-bit Windows: Download `chromedriver-win64.zip`
- For 32-bit Windows: Download `chromedriver-win32.zip`

### Error: "ChromeDriver version mismatch"

**Solution:** Chrome and ChromeDriver versions must match
1. Check Chrome version: `chrome://version`
2. Download matching ChromeDriver version
3. Major versions must match (e.g., both 120.x.x.x)

### Error: "Access is denied"

**Solution:** Run as administrator or use a different location
```cmd
# Try user-specific directory instead
mkdir %USERPROFILE%\chromedriver
# Extract to: C:\Users\YourName\chromedriver\chromedriver.exe
```

### Error: "This version of ChromeDriver only supports Chrome version X"

**Solution:**
1. Update Google Chrome to the latest version
2. Download the latest ChromeDriver
3. Or download ChromeDriver matching your current Chrome version

## Linux/Mac Setup

### Linux
```bash
# Download
wget https://chromedriver.storage.googleapis.com/LATEST_RELEASE
version=$(cat LATEST_RELEASE)
wget https://chromedriver.storage.googleapis.com/$version/chromedriver_linux64.zip

# Extract
unzip chromedriver_linux64.zip

# Install
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver

# Verify
chromedriver --version
```

### macOS
```bash
# Download
brew install chromedriver

# Or manual:
curl -O https://chromedriver.storage.googleapis.com/LATEST_RELEASE
version=$(cat LATEST_RELEASE)
curl -O https://chromedriver.storage.googleapis.com/$version/chromedriver_mac64.zip
unzip chromedriver_mac64.zip
sudo mv chromedriver /usr/local/bin/

# Verify
chromedriver --version
```

## Alternative: Use Firefox Instead

If Chrome setup is difficult, use Firefox with GeckoDriver:

```python
from selenium import webdriver

# Firefox doesn't require separate driver download in newer versions
driver = webdriver.Firefox()
```

### Download GeckoDriver (if needed):
1. Visit: https://github.com/mozilla/geckodriver/releases
2. Download for your OS
3. Extract and place in PATH or specify path:

```python
from selenium.webdriver.firefox.service import Service

service = Service(executable_path=r"C:\geckodriver\geckodriver.exe")
driver = webdriver.Firefox(service=service)
```

## Quick Reference

### Common ChromeDriver Locations

**Windows:**
- `C:\Windows\chromedriver.exe`
- `C:\chromedriver\chromedriver.exe`
- `C:\Program Files\chromedriver\chromedriver.exe`
- `%USERPROFILE%\chromedriver\chromedriver.exe`

**Linux:**
- `/usr/local/bin/chromedriver`
- `/usr/bin/chromedriver`
- `~/.local/bin/chromedriver`

**macOS:**
- `/usr/local/bin/chromedriver`
- `/opt/homebrew/bin/chromedriver`

### Check Chrome Version

**Windows:**
```cmd
reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version
```

**Linux/Mac:**
```bash
google-chrome --version
# or
chromium --version
```

## Testing Your Setup

Run the offline test script:

```bash
# Start test server (Terminal 1)
cd test_data
python -m http.server 8080

# Run test (Terminal 2)
python test_data/test_script_offline.py
```

If successful, you'll see:
```
✅ Test server is running
✅ WebDriver initialized successfully
✅ Page loaded
✅ Discount field found
✅ Code entered
✅ Apply clicked
✅ Discount applied: $15.00
✅ TEST PASSED
```

## Next Steps

Once ChromeDriver is set up:
1. Generate Selenium scripts using the QA Agent UI
2. Update the `CHROMEDRIVER_PATH` in your scripts
3. Run tests with: `python data/scripts/your_test.py`
4. Integrate into your CI/CD pipeline

## Resources

- [ChromeDriver Downloads](https://chromedriver.chromium.org/downloads)
- [Chrome for Testing](https://googlechromelabs.github.io/chrome-for-testing/)
- [Selenium Documentation](https://www.selenium.dev/documentation/)
- [GeckoDriver (Firefox)](https://github.com/mozilla/geckodriver/releases)
