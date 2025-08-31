# YouTube MCP Server

A Model Context Protocol (MCP) server that provides comprehensive YouTube integration with video search, detailed video information retrieval, and transcript fetching capabilities.

## Features

- **🔍 Video Search**: Search YouTube videos with pagination support
- **📹 Video Details**: Get comprehensive video information including statistics, content details, and metadata
- **📝 Transcript Fetching**: Real transcript extraction with intelligent language prioritization
- **🌐 Multi-language Support**: Automatic language detection and fallback for transcripts
- **⚡ Async Performance**: Built with async/await for optimal performance
- **🔒 Input/Output Validation**: Complete schema validation with detailed error reporting

## Tools

### 1. `search_videos`

Search for videos on YouTube with flexible pagination.

**Parameters:**
- `query` (string, required): Search query for finding videos
- `pageToken` (string, optional): Token for pagination to get next/previous page results

**Example:**
```json
{
  "query": "python programming tutorial",
  "pageToken": "CAUQAA"
}
```

**Returns:** Search results with video snippets and pagination tokens

### 2. `get_videos`

Get detailed information about specific YouTube videos.

**Parameters:**
- `ids` (array, required): List of video IDs to retrieve (max 50)
- `parts` (array, optional): Parts of video data to retrieve
  - Available parts: `snippet`, `contentDetails`, `statistics`, `status`, `player`, `recordingDetails`, `fileDetails`, `processingDetails`, `suggestions`, `liveStreamingDetails`, `localizations`, `topicDetails`
  - Default: `["snippet"]`

**Example:**
```json
{
  "ids": ["dQw4w9WgXcQ", "9bZkp7q19f0"],
  "parts": ["snippet", "contentDetails", "statistics"]
}
```

**Returns:** Comprehensive video data including duration, view counts, like counts, descriptions, and more

### 3. `get_transcript`

Extract video transcripts with intelligent language handling.

**Parameters:**
- `videoId` (string, required): YouTube video ID
- `language` (string, optional): Preferred language code (e.g., 'en', 'es', 'fr')

**Language Priority:**
1. **Requested language** (if specified)
2. **English** (fallback)
3. **Manual transcripts** (preferred over auto-generated)
4. **Any available transcript**

**Example:**
```json
{
  "videoId": "dQw4w9WgXcQ",
  "language": "en"
}
```

**Returns:** Transcript with text segments, precise timestamps, and language metadata

## Installation

### Prerequisites

1. **YouTube Data API v3 Key**:
   - Visit [Google Cloud Console](https://console.developers.google.com/)
   - Create a new project or select an existing one
   - Enable YouTube Data API v3
   - Create credentials (API Key)
   - Copy the API key for configuration

### Setup

1. **Install the server:**
   ```bash
   git clone <repository-url>
   cd youtube-mcp-server
   uv sync
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your YouTube API key:
   # YOUTUBE_API_KEY=your_actual_api_key_here
   ```

3. **Test installation:**
   ```bash
   uv run python test_server.py
   ```

### Claude Desktop Integration

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "youtube": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/yourusername/youtube-mcp-server",
        "youtube-mcp-server"
      ],
      "env": {
        "YOUTUBE_API_KEY": "your_youtube_api_key_here"
      }
    }
  }
}
```

## Usage Examples

### Basic Video Search
```python
# Search for Python tutorials
result = await search_videos("python programming tutorial")
```

### Get Video Details
```python
# Get comprehensive video information
result = await get_videos(
    ids=["dQw4w9WgXcQ"], 
    parts=["snippet", "contentDetails", "statistics"]
)
```

### Fetch Transcript
```python
# Get transcript in preferred language
result = await get_transcript("dQw4w9WgXcQ", language="en")
```

## API Rate Limits

The YouTube Data API v3 has the following quota limits:

- **Default quota**: 10,000 units per day
- **Search requests**: 100 units each
- **Video details**: 1 unit per video
- **Transcript requests**: No additional quota cost (uses separate API)

**Typical usage:**
- Video search + details: ~110 units (allows ~90 searches/day)
- Transcript fetching: No quota impact

## Development

### Project Structure

```
youtube-mcp-server/
├── youtube_mcp_server/
│   ├── __init__.py
│   ├── __main__.py
│   ├── server.py          # MCP server implementation
│   ├── handlers.py        # Tool function implementations
│   └── tools.json         # Tool schema definitions
├── test_cases.json        # Comprehensive test cases
├── test_server.py         # Test suite with schema validation
├── main.py               # Development entry point
├── pyproject.toml        # Project configuration
└── README.md
```

### Running Tests

```bash
# Run comprehensive test suite
uv run python test_server.py

# Run the server locally
uv run python main.py
```

### Adding Features

1. **Define tool schema** in `youtube_mcp_server/tools.json`
2. **Implement function** in `youtube_mcp_server/handlers.py`
3. **Update mapping** in `TOOL_FUNCTIONS`
4. **Add test cases** in `test_cases.json`
5. **Run tests** to validate

## Error Handling

The server provides comprehensive error handling:

- **🔑 API Key Issues**: Clear messages for missing/invalid YouTube API keys
- **📊 Quota Management**: Informative messages about API quota limits
- **✅ Input Validation**: Detailed validation errors for incorrect parameters
- **🌐 Network Resilience**: Graceful handling of connection issues
- **🔍 Schema Validation**: Full input/output validation with detailed error messages

## Technical Details

### Dependencies

- **MCP Framework**: `mcp>=1.6.0` for Model Context Protocol support
- **Google API Client**: `google-api-python-client>=2.0.0` for YouTube Data API
- **Transcript API**: `youtube-transcript-api>=0.6.0` for transcript extraction
- **Environment**: `python-dotenv>=1.0.0` for configuration management
- **Validation**: `jsonschema>=4.0.0` for schema validation

### Performance

- **Async Architecture**: All operations use async/await for optimal performance
- **Connection Pooling**: Efficient HTTP connection management
- **Error Recovery**: Automatic retry logic for transient failures
- **Schema Caching**: Tool schemas loaded once at startup

### Security

- **Environment Variables**: API keys stored securely in environment
- **Input Sanitization**: All inputs validated against strict schemas
- **Rate Limiting**: Built-in respect for YouTube API rate limits
- **Error Isolation**: Detailed error messages without exposing internals

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes with tests
4. Ensure all tests pass: `uv run python test_server.py`
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- **Documentation**: Check test cases in `test_cases.json` for usage examples
- **Validation**: Run `uv run python test_server.py` to validate your setup
- **API Reference**: [YouTube Data API v3 Documentation](https://developers.google.com/youtube/v3)
- **Issues**: Open GitHub issues for bugs or feature requests

---

Built with ❤️ using the Model Context Protocol framework.