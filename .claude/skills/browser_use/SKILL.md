---
name: browser_use
description: E2B Desktop sandbox skill for browser automation and desktop interaction. Use when user needs to interact with web browsers, open applications, or perform desktop tasks in isolated environment.
---

# Browser Use Skill

## Overview

This skill enables:
- Running applications in isolated desktop sandbox (Chrome, Firefox, VSCode, etc.)
- Browser automation and web interaction
- Desktop GUI control (mouse, keyboard)
- Taking screenshots
- Executing bash commands in sandbox
- File operations in sandbox environment

## Prerequisites

1. Python package: `e2b-desktop`
2. E2B API token (environment variable `E2B_API_KEY`)

## Important: Working Directory

**Always run commands from the skill directory:**
```bash
cd "../../.claude/skills/browser_use"
```

## Sandbox Management

The sandbox is automatically managed by the agent service:
- **One sandbox per user session** - Created on first use
- **Persistent connection** - Same sandbox is reused throughout session
- **Automatic cleanup** - Sandbox is terminated when session ends

## Available Functions

### 1. Launch Application

Launch applications in the sandbox:

```python
from browser_helper import launch_application

launch_application("google-chrome")
```

Supported applications:
- `google-chrome` - Google Chrome browser
- `firefox` - Mozilla Firefox
- `vscode` - Visual Studio Code
- `gedit` - Text editor
- Any other installed application

### 2. Stream Desktop

Get streaming URL to see the desktop:

```python
from browser_helper import start_stream

stream_url = start_stream()
print(f"View desktop: {stream_url}")
```

Options:
- `view_only=True` - Disable user interaction
- `window_id` - Stream specific window (default: whole desktop)

### 3. Mouse Control

Control mouse in sandbox:

```python
from browser_helper import mouse_click, mouse_move, mouse_scroll

# Click at position
mouse_click(x=100, y=200, button="left")

# Move mouse
mouse_move(x=150, y=250)

# Scroll
mouse_scroll(amount=5)  # Positive=up, negative=down
```

### 4. Keyboard Control

Type text and press keys:

```python
from browser_helper import type_text, press_keys

# Type text
type_text("Hello, world!")

# Press single key
press_keys("enter")

# Key combination
press_keys(["ctrl", "c"])
```

Common keys: `enter`, `tab`, `backspace`, `delete`, `space`, `escape`, `ctrl`, `alt`, `shift`

### 5. Take Screenshot

Capture current desktop:

```python
from browser_helper import take_screenshot

screenshot_path = take_screenshot("screenshot.png")
```

### 6. Execute Commands

Run bash commands in sandbox:

```python
from browser_helper import run_command

output = run_command("ls -la /home/user")
print(output)
```

### 7. Open Browser (Recommended)

Quick way to open browser and navigate to URL:

```python
from browser_helper import open_browser

# Open Chrome and navigate to URL
open_browser("https://example.com")

# Just open Chrome
open_browser()
```

This is **preferred over** manually launching Chrome, typing URL, and pressing enter.

### 8. File Operations

Work with files in sandbox:

```python
from browser_helper import write_file, read_file, open_file

# Write file
write_file("/home/user/test.txt", "Hello!")

# Open file with default app
open_file("/home/user/test.txt")

# Read file (if needed)
content = read_file("/home/user/test.txt")
```

## Example Workflows

### Open website and interact

```python
from browser_helper import *

# Open browser and navigate to website
open_browser("https://example.com")

# Wait for page to load
wait(3)

# Take screenshot
take_screenshot("page_loaded.png")

# Interact with page
mouse_click(x=500, y=300)
type_text("search query")
press_keys("enter")
```

### Fill web form

```python
from browser_helper import *

# Open login page
open_browser("https://example.com/login")
wait(2)

# Click on email input field
mouse_click(x=300, y=400)

# Type email
type_text("user@example.com")

# Tab to next field
press_keys("tab")

# Type password
type_text("password123")

# Submit form
press_keys("enter")
wait(2)

# Verify login
take_screenshot("logged_in.png")
```

### Search and extract data

```python
from browser_helper import *

# Open Hacker News
open_browser("https://news.ycombinator.com")
wait(3)

# Take screenshot for analysis
take_screenshot("hn_screenshot.png")

# Click first article
mouse_click(x=200, y=150)
wait(2)

# Take screenshot of article
take_screenshot("article.png")
```

## Usage Tips

1. **Use open_browser()** - Instead of manually launching Chrome + typing URL, use `open_browser(url)`
2. **Sandbox is automatic** - No need to call `get_sandbox()`, functions handle it automatically
3. **Add waits** - Use `wait(seconds)` after actions that need time (page loads, animations)
4. **Check screenshots** - Take screenshots to verify state before/after actions
5. **Error handling** - Check command outputs for errors

## Limitations

- Sandbox has limited resources (CPU, RAM)
- Network access may be restricted
- Some applications may not be pre-installed
- Session persists only during agent session

## Safety

- Each user has isolated sandbox
- No access to host system
- Automatic cleanup on session end
- All actions are sandboxed and safe
