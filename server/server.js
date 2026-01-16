import express from 'express';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';
import dotenv from 'dotenv';
import { query } from '@anthropic-ai/claude-agent-sdk';
import { Composio } from '@composio/core';
import fs from 'fs/promises';
import { existsSync } from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config({ path: path.join(__dirname, '..', '.env') });

// Create temp directory for uploaded files
const UPLOAD_DIR = path.join(__dirname, 'uploads');
if (!existsSync(UPLOAD_DIR)) {
  await fs.mkdir(UPLOAD_DIR, { recursive: true });
}

const app = express();
const PORT = process.env.PORT || 3001;

// Initialize Composio
const composio = new Composio();

const composioSessions = new Map();

const chatSessions = new Map();

// Store pending permission requests
const pendingPermissions = new Map();

// Middleware
app.use(cors());
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ limit: '50mb', extended: true }));

// Serve static files from renderer directory
app.use(express.static(path.join(__dirname, '..', 'renderer')));

// Chat endpoint using Claude Agent SDK
app.post('/api/chat', async (req, res) => {
  const { message, chatId, userId = 'default-user', attachments = [] } = req.body;

  console.log('[CHAT] Request received:', message);
  console.log('[CHAT] Chat ID:', chatId);
  console.log('[CHAT] Attachments:', attachments.length);

  if (!message) {
    return res.status(400).json({ error: 'Message is required' });
  }

  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache, no-transform');
  res.setHeader('Connection', 'keep-alive');
  res.setHeader('X-Accel-Buffering', 'no');
  res.flushHeaders();

  try {
    // Get or create Composio session for this user
    let composioSession = composioSessions.get(userId);
    if (!composioSession) {
      console.log('[COMPOSIO] Creating new session for user:', userId);
      composioSession = await composio.create(userId);
      composioSessions.set(userId, composioSession);
      console.log('[COMPOSIO] Session created with MCP URL:', composioSession.mcp.url);
    }

    // Check if we have an existing Claude session for this chat
    console.log('[CHAT] All stored sessions:', Array.from(chatSessions.entries()));
    const existingSessionId = chatId ? chatSessions.get(chatId) : null;
    console.log('[CHAT] Existing session ID for', chatId, ':', existingSessionId || 'none (new chat)');

    // Build prompt with attachments support
    let promptContent = message;
    const uploadedFiles = [];
    
    // If there are attachments, save them to disk and reference in message
    if (attachments && attachments.length > 0) {
      for (const attachment of attachments) {
        if (attachment.type && attachment.type.startsWith('image/')) {
          // Image attachment - extract base64 data and save
          const base64Match = attachment.data.match(/^data:([^;]+);base64,(.+)$/);
          if (base64Match) {
            const ext = attachment.name ? path.extname(attachment.name) : '.png';
            const filename = `${Date.now()}_${Math.random().toString(36).substr(2, 9)}${ext}`;
            const filepath = path.join(UPLOAD_DIR, filename);
            await fs.writeFile(filepath, Buffer.from(base64Match[2], 'base64'));
            uploadedFiles.push({ name: attachment.name, path: filepath });
            console.log('[CHAT] Saved image:', filepath);
          }
        } else if (attachment.data) {
          // Text/other file - save raw data
          const filename = attachment.name || `file_${Date.now()}_${Math.random().toString(36).substr(2, 9)}.txt`;
          const filepath = path.join(UPLOAD_DIR, filename);
          
          // If data is base64, decode it
          if (attachment.data.startsWith('data:')) {
            const base64Match = attachment.data.match(/^data:([^;]+);base64,(.+)$/);
            if (base64Match) {
              await fs.writeFile(filepath, Buffer.from(base64Match[2], 'base64'));
            }
          } else {
            // Plain text data
            await fs.writeFile(filepath, attachment.data, 'utf-8');
          }
          
          uploadedFiles.push({ name: attachment.name || filename, path: filepath });
          console.log('[CHAT] Saved file:', filepath);
        }
      }
      
      // Add file references to the message
      if (uploadedFiles.length > 0) {
        const fileList = uploadedFiles.map(f => `- ${f.name}: ${f.path}`).join('\n');
        promptContent = `${message}\n\nNahrané soubory:\n${fileList}`;
        console.log('[CHAT] Modified prompt with files:', promptContent);
      }
    }

    // Build query options
    const queryOptions = {
      allowedTools: ['Read', 'Write', 'Edit', 'Bash', 'Glob', 'Grep', 'WebSearch', 'WebFetch', 'TodoWrite', 'Skill'],
      disallowedTools: ['NotebookEdit', 'ExitPlanMode', 'EnterPlanMode', 'BashOutput', 'KillShell', 'Task', 'SlashCommand'],
      settingSources: ['user', 'project'],
      maxTurns: 20,
      mcpServers: {
        composio: {
          type: 'http',
          url: composioSession.mcp.url,
          headers: composioSession.mcp.headers
        }
      },
      permissionMode: 'bypassPermissions'
    };

    // If we have an existing session, resume it
    if (existingSessionId) {
      queryOptions.resume = existingSessionId;
      console.log('[CHAT] Resuming session:', existingSessionId);
    }

    console.log('[CHAT] Calling Claude Agent SDK...');

    // Track usage
    let totalUsage = {
      input_tokens: 0,
      output_tokens: 0,
      cache_creation_input_tokens: 0,
      cache_read_input_tokens: 0
    };

    // Stream responses from Claude Agent SDK with error handling
    try {
      for await (const chunk of query({
        prompt: promptContent,
        options: queryOptions
      })) {
      console.log('📦 AGENT CHUNK:', JSON.stringify(chunk, null, 2));
      
      // Capture usage information from assistant messages
      if (chunk.type === 'assistant' && chunk.message?.usage) {
        const usage = chunk.message.usage;
        totalUsage.input_tokens += usage.input_tokens || 0;
        totalUsage.output_tokens += usage.output_tokens || 0;
        totalUsage.cache_creation_input_tokens += usage.cache_creation_input_tokens || 0;
        totalUsage.cache_read_input_tokens += usage.cache_read_input_tokens || 0;
      }



      // Capture session ID from system init message
      // Try multiple possible locations for session_id
      if (chunk.type === 'system' && chunk.subtype === 'init') {
        const newSessionId = chunk.session_id || chunk.data?.session_id || chunk.sessionId;
        if (newSessionId && chatId) {
          chatSessions.set(chatId, newSessionId);
          console.log('[CHAT] Session ID captured:', newSessionId);
          console.log('[CHAT] Total sessions stored:', chatSessions.size);
        } else {
          console.log('[CHAT] No session_id found in init message');
        }
        // Send session ID to frontend
        if (newSessionId) {
          res.write(`data: ${JSON.stringify({ type: 'session_init', session_id: newSessionId })}\n\n`);
        }
        continue;
      }

      // Handle USER chunks with tool results
      if (chunk.type === 'user' && chunk.tool_use_result) {
        console.log('[CHAT] 🔧 Tool result chunk detected');
        // Extract tool result from the chunk
        const toolResult = chunk.tool_use_result;
        let resultText = '';
        
        if (Array.isArray(toolResult)) {
          for (const item of toolResult) {
            if (item.type === 'text') {
              resultText += item.text;
            }
          }
        }
        
        // Also check message.content for tool_use_id
        let toolUseId = null;
        if (chunk.message?.content?.[0]?.tool_use_id) {
          toolUseId = chunk.message.content[0].tool_use_id;
        }
        
        const resultEvent = {
          type: 'tool_result',
          result: resultText || JSON.stringify(toolResult),
          tool_use_id: toolUseId
        };
        res.write(`data: ${JSON.stringify(resultEvent)}\n\n`);
        console.log('[CHAT] ✅ Sent tool result for:', toolUseId);
        continue;
      }

      // If it's an assistant message, extract and emit text content
      if (chunk.type === 'assistant' && chunk.message && chunk.message.content) {
        const content = chunk.message.content;
        const usage = chunk.message.usage; // Get usage for this specific message
        
        if (Array.isArray(content)) {
          for (const block of content) {
            if (block.type === 'text' && block.text) {
              res.write(`data: ${JSON.stringify({ type: 'text', content: block.text })}\n\n`);
            } else if (block.type === 'tool_use') {
              const toolEvent = {
                type: 'tool_use',
                name: block.name,
                input: block.input,
                id: block.id,
                usage: usage // Include usage info with tool use
              };
              res.write(`data: ${JSON.stringify(toolEvent)}\n\n`);
              console.log('[CHAT] Tool use:', block.name, 'Usage:', usage);
            } else if (block.type === 'tool_result') {
              // Tool results may come in content blocks
              const resultEvent = {
                type: 'tool_result',
                result: block.content || block.result || block,
                tool_use_id: block.tool_use_id || block.id
              };
              res.write(`data: ${JSON.stringify(resultEvent)}\n\n`);
              console.log('[CHAT] Tool result for:', block.tool_use_id || block.id);
            }
          }
        }
        continue;
      }

      // If it's a tool result, format it nicely
      if (chunk.type === 'tool_result' || chunk.type === 'result') {
        const eventData = {
          type: 'tool_result',
          result: chunk.result || chunk.content || chunk,
          tool_use_id: chunk.tool_use_id
        };
        res.write(`data: ${JSON.stringify(eventData)}\n\n`);
        continue;
      }

      // Skip system chunks, pass through others
      if (chunk.type !== 'system') {
        res.write(`data: ${JSON.stringify(chunk)}\n\n`);
      }
    }

    // Send usage information
      if (totalUsage.input_tokens > 0 || totalUsage.output_tokens > 0) {
        // Calculate cost (Claude Sonnet 3.5 pricing as of 2024)
        // Input: $3 per million tokens, Output: $15 per million tokens
        // Cache write: $3.75 per million tokens, Cache read: $0.30 per million tokens
        const inputCost = (totalUsage.input_tokens / 1000000) * 3;
        const outputCost = (totalUsage.output_tokens / 1000000) * 15;
        const cacheWriteCost = (totalUsage.cache_creation_input_tokens / 1000000) * 3.75;
        const cacheReadCost = (totalUsage.cache_read_input_tokens / 1000000) * 0.30;
        const totalCost = inputCost + outputCost + cacheWriteCost + cacheReadCost;

        res.write(`data: ${JSON.stringify({ 
          type: 'usage', 
          usage: totalUsage,
          cost: {
            input: inputCost,
            output: outputCost,
            cache_write: cacheWriteCost,
            cache_read: cacheReadCost,
            total: totalCost
          }
        })}\n\n`);
        console.log('[CHAT] Total usage:', totalUsage, 'Cost: $' + totalCost.toFixed(4));
      }

      // Send completion signal
      res.write('data: {"type": "done"}\n\n');
      res.end();
      console.log('[CHAT] Stream completed');
    } catch (error) {
      console.error('[CHAT] Error:', error.message);
      console.error('[CHAT] Stack:', error.stack);
      res.write(`data: ${JSON.stringify({ type: 'error', message: error.message })}\n\n`);
      res.end();
    }
  } catch (error) {
    console.error('[CHAT] Request error:', error.message);
    res.status(500).json({ error: error.message });
  }
});

// Health check endpoint
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Permission response endpoint
app.post('/api/permission', (req, res) => {
  const { requestId, allowed } = req.body;
  
  console.log(`[PERMISSION] Response for ${requestId}: ${allowed ? 'ALLOWED' : 'DENIED'}`);
  
  const resolver = pendingPermissions.get(requestId);
  if (resolver) {
    pendingPermissions.delete(requestId);
    resolver({ allowed, reason: allowed ? null : 'User denied' });
    res.json({ success: true });
  } else {
    res.status(404).json({ error: 'Request not found' });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`\n✓ Backend server running on http://localhost:${PORT}`);
  console.log(`✓ Frontend available at: http://localhost:${PORT}`);
  console.log(`✓ Chat endpoint: POST http://localhost:${PORT}/api/chat`);
  console.log(`✓ Health check: GET http://localhost:${PORT}/api/health\n`);
});
