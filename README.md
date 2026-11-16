# Automated Multi-Platform Posting System

A FastAPI-based application that automatically publishes messages across multiple third-party platforms through their APIs.

## Features

- **REST API Endpoint**: `POST /posting` for submitting messages
- **Input Validation**: Message length (≤200 chars), exactly one CTA link, URL validation
- **Multi-Platform Support**: 8 platforms integrated (Twitter/X, LinkedIn, Facebook, Reddit, Telegram, Discord, Mastodon, Bluesky)
- **Error Resilience**: Failed platforms don't block others
- **Detailed Response**: Status, posted URL, public access, timestamp, and error details per platform
- **Environment-based Configuration**: Secure credential management via `.env` file

## Supported Platforms

| Platform | API Used | Public Access |
|----------|----------|---------------|
| Twitter/X | Twitter API v2 | Yes |
| LinkedIn | LinkedIn UGC API | Yes |
| Facebook | Graph API v19.0 | Yes |
| Reddit | Reddit OAuth API | Yes |
| Telegram | Bot API | No (Private chats) |
| Discord | Webhook API | No (Server only) |
| Mastodon | Mastodon API | Yes |
| Bluesky | AT Protocol | Yes |

## Project Structure

```
automated-posting/
├── app/
│   ├── main.py                 # FastAPI app & endpoint
│   ├── schemas.py              # Pydantic models
│   ├── config.py               # Environment configuration
│   ├── platforms/
│   │   ├── base.py             # Abstract base class
│   │   ├── twitter.py          # Twitter/X integration
│   │   ├── linkedin.py         # LinkedIn integration
│   │   ├── facebook.py         # Facebook integration
│   │   ├── reddit.py           # Reddit integration
│   │   ├── telegram.py         # Telegram integration
│   │   ├── discord.py          # Discord integration
│   │   ├── mastodon.py         # Mastodon integration
│   │   └── bluesky.py          # Bluesky integration
│   └── services/
│       └── posting_service.py  # Orchestration service
├── tests/
│   └── test_posting.py         # Unit & integration tests
├── .env.example                # Environment template
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Setup Instructions

### Prerequisites

- Python 3.10+
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd automated-posting
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API credentials
   ```

5. **Run the server**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 4000
   ```

6. **Access API Documentation**
   - Swagger UI: http://localhost:4000/docs
   - ReDoc: http://localhost:4000/redoc

## API Usage

### Endpoint

```http
POST http://localhost:4000/posting
```

### Request Body

```json
{
  "message": "Check out our latest business platform and grow your online visibility. https://example.com"
}
```

### Validation Rules

- Message must not exceed 200 characters
- Must contain exactly one CTA link (URL)
- URL must be valid (http/https)

### Response Format

```json
{
  "success": true,
  "results": [
    {
      "platform": "Twitter/X",
      "status": "success",
      "posted_url": "https://twitter.com/user/status/123",
      "public_access": true,
      "date": "2026-11-15",
      "time": "10:30:00",
      "error": null
    },
    {
      "platform": "LinkedIn",
      "status": "failed",
      "posted_url": null,
      "public_access": false,
      "date": null,
      "time": null,
      "error": "Authentication failed"
    }
  ]
}
```

### Example cURL Request

```bash
curl -X POST http://localhost:4000/posting \
  -H "Content-Type: application/json" \
  -d '{"message": "Check out our platform! https://example.com"}'
```

## Platform Configuration

Each platform requires specific API credentials. Follow these guides to obtain them:

### Twitter/X
1. Apply for developer access at https://developer.twitter.com/
2. Create a project and app
3. Generate Bearer Token (OAuth 2.0) or API Keys (OAuth 1.0a)

### LinkedIn
1. Create app at https://developer.linkedin.com/
2. Request `w_member_social` scope
3. Generate access token via OAuth 2.0

### Facebook
1. Create app at https://developers.facebook.com/
2. Add Facebook Login and Pages products
3. Generate Page Access Token with `pages_manage_posts` permission

### Reddit
1. Create app at https://www.reddit.com/prefs/apps (type: script)
2. Note client_id and client_secret
3. Use username/password for OAuth flow

### Telegram
1. Message @BotFather on Telegram
2. Create new bot with `/newbot`
3. Get chat ID by messaging bot and visiting `https://api.telegram.org/bot<TOKEN>/getUpdates`

### Discord
1. Server Settings → Integrations → Webhooks
2. Create webhook and copy URL

### Mastodon
1. Go to Preferences → Development → New Application
2. Select `write:statuses` scope
3. Copy access token

### Bluesky
1. Go to https://bsky.app/settings/app-passwords
2. Create app password
3. Use handle and app password

## Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=app tests/
```

## Sample API Requests & Responses

### Successful Request

**Request:**
```bash
curl -X POST http://localhost:4000/posting \
  -H "Content-Type: application/json" \
  -d '{"message": "Launching our new product! Check it out: https://myapp.com"}'
```

**Response:**
```json
{
  "success": true,
  "results": [
    {
      "platform": "Twitter/X",
      "status": "success",
      "posted_url": "https://twitter.com/user/status/1857423891234567890",
      "public_access": true,
      "date": "2026-11-15",
      "time": "14:32:15",
      "error": null
    },
    {
      "platform": "LinkedIn",
      "status": "success",
      "posted_url": "https://www.linkedin.com/feed/update/urn:li:activity:7263849213456789504",
      "public_access": true,
      "date": "2026-11-15",
      "time": "14:32:16",
      "error": null
    },
    {
      "platform": "Facebook",
      "status": "success",
      "posted_url": "https://www.facebook.com/123456789/posts/987654321",
      "public_access": true,
      "date": "2026-11-15",
      "time": "14:32:17",
      "error": null
    },
    {
      "platform": "Reddit",
      "status": "failed",
      "posted_url": null,
      "public_access": false,
      "date": "2026-11-15",
      "time": "14:32:18",
      "error": "Subreddit not found"
    },
    {
      "platform": "Telegram",
      "status": "success",
      "posted_url": "https://t.me/c/123456789/42",
      "public_access": false,
      "date": "2026-11-15",
      "time": "14:32:19",
      "error": null
    },
    {
      "platform": "Discord",
      "status": "success",
      "posted_url": "https://discord.com/api/webhooks/...",
      "public_access": false,
      "date": "2026-11-15",
      "time": "14:32:20",
      "error": null
    },
    {
      "platform": "Mastodon",
      "status": "success",
      "posted_url": "https://mastodon.social/@user/113456789012345678",
      "public_access": true,
      "date": "2026-11-15",
      "time": "14:32:21",
      "error": null
    },
    {
      "platform": "Bluesky",
      "status": "success",
      "posted_url": "https://bsky.app/profile/user.bsky.social/post/3kb2x...",
      "public_access": true,
      "date": "2026-11-15",
      "time": "14:32:22",
      "error": null
    }
  ]
}
```

### Validation Error Response

**Request:**
```bash
curl -X POST http://localhost:4000/posting \
  -H "Content-Type: application/json" \
  -d '{"message": "No URL in this message"}'
```

**Response:**
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "message"],
      "msg": "Message must contain exactly one CTA link (URL)",
      "input": "No URL in this message"
    }
  ]
}
```

## Test Screenshots

This section documents the test results and screenshots demonstrating the implementation.

### 1. Server Startup Logs
Terminal output showing successful server startup on port 4000:
```
INFO:     Started server process [17344]
INFO:     Waiting for application startup.
INFO:app.main:Starting Automated Multi-Platform Posting System
INFO:app.main:Configured platforms: []
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:4000 (Press CTRL+C to quit)
```

### 2. Swagger UI Documentation
API documentation available at http://localhost:4000/docs showing the `/posting` endpoint with request/response schemas.
<img width="1920" height="1080" alt="Screenshot (126)" src="https://github.com/user-attachments/assets/58329fe3-c7a2-4ad2-b00d-0be248e1abda" />



### 3. Health Check Endpoint
**Request:** `GET http://localhost:4000/health`
**Response:**
```json
{
  "status": "healthy",
  "service": "Automated Multi-Platform Posting System"
}
```

### 4. Root Endpoint
**Request:** `GET http://localhost:4000/`
**Response:**
```json
{
  "message": "Automated Multi-Platform Posting System",
  "version": "1.0.0",
  "docs": "/docs",
  "configured_platforms": [],
  "all_platforms": [
    "Twitter/X",
    "LinkedIn",
    "Facebook",
    "Reddit",
    "Telegram",
    "Discord",
    "Mastodon",
    "Bluesky"
  ]
}
```

### 5. Valid Posting Request (All Platforms - Credentials Not Configured)
**Request:**
```bash
curl -X POST http://localhost:4000/posting \
  -H "Content-Type: application/json" \
  -d '{"message": "Check out our latest business platform and grow your online visibility. https://example.com"}'
```

**Response:** (Shows all 8 platforms with "credentials not configured" errors - expected without API keys)
```json
{
  "success": false,
  "results": [
    {
      "platform": "Twitter/X",
      "status": "failed",
      "posted_url": null,
      "public_access": false,
      "date": "2026-11-16",
      "time": "12:31:41",
      "error": "Twitter API credentials not configured"
    },
    {
      "platform": "LinkedIn",
      "status": "failed",
      "posted_url": null,
      "public_access": false,
      "date": "2026-11-16",
      "time": "12:31:41",
      "error": "LinkedIn API credentials not configured"
    },
    {
      "platform": "Facebook",
      "status": "failed",
      "posted_url": null,
      "public_access": false,
      "date": "2026-11-16",
      "time": "12:31:41",
      "error": "Facebook API credentials not configured"
    },
    {
      "platform": "Reddit",
      "status": "failed",
      "posted_url": null,
      "public_access": false,
      "date": "2026-11-16",
      "time": "12:31:41",
      "error": "Reddit API credentials not configured"
    },
    {
      "platform": "Telegram",
      "status": "failed",
      "posted_url": null,
      "public_access": false,
      "date": "2026-11-16",
      "time": "12:31:41",
      "error": "Telegram Bot credentials not configured"
    },
    {
      "platform": "Discord",
      "status": "failed",
      "posted_url": null,
      "public_access": false,
      "date": "2026-11-16",
      "time": "12:31:41",
      "error": "Discord Webhook URL not configured"
    },
    {
      "platform": "Mastodon",
      "status": "failed",
      "posted_url": null,
      "public_access": false,
      "date": "2026-11-16",
      "time": "12:31:41",
      "error": "Mastodon credentials not configured"
    },
    {
      "platform": "Bluesky",
      "status": "failed",
      "posted_url": null,
      "public_access": false,
      "date": "2026-11-16",
      "time": "12:31:41",
      "error": "Bluesky credentials not configured"
    }
  ]
}
```

### 6. Validation Error - No URL
**Request:**
```bash
curl -X POST http://localhost:4000/posting \
  -H "Content-Type: application/json" \
  -d '{"message": "No URL in this message"}'
```

**Response:** (HTTP 422)
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "message"],
      "msg": "Value error, Message must contain exactly one CTA link (URL)",
      "input": "No URL in this message"
    }
  ]
}
```

### 7. Validation Error - Multiple URLs
**Request:**
```bash
curl -X POST http://localhost:4000/posting \
  -H "Content-Type: application/json" \
  -d '{"message": "Two URLs https://a.com and https://b.com"}'
```

**Response:** (HTTP 422)
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "message"],
      "msg": "Value error, Message must contain exactly one CTA link (URL)",
      "input": "Two URLs https://a.com and https://b.com"
    }
  ]
}
```

### 8. Validation Error - Invalid URL Format
**Request:**
```bash
curl -X POST http://localhost:4000/posting \
  -H "Content-Type: application/json" \
  -d '{"message": "Check out https://not-a-valid-url"}'
```

**Response:** (HTTP 422)
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "message"],
      "msg": "Value error, Invalid URL format",
      "input": "Check out https://not-a-valid-url"
    }
  ]
}
```

### 9. Validation Error - Message Too Long (>200 chars)
**Request:**
```bash
curl -X POST http://localhost:4000/posting \
  -H "Content-Type: application/json" \
  -d '{"message": "aaaaaaaa... (201 chars) ... https://example.com"}'
```

**Response:** (HTTP 422)
```json
{
  "detail": [
    {
      "type": "string_too_long",
      "loc": ["body", "message"],
      "msg": "String should have at most 200 characters",
      "input": "aaaaaaaa... (201 chars) ... https://example.com"
    }
  ]
}
```

### 10. Unit Tests Passing
**Command:** `pytest tests/ -v`
**Output:** 13 tests passed covering:
- Root endpoint
- Health endpoint
- Valid post request
- Invalid message (too long, no URL, multiple URLs, invalid URL, empty)
- Schema validation
- Posting service initialization
- Platform result schema
- Mock platform success/failure

---

## Screenshots Placeholder

Add actual screenshots to the `docs/` folder and reference them here:

### Swagger UI Documentation

<img width="1920" height="1080" alt="Screenshot (126)" src="https://github.com/user-attachments/assets/dcc78adc-399b-4768-b089-cd05fde7af23" />


### Successful Posting Response
<img width="1920" height="1080" alt="Screenshot (114)" src="https://github.com/user-attachments/assets/74e68633-20f2-4a0e-a00b-caa5217fe987" />
<img width="1920" height="1080" alt="Screenshot (115)" src="https://github.com/user-attachments/assets/7ef245de-f97f-4e97-ba91-512cfccd3b77" />
<img width="1920" height="1080" alt="Screenshot (118)" src="https://github.com/user-attachments/assets/4c3f17ce-1e2f-471b-927e-26b58982611b" />


### Validation Error
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/ad4ff6b4-8bfb-4415-abcf-f766cbe35f8b" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/b7db73bd-3218-463f-adb7-bf0ea4a7b26a" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/7a2ce7a6-c250-4010-a569-a65f5d5431b1" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/e3733371-853b-439d-9410-dbc353abc0b7" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/cd987511-a2aa-4f24-a23f-3d84e85afa5e" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/31156a5f-9496-4de5-96cc-206546fbd198" />

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/6c75d6c0-7eac-4f30-bdce-fa804192ca62" />

### Health Check
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/78feec35-9c37-478f-b70a-3a7fcfe228bb" />


### Test Results
![Uploading image.png…]()


## Error Handling

- **Platform failures are isolated**: One platform failing doesn't affect others
- **Detailed error messages**: Each failed platform returns specific error details
- **Network timeouts**: 30-second timeout per platform request
- **Graceful degradation**: Returns partial results even if some platforms fail

## Security Considerations

- All credentials stored in `.env` file (never committed)
- `.env` added to `.gitignore`
- HTTPS enforced for all API communications
- Input validation prevents injection attacks
- Rate limiting can be added via middleware

## License

This project is created for the Python Practical Test assignment.

## Contact

For questions about this implementation, please refer to the GitHub repository issues.
