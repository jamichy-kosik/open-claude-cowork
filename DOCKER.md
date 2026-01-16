# Claude Agent Chat - Docker Setup

## Prerequisites

- Docker
- Docker Compose
- Anthropic API Key

## Quick Start

1. **Set your API key** in `.env` file:
```bash
ANTHROPIC_API_KEY=your_api_key_here
```

2. **Build and start** the application:
```bash
docker-compose up --build
```

3. **Open** in your browser:
```
http://localhost:3001
```

## Docker Commands

### Start application
```bash
docker-compose up -d
```

### Stop application
```bash
docker-compose down
```

### View logs
```bash
docker-compose logs -f
```

### Rebuild after code changes
```bash
docker-compose up --build
```

### Remove everything (including volumes)
```bash
docker-compose down -v
```

## Features

✅ Complete web-based chat interface
✅ Claude Agent SDK with skills support
✅ Composio MCP integration (Gmail, etc.)
✅ File upload support
✅ Token usage & cost tracking
✅ Tool call visualization
✅ Persistent chat history (localStorage)
✅ Skills from `.claude/skills/` directory

## Skills

Place your skills in `.claude/skills/` directory. They will be mounted into the container.

## Notes

- Frontend runs on port 3001
- Backend API also on port 3001
- Uploaded files are stored in `server/uploads/`
- Skills are loaded from `.claude/skills/`
