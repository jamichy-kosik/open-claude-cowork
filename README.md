<p align="center">
  <h1 align="center">Open Claude Cowork</h1>
</p>

<p align="center">
  <img src="open-claude-cowork.gif" alt="Open Claude Cowork Demo" width="800">
</p>

<p align="center">
  <a href="https://docs.composio.dev/tool-router/overview">
    <img src="https://img.shields.io/badge/Composio-Tool%20Router-orange" alt="Composio">
  </a>
  <a href="https://platform.claude.com/docs/en/agent-sdk/overview">
    <img src="https://img.shields.io/badge/Claude-Agent%20SDK-blue" alt="Claude Agent SDK">
  </a>
  <a href="https://github.com/anthropics/claude-code">
    <img src="https://img.shields.io/badge/Powered%20by-Claude%20Code-purple" alt="Claude Code">
  </a>
  <a href="https://twitter.com/composio">
    <img src="https://img.shields.io/twitter/follow/composio?style=social" alt="Twitter">
  </a>
</p>

<p align="center">
  An open-source desktop chat application powered by Claude Agent SDK and Composio Tool Router. Build AI agents with access to 500+ tools and persistent chat sessions.
</p>

<p align="center">
  <a href="https://platform.composio.dev?utm_source=github&utm_medium=readme&utm_campaign=open-claude-cowork">
    <img src="https://img.shields.io/badge/Get%20Started-Composio%20Platform-orange?style=for-the-badge" alt="Get Started with Composio">
  </a>
</p>

---

## Features

- **Claude Agent SDK Integration** - Full agentic capabilities with tool use and multi-turn conversations
- **Composio Tool Router** - Access to 500+ external tools (Gmail, Slack, GitHub, Google Drive, and more)
- **Persistent Chat Sessions** - Conversations maintain context across messages using SDK session management
- **Multi-Chat Support** - Create and switch between multiple chat sessions
- **Real-time Streaming** - Server-Sent Events (SSE) for smooth, token-by-token response streaming
- **Tool Call Visualization** - See tool inputs and outputs in real-time in the sidebar
- **Progress Tracking** - Todo list integration for tracking agent task progress
- **Modern UI** - Clean, dark-themed interface inspired by Claude.ai
- **Desktop App** - Native Electron application for macOS, Windows, and Linux

---

## Tech Stack

| Category | Technology |
|----------|------------|
| **Desktop Framework** | Electron.js |
| **Backend** | Node.js + Express |
| **AI Agent** | Claude Agent SDK |
| **Tool Integration** | Composio Tool Router |
| **Streaming** | Server-Sent Events (SSE) |
| **Markdown** | Marked.js |
| **Styling** | Vanilla CSS |

---

## Getting Started

### Quick Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/ComposioHQ/open-claude-cowork.git
cd open-claude-cowork

# Run the automated setup script
./setup.sh
```

The setup script will:
- Install Composio CLI if not already installed
- Guide you through Composio signup/login
- Configure your API keys in `.env`
- Install all project dependencies

### Manual Setup

If you prefer manual setup, follow these steps:

#### Prerequisites

- Node.js 18+ installed
- Anthropic API key ([console.anthropic.com](https://console.anthropic.com))
- Composio API key ([app.composio.dev](https://app.composio.dev))

#### 1. Clone the Repository

```bash
git clone https://github.com/ComposioHQ/open-claude-cowork.git
cd open-claude-cowork
```

#### 2. Install Dependencies

```bash
# Install Electron app dependencies
npm install

# Install backend dependencies
cd server
npm install
cd ..
```

#### 3. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```env
ANTHROPIC_API_KEY=your-anthropic-api-key
COMPOSIO_API_KEY=your-composio-api-key
```

### Starting the Application

#### Option 1: Docker (Recommended)

The easiest way to run the application:

```bash
# Start the application in Docker
docker-compose up --build
```

The application will be available at `http://localhost:3001`

**Docker Commands:**
```bash
# Start in background
docker-compose up -d

# View logs
docker logs open-claude-cowork-app-1 -f

# Stop the application
docker-compose down

# Rebuild after changes
docker-compose up --build
```

#### Option 2: Local Development

You need **two terminal windows**:

**Terminal 1 - Backend Server:**
```bash
cd server
npm start
```

**Terminal 2 - Electron App:**
```bash
npm start
```

Access the web version at `http://localhost:3001` or use the Electron desktop app.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Electron App                              │
│  ┌─────────────────┐    ┌─────────────────┐                     │
│  │   Main Process  │    │ Renderer Process │                    │
│  │   (main.js)     │    │  (renderer.js)   │                    │
│  └────────┬────────┘    └────────┬─────────┘                    │
│           │                      │                               │
│           └──────────┬───────────┘                               │
│                      │ IPC (preload.js)                          │
└──────────────────────┼───────────────────────────────────────────┘
                       │
                       │ HTTP + SSE
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Backend Server                               │
│  ┌─────────────────┐    ┌─────────────────┐                     │
│  │  Express.js     │───▶│ Claude Agent SDK │                    │
│  │  (server.js)    │    │  + Session Mgmt  │                    │
│  └─────────────────┘    └────────┬─────────┘                    │
│                                  │                               │
│                                  ▼                               │
│                    ┌─────────────────────────┐                   │
│                    │   Composio Tool Router  │                   │
│                    │   (MCP Server)          │                   │
│                    └─────────────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
```

### Session Management

The app uses Claude Agent SDK's built-in session management:
1. First message creates a new session, returning a `session_id`
2. Subsequent messages use `resume` option with the stored session ID
3. Full conversation context is maintained server-side

### Tool Integration

Composio Tool Router provides MCP server integration:
- Tools are authenticated per-user via Composio dashboard
- Available tools include Google Workspace, Slack, GitHub, and 500+ more
- Tool calls are streamed and displayed in real-time

---

## File Structure

```
open-claude-cowork/
├── main.js                 # Electron main process
├── preload.js              # IPC security bridge
├── renderer/
│   ├── index.html          # Chat interface
│   ├── renderer.js         # Frontend logic
│   └── style.css           # Styling
├── server/
│   ├── server.js           # Express + Claude Agent SDK + Composio
│   └── package.json
├── package.json
├── .env                    # API keys (not tracked)
└── .env.example            # Template
```

---

## Available Scripts

| Command | Description |
|---------|-------------|
| `npm start` | Start the Electron app |
| `npm run dev` | Start in development mode with live reload |
| `cd server && npm start` | Start the backend server |

---

## Troubleshooting

**Docker: "Claude Code process exited with code 1"**
- This was caused by running as root user - now fixed with non-root user in Dockerfile
- If you still see this, ensure you're using the latest version: `docker-compose up --build`

**"Failed to connect to backend"**
- Ensure backend server is running on port 3001
- Check Terminal 1 for error logs
- If using Docker, check logs: `docker logs open-claude-cowork-app-1`

**"API key error"**
- Verify `ANTHROPIC_API_KEY` in `.env` starts with `sk-ant-`
- Ensure `COMPOSIO_API_KEY` is valid
- For Docker, make sure `.env` file exists in the project root

**"Session not persisting"**
- Check server logs for session ID capture
- Ensure `chatId` is being passed from frontend

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## Resources

- [Claude Agent SDK Documentation](https://docs.anthropic.com/en/docs/claude-agent-sdk)
- [Composio Tool Router](https://docs.composio.dev/tool-router)
- [Composio Dashboard](https://app.composio.dev)
- [Electron Documentation](https://www.electronjs.org/docs)

---

<p align="center">
  Built with Claude Code and Composio
</p>
