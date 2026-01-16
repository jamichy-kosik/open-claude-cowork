"""
Browser Use Skill Helper
E2B Desktop Sandbox helper functions for browser automation and desktop interaction.

Installation:
    pip install e2b-desktop

Environment:
    E2B_API_KEY - Required for sandbox creation
"""

from e2b_desktop import Sandbox
from typing import Optional, List, Union
import os

# Global sandbox instance - cached for performance
_sandbox: Optional[Sandbox] = None
_sandbox_id_cache: Optional[str] = None


def get_sandbox() -> Sandbox:
    """
    Get the current sandbox instance.
    
    Returns:
        Sandbox: The active sandbox instance
        
    Note:
        This function automatically retrieves sandbox from environment variable AGENT_SANDBOX_ID.
        If sandbox doesn't exist, creates a new one and exports the ID.
    """
    global _sandbox, _sandbox_id_cache
    
    # Get sandbox ID from environment
    sandbox_id = os.environ.get('AGENT_SANDBOX_ID')
    
    # If we have cached sandbox and ID matches, return it
    if _sandbox is not None and _sandbox_id_cache == sandbox_id:
        return _sandbox
    
    # Try to connect to existing sandbox
    if sandbox_id:
        try:
            print(f"[E2B] Connecting to sandbox: {sandbox_id}")
            _sandbox = Sandbox.connect(sandbox_id)
            _sandbox_id_cache = sandbox_id
            print(f"[E2B] Connected to sandbox: {sandbox_id}")
            return _sandbox
        except Exception as e:
            print(f"[E2B] Failed to connect to sandbox {sandbox_id}: {e}")
            print("[E2B] Creating new sandbox...")
    
    # Create new sandbox
    print("[E2B] Creating new E2B Desktop sandbox...")
    _sandbox = Sandbox.create()
    _sandbox_id_cache = _sandbox.sandbox_id
    
    # Export sandbox ID for other processes
    os.environ['AGENT_SANDBOX_ID'] = _sandbox.sandbox_id
    print(f"[E2B] Sandbox created: {_sandbox.sandbox_id}")
    print(f"[E2B] Sandbox ID exported to environment: AGENT_SANDBOX_ID={_sandbox.sandbox_id}")
    
    return _sandbox


def set_sandbox(sandbox: Sandbox) -> None:
    """
    Set the global sandbox instance (for backwards compatibility).
    
    Args:
        sandbox: The sandbox instance to use
    """
    global _sandbox, _sandbox_id_cache
    _sandbox = sandbox
    _sandbox_id_cache = sandbox.sandbox_id
    os.environ['AGENT_SANDBOX_ID'] = sandbox.sandbox_id


def launch_application(app_name: str, sandbox: Optional[Sandbox] = None) -> None:
    """
    Launch an application in the sandbox.
    
    Args:
        app_name: Application to launch (e.g., 'google-chrome', 'firefox', 'vscode')
        sandbox: Optional sandbox instance (auto-fetched if not provided)
        
    Example:
        >>> launch_application('google-chrome')
    """
    if sandbox is None:
        sandbox = get_sandbox()
    print(f"[E2B] Launching {app_name}...")
    sandbox.launch(app_name)


def wait(seconds: float, sandbox: Optional[Sandbox] = None) -> None:
    """
    Wait for specified number of seconds.
    
    Args:
        seconds: Number of seconds to wait
        sandbox: Optional (not used, for backwards compatibility)
        
    Example:
        >>> wait(2.5)  # Wait 2.5 seconds
    """
    if sandbox is None:
        sandbox = get_sandbox()
    sandbox.wait(1000 * seconds)


def start_stream(window_id: Optional[str] = None, 
                view_only: bool = False, require_auth: bool = False, 
                sandbox: Optional[Sandbox] = None) -> str:
    """
    Start streaming the desktop and get the URL.
    
    Args:
        window_id: Optional window ID (not used in current version)
        view_only: If True, get view-only URL
        require_auth: If True, require authentication
        sandbox: Optional sandbox instance (auto-fetched if not provided)
        
    Returns:
        str: The stream URL
        
    Example:
        >>> url = start_stream()
        >>> print(f"View desktop: {url}")
    """
    if sandbox is None:
        sandbox = get_sandbox()
    try:
        # Start VNC stream
        sandbox.stream.start()
        
        # Get URL (with or without auth)
        if require_auth:
            auth_key = sandbox.stream.get_auth_key()
            stream_url = sandbox.stream.get_url(auth_key=auth_key)
        else:
            stream_url = sandbox.stream.get_url(view_only=view_only)
        
        print(f"[E2B] Stream started: {stream_url}")
        return stream_url
    except Exception as e:
        print(f"[E2B] Error starting stream: {e}")
        # Fallback to direct URL
        stream_url = f"https://6080-{sandbox.sandbox_id}.e2b.app/vnc.html?autoconnect=true&resize=scale"
        return stream_url


def get_stream_url(view_only: bool = False, sandbox: Optional[Sandbox] = None) -> str:
    """
    Get the stream URL (stream must be already started).
    
    Args:
        view_only: If True, get view-only URL
        sandbox: Optional sandbox instance (auto-fetched if not provided)
        
    Returns:
        str: The stream URL
    """
    if sandbox is None:
        sandbox = get_sandbox()
    try:
        return sandbox.stream.get_url(view_only=view_only)
    except:
        return f"https://6080-{sandbox.sandbox_id}.e2b.app/vnc.html?autoconnect=true&resize=scale"


def stop_stream(sandbox: Optional[Sandbox] = None) -> None:
    """
    Stop the current stream.
    
    Args:
        sandbox: Optional sandbox instance (auto-fetched if not provided)
    """
    if sandbox is None:
        sandbox = get_sandbox()
    try:
        sandbox.stream.stop()
        print("[E2B] Stream stopped")
    except Exception as e:
        print(f"[E2B] Error stopping stream: {e}")


def mouse_click(x: Optional[int] = None, y: Optional[int] = None,
               button: str = "left", sandbox: Optional[Sandbox] = None) -> None:
    """
    Click the mouse button.
    
    Args:
        x: X coordinate (None = current position)
        y: Y coordinate (None = current position)
        button: Mouse button - "left", "right", or "middle"
        sandbox: Optional sandbox instance (auto-fetched if not provided)
        
    Example:
        >>> mouse_click(100, 200)  # Left click at (100, 200)
        >>> mouse_click(button="right")  # Right click at current position
    """
    if sandbox is None:
        sandbox = get_sandbox()
    if button == "left":
        if x is not None and y is not None:
            sandbox.left_click(x=x, y=y)
        else:
            sandbox.left_click()
    elif button == "right":
        if x is not None and y is not None:
            sandbox.right_click(x=x, y=y)
        else:
            sandbox.right_click()
    elif button == "middle":
        if x is not None and y is not None:
            sandbox.middle_click(x=x, y=y)
        else:
            sandbox.middle_click()


def mouse_double_click(x: Optional[int] = None, 
                      y: Optional[int] = None, sandbox: Optional[Sandbox] = None) -> None:
    """
    Double click the mouse.
    
    Args:
        x: X coordinate (None = current position)
        y: Y coordinate (None = current position)
        sandbox: Optional sandbox instance (auto-fetched if not provided)
    """
    if sandbox is None:
        sandbox = get_sandbox()
    if x is not None and y is not None:
        sandbox.double_click(x=x, y=y)
    else:
        sandbox.double_click()


def mouse_move(x: int, y: int, sandbox: Optional[Sandbox] = None) -> None:
    """
    Move mouse to coordinates.
    
    Args:
        x: X coordinate
        y: Y coordinate
        sandbox: Optional sandbox instance (auto-fetched if not provided)
    """
    if sandbox is None:
        sandbox = get_sandbox()
    sandbox.move_mouse(x, y)


def mouse_scroll(amount: int, sandbox: Optional[Sandbox] = None) -> None:
    """
    Scroll with the mouse wheel.
    
    Args:
        amount: Scroll amount (positive=up, negative=down)
        sandbox: Optional sandbox instance (auto-fetched if not provided)
        
    Example:
        >>> mouse_scroll(5)   # Scroll up
        >>> mouse_scroll(-5)  # Scroll down
    """
    if sandbox is None:
        sandbox = get_sandbox()
    sandbox.scroll(amount)


def mouse_drag(from_x: int, from_y: int, 
              to_x: int, to_y: int, sandbox: Optional[Sandbox] = None) -> None:
    """
    Drag mouse from one position to another.
    
    Args:
        from_x: Start X coordinate
        from_y: Start Y coordinate
        to_x: End X coordinate
        to_y: End Y coordinate
        sandbox: Optional sandbox instance (auto-fetched if not provided)
    """
    if sandbox is None:
        sandbox = get_sandbox()
    sandbox.drag((from_x, from_y), (to_x, to_y))


def mouse_press(button: str = "left", sandbox: Optional[Sandbox] = None) -> None:
    """
    Press and hold mouse button.
    
    Args:
        button: Mouse button - "left", "right", or "middle"
        sandbox: Optional sandbox instance (auto-fetched if not provided)
    """
    if sandbox is None:
        sandbox = get_sandbox()
    sandbox.mouse_press(button)


def mouse_release(button: str = "left", sandbox: Optional[Sandbox] = None) -> None:
    """
    Release mouse button.
    
    Args:
        button: Mouse button - "left", "right", or "middle"
        sandbox: Optional sandbox instance (auto-fetched if not provided)
    """
    if sandbox is None:
        sandbox = get_sandbox()
    sandbox.mouse_release(button)


def type_text(text: str, chunk_size: int = 25, 
             delay_ms: int = 75, sandbox: Optional[Sandbox] = None) -> None:
    """
    Type text at current cursor position.
    
    Args:
        text: Text to type
        chunk_size: Number of characters to type at once
        delay_ms: Delay between chunks in milliseconds
        sandbox: Optional sandbox instance (auto-fetched if not provided)
        
    Example:
        >>> type_text("Hello, world!")
        >>> type_text("Fast typing!", chunk_size=50, delay_ms=25)
    """
    if sandbox is None:
        sandbox = get_sandbox()
    sandbox.write(text, chunk_size=chunk_size, delay_in_ms=delay_ms)


def press_keys(keys: Union[str, List[str]], sandbox: Optional[Sandbox] = None) -> None:
    """
    Press keyboard key(s).
    
    Args:
        keys: Single key or list of keys for combination
        sandbox: Optional sandbox instance (auto-fetched if not provided)
        
    Example:
        >>> press_keys("enter")
        >>> press_keys(["ctrl", "c"])  # Ctrl+C
        >>> press_keys(["ctrl", "shift", "t"])  # Ctrl+Shift+T
        
    Common keys:
        - enter, tab, backspace, delete, space, escape
        - ctrl, alt, shift, meta (Windows/Command key)
        - up, down, left, right
        - home, end, pageup, pagedown
        - f1-f12
    """
    if sandbox is None:
        sandbox = get_sandbox()
    sandbox.press(keys)


def run_command(command: str, sandbox: Optional[Sandbox] = None) -> str:
    """
    Run bash command in sandbox.
    
    Args:
        command: Bash command to execute
        sandbox: Optional sandbox instance (auto-fetched if not provided)
        
    Returns:
        str: Command output
        
    Example:
        >>> output = run_command("ls -la /home/user")
        >>> print(output)
    """
    if sandbox is None:
        sandbox = get_sandbox()
    result = sandbox.commands.run(command)
    return str(result)


def take_screenshot(filename: str = "screenshot.png", sandbox: Optional[Sandbox] = None) -> str:
    """
    Take screenshot and save locally.
    
    Args:
        filename: Local filename to save to
        sandbox: Optional sandbox instance (auto-fetched if not provided)
        
    Returns:
        str: Path to saved screenshot
        
    Example:
        >>> path = take_screenshot("page.png")
        >>> print(f"Screenshot saved to {path}")
    """
    if sandbox is None:
        sandbox = get_sandbox()
    image = sandbox.screenshot()
    with open(filename, "wb") as f:
        f.write(image)
    print(f"[E2B] Screenshot saved to {filename}")
    return filename


def write_file(path: str, content: str, sandbox: Optional[Sandbox] = None) -> None:
    """
    Write file in sandbox.
    
    Args:
        path: File path in sandbox (e.g., "/home/user/file.txt")
        content: File content
        sandbox: Optional sandbox instance (auto-fetched if not provided)
        
    Example:
        >>> write_file("/home/user/test.txt", "Hello!")
    """
    if sandbox is None:
        sandbox = get_sandbox()
    sandbox.files.write(path, content)
    print(f"[E2B] File written: {path}")


def read_file(path: str, sandbox: Optional[Sandbox] = None) -> str:
    """
    Read file from sandbox.
    
    Args:
        path: File path in sandbox
        sandbox: Optional sandbox instance (auto-fetched if not provided)
        
    Returns:
        str: File content
    """
    if sandbox is None:
        sandbox = get_sandbox()
    return sandbox.files.read(path)


def open_file(path: str, sandbox: Optional[Sandbox] = None) -> None:
    """
    Open file with default application.
    
    Args:
        path: File path in sandbox
        sandbox: Optional sandbox instance (auto-fetched if not provided)
        
    Example:
        >>> write_file("/home/user/doc.txt", "Content")
        >>> open_file("/home/user/doc.txt")
    """
    if sandbox is None:
        sandbox = get_sandbox()
    sandbox.open(path)
    print(f"[E2B] Opened file: {path}")


def set_cursor_size(size: int = 96, sandbox: Optional[Sandbox] = None) -> None:
    """
    Set mouse cursor size (makes it easier to see).
    
    Args:
        size: Cursor size in pixels (default: 96, normal: 24)
        sandbox: Optional sandbox instance (auto-fetched if not provided)
        
    Example:
        >>> set_cursor_size(96)  # Large cursor
    """
    if sandbox is None:
        sandbox = get_sandbox()
    try:
        # Set cursor size using xrdb
        sandbox.commands.run(f'echo "Xcursor.size: {size}" | xrdb -merge')
        print(f"[E2B] Cursor size set to {size}px")
    except Exception as e:
        print(f"[E2B] Could not set cursor size: {e}")


# Convenience function for common workflow
def open_browser(url: Optional[str] = None, sandbox: Optional[Sandbox] = None) -> None:
    """
    Open browser and optionally navigate to URL.
    
    Args:
        url: Optional URL to navigate to
        sandbox: Optional sandbox instance (auto-fetched if not provided)
        
    Example:
        >>> open_browser("https://example.com")
    """
    if sandbox is None:
        sandbox = get_sandbox()
    
    # Set larger cursor for better visibility
    set_cursor_size(48, sandbox)
    
    # Try Firefox first, fallback to Chrome if not available
    launch_application('google-chrome', sandbox)
    
    wait(7)  # Wait for browser to open
    
    if url:
        print("[E2B] Navigating to URL:", url)
        type_text(url, sandbox=sandbox)
        press_keys("enter", sandbox)
        wait(5)