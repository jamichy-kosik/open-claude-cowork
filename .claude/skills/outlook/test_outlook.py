"""
Test script for Outlook skill
Verifies all translations and basic functionality
"""
import sys
from pathlib import Path

# Add outlook skill to path
skill_path = Path(__file__).parent
sys.path.insert(0, str(skill_path))

print("=" * 60)
print("Testing Outlook Skill")
print("=" * 60)

# Test 1: Import all functions
print("\n1. Testing imports...")
try:
    from outlook_helper import (
        get_emails,
        send_email,
        search_emails,
        get_calendar_events,
        create_calendar_event,
        get_user_profile,
        is_authenticated,
        logout,
        get_current_user,
        authenticate_device_code
    )
    print("   ✅ All functions imported successfully")
except ImportError as e:
    print(f"   ❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Check authentication status
print("\n2. Testing authentication check...")
try:
    authenticated = is_authenticated()
    print(f"   ✅ Authentication check works (Status: {authenticated})")
except Exception as e:
    print(f"   ❌ Authentication check failed: {e}")

# Test 3: Check current user
print("\n3. Testing current user function...")
try:
    user = get_current_user()
    if user:
        print(f"   ✅ Current user: {user}")
    else:
        print("   ℹ️  No user logged in (expected if not authenticated)")
except Exception as e:
    print(f"   ❌ Get current user failed: {e}")

# Test 4: Verify English translations
print("\n4. Verifying English translations...")
import outlook_helper
import inspect

docstrings = []
source_code = inspect.getsource(outlook_helper)

# Check for Czech words (common ones)
czech_words = [
    "Chybí", "chybí",
    "Nepodařilo", "nepodařilo",
    "Zkontroluje", "zkontroluje",
    "Vytvoří", "vytvoří",
    "Načte", "načte",
    "Odešle", "odešle",
    "Vyhledá", "vyhledá",
    "Uživatel", "uživatel",
    "Přihlášen", "přihlášen"
]

found_czech = []
for word in czech_words:
    if word in source_code:
        found_czech.append(word)

if found_czech:
    print(f"   ⚠️  Found Czech words: {', '.join(set(found_czech))}")
else:
    print("   ✅ No Czech words found in code")

# Test 5: Check SKILL.md
print("\n5. Checking SKILL.md...")
skill_md = Path(__file__).parent / "SKILL.md"
if skill_md.exists():
    content = skill_md.read_text(encoding='utf-8')
    
    # Check for required English sections
    required_sections = [
        "## Overview",
        "## Prerequisites",
        "## How to Use",
        "## Available Functions",
        "## Troubleshooting"
    ]
    
    missing = []
    for section in required_sections:
        if section not in content:
            missing.append(section)
    
    if missing:
        print(f"   ⚠️  Missing sections: {', '.join(missing)}")
    else:
        print("   ✅ All required sections present")
    
    # Check description is in English
    if "description:" in content:
        desc_line = [line for line in content.split('\n') if line.startswith('description:')][0]
        if any(cz in desc_line for cz in ["pro", "přes", "když"]):
            print("   ⚠️  Description still in Czech")
        else:
            print("   ✅ Description in English")
else:
    print("   ❌ SKILL.md not found")

# Test 6: Test function signatures
print("\n6. Testing function signatures...")
try:
    # Test get_emails signature
    sig = inspect.signature(get_emails)
    params = list(sig.parameters.keys())
    if params == ['count', 'folder', 'unread_only']:
        print("   ✅ get_emails signature correct")
    else:
        print(f"   ⚠️  get_emails params: {params}")
    
    # Test send_email signature
    sig = inspect.signature(send_email)
    params = list(sig.parameters.keys())
    if params == ['to', 'subject', 'body', 'cc', 'is_html']:
        print("   ✅ send_email signature correct")
    else:
        print(f"   ⚠️  send_email params: {params}")
    
    # Test search_emails signature
    sig = inspect.signature(search_emails)
    params = list(sig.parameters.keys())
    if params == ['query', 'count']:
        print("   ✅ search_emails signature correct")
    else:
        print(f"   ⚠️  search_emails params: {params}")
        
except Exception as e:
    print(f"   ❌ Signature test failed: {e}")

print("\n" + "=" * 60)
print("Testing Complete!")
print("=" * 60)
print("\nNotes:")
print("  - Authentication requires Azure App Registration")
print("  - Set MICROSOFT_CLIENT_ID in .env to enable")
print("  - Use --auth-browser for interactive login")
print("=" * 60)
