# Outlook Database Authentication - Implementation Guide

## Overview

Successfully implemented database-based authentication for Outlook skill, similar to Google OAuth services. Users can now connect their Outlook account through the application Settings page, and tokens are stored securely in the database per-user.

## What Was Changed

### Backend Changes

#### 1. **API Endpoints** (`backend/app/api/oauth.py`)
Added new Outlook OAuth endpoints:
- `POST /oauth/outlook/token` - Save MSAL token cache to database
- `GET /oauth/outlook/status` - Check if user has Outlook connected
- `GET /oauth/outlook/authorize` - Get OAuth authorization URL
- `POST /oauth/outlook/callback` - Handle OAuth callback and save token
- `DELETE /oauth/outlook/disconnect` - Disconnect Outlook account

#### 2. **Service Layer** (`backend/app/services/oauth_service.py`)
Added function:
```python
def get_outlook_token_cache(user_id: int, db: Session) -> str:
    """Load Outlook MSAL token cache from database"""
```

#### 3. **Outlook Helper** (`.claude/skills/outlook/outlook_helper.py`)
- Added `_get_token_cache_from_db()` function to load token from database
- Modified `_get_msal_app()` to support two token sources:
  1. **Database** (when `AGENT_USER_ID` is set - agent context)
  2. **Local file** (fallback for manual testing)
- Token priority: Database → Local file

### Frontend Changes

#### 1. **API Functions** (`frontend/src/utils/api.js`)
Added Outlook OAuth functions:
```javascript
getOutlookStatus: () => api.get('/oauth/outlook/status'),
authorizeOutlook: () => api.get('/oauth/outlook/authorize'),
outlookCallback: (code) => api.post('/oauth/outlook/callback', ...),
disconnectOutlook: () => api.delete('/oauth/outlook/disconnect'),
```

#### 2. **Settings Page** (`frontend/src/pages/Settings.jsx`)
- Added Outlook section with Connect/Disconnect buttons
- Connection status indicator
- OAuth popup window handling

#### 3. **Callback Page** (`frontend/src/pages/OutlookCallback.jsx`)
New page to handle OAuth redirect:
- Processes authorization code
- Sends to backend for token exchange
- Returns success/error to parent window

#### 4. **Routing** (`frontend/src/App.jsx`)
Added route: `/oauth/outlook/callback`

## How It Works

### User Flow

1. **User goes to Settings page**
2. **Clicks "Connect" on Microsoft Outlook section**
3. **OAuth popup opens** with Microsoft login
4. **User logs in** with Microsoft account
5. **Microsoft redirects** to `http://localhost:3000/oauth/outlook/callback?code=...`
6. **Callback page** sends code to backend
7. **Backend exchanges code** for MSAL token cache using `msal` library
8. **Token cache saved** to database (`oauth_credentials` table)
9. **Popup closes**, Settings page shows "Connected" status

### Agent Integration

When agent needs to access Outlook:

1. **Agent Service** sets `AGENT_USER_ID` environment variable
2. **outlook_helper.py** detects `AGENT_USER_ID`
3. **Helper loads token** from database for that user
4. **MSAL app uses** database token cache
5. **API requests succeed** with user's token

### Database Storage

Token is stored in `oauth_credentials` table:
- `service` = 'outlook'
- `access_token` = Serialized MSAL token cache (JSON)
- `user_id` = User's database ID

The MSAL token cache includes:
- Access token
- Refresh token
- Token expiry
- Account information

## Prerequisites

### Environment Variable
Set in `.env` file:
```
MICROSOFT_CLIENT_ID=<your-azure-app-client-id>
```

### Azure App Registration
1. Go to https://portal.azure.com
2. Azure Active Directory → App registrations → New registration
3. Name: "Outlook Helper" or similar
4. Supported account types: "Personal Microsoft accounts only"
5. Redirect URI: `http://localhost:3000/oauth/outlook/callback`
6. Copy Application (client) ID to `.env`

### Required Permissions (Scopes)
- `User.Read` - Read user profile
- `Mail.Read` - Read emails
- `Mail.Send` - Send emails
- `Mail.ReadWrite` - Modify emails
- `Calendars.Read` - Read calendar
- `Calendars.ReadWrite` - Modify calendar
- `offline_access` - Get refresh token

## Testing

### Run Test Script
```bash
cd "c:\Users\JakubMichna\WORK\OLD AI\.claude\skills\outlook"
python test_outlook_db_auth.py
```

Expected output:
```
✅ Database can store and retrieve Outlook tokens
✅ Helper can load token from database
✅ All Outlook API functions defined in api.js
✅ OutlookCallback.jsx exists
```

### Manual Testing

1. **Start backend and frontend**
2. **Login to application**
3. **Go to Settings** (http://localhost:3000/settings)
4. **Find Microsoft Outlook section**
5. **Click "Connect" button**
6. **Login in popup window**
7. **Verify "Connected" status**

### Test Email Reading
```bash
cd "../../.claude/skills/outlook"
python -c "from outlook_helper import get_emails; print(get_emails(count=5))"
```

With database token (when running through agent):
```python
import os
os.environ['AGENT_USER_ID'] = '1'  # Your user ID
# Then import and use outlook_helper
```

## Benefits

### For Users
✅ **One-click connection** in UI  
✅ **No manual token management**  
✅ **Per-user isolation** - each user has own token  
✅ **Automatic refresh** - MSAL handles token renewal  

### For Developers
✅ **Consistent with Google OAuth** pattern  
✅ **Database-backed** - no local files to manage  
✅ **Agent integration** - works seamlessly with agent context  
✅ **Fallback support** - local file still works for testing  

## Files Modified

1. `backend/app/api/oauth.py` - OAuth endpoints
2. `backend/app/services/oauth_service.py` - Token retrieval service
3. `.claude/skills/outlook/outlook_helper.py` - Database integration
4. `.claude/skills/outlook/SKILL.md` - Updated documentation
5. `frontend/src/utils/api.js` - API functions
6. `frontend/src/pages/Settings.jsx` - UI for connection
7. `frontend/src/pages/OutlookCallback.jsx` - OAuth callback handler
8. `frontend/src/App.jsx` - Routing

## Troubleshooting

### "MICROSOFT_CLIENT_ID not configured"
- Set `MICROSOFT_CLIENT_ID` in `.env` file
- Restart backend

### "Token expired"
- MSAL automatically refreshes if refresh_token exists
- If still fails, disconnect and reconnect in Settings

### OAuth popup blocked
- Allow popups for localhost:3000
- Or use incognito/private window

### "Failed to load token from database"
- Check user has connected Outlook in Settings
- Verify `AGENT_USER_ID` is set correctly
- Check database has record with service='outlook'

## Next Steps

To use with agent:
1. User connects Outlook in Settings
2. Agent automatically uses database token
3. All Outlook commands work through agent

Example agent usage:
```
Show me my last 5 emails from Outlook
```

Agent will:
1. Load user's token from database
2. Call outlook_helper functions
3. Return email list
