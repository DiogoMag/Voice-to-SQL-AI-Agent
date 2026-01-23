# 🗣️ Voice Telegram Pi Assistant

Voice messages → Raspberry Pi → STT → LLM → RDS (todos/shopping) → TTS replies

## 📖 Table of Contents
- [🚀 Quick Start](#-quick-start)
- [✨ Features](#features)
- [🏗️ Architecture](#architecture)
- [🛠️ Tech Stack](#tech-stack)
- [⚙️ Configuration](#configuration)
- [🗄️ Database Schema](#database-schema)
- [🔧 Development](#development)
- [📈 Roadmap](#roadmap)

## 🚀 Quick Start
```bash
git clone https://github.com/yourusername/voice-telegram-pi.git && cd voice-telegram-pi
cp .env.example .env && nano .env  # Add your tokens/keys
pip install -r requirements.txt
python src/bot.py
```

Send a voice message to your Telegram bot and get audio replies!

## ✨ Features
- 🔄 Full voice→text→LLM→voice pipeline
- 🛒 Shopping list queries from RDS RA3
- ✅ Todo list retrieval and formatting
- 🤖 Intent-based routing (general Qs vs data/tools)
- 🥧 Optimized for Raspberry Pi deployment

## 🏗️ Architecture

```
Telegram Voice Msg → bot.py 
                    ↓
                stt.py (Whisper)
                    ↓
            intent_router.py ──┐
                               ├─ LLM (general Qs)
                               └─ RDS RA3 (lists)
                                         ↓
                                      tts.py
                                         ↓
                                   Telegram Reply
```

**Core modules:**
- `src/bot.py` - Telegram handler & audio forwarding
- `src/audio/stt.py` - Speech-to-text
- `src/audio/tts.py` - Text-to-speech  
- `src/llm/client.py` - LLM API wrapper
- `src/rds/client.py` - RDS RA3 queries
- `src/core/intent_router.py` - Routes queries to LLM or DB
- `src/core/pipeline.py` - End-to-end orchestration

## 🛠️ Tech Stack
| Component | Technology |
|-----------|------------|
| Language | Python 3.11+ |
| Runtime | Raspberry Pi OS |
| Bot Framework | python-telegram-bot |
| STT | OpenAI Whisper (local) |
| TTS | gTTS or ElevenLabs |
| LLM | OpenAI GPT-4o-mini |
| Database | Amazon RDS RA3 (PostgreSQL) |

**Requirements:**
```bash
pip install python-telegram-bot openai-whisper gtts psycopg2-binary openai python-dotenv
```

## ⚙️ Configuration
Copy `.env.example` → `.env`:

```env
# Telegram
TELEGRAM_BOT_TOKEN=your_botfather_token

# LLM  
OPENAI_API_KEY=sk-your-openai-key

# RDS RA3 (PostgreSQL)
RDS_HOST=your-rds-endpoint.rds.amazonaws.com
RDS_PORT=5432
RDS_USER=your_db_user
RDS_PASSWORD=your_db_password
RDS_DB_NAME=personal_assistant

# Audio
STT_MODEL=base
TTS_VOICE=en-GB-Standard-A
```

## 🗄️ Database Schema
```sql
-- Shopping list
CREATE TABLE shopping_list (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR(50) NOT NULL,
  item_name VARCHAR(200) NOT NULL,
  quantity VARCHAR(50),
  added_at TIMESTAMP DEFAULT NOW(),
  status VARCHAR(20) DEFAULT 'pending'
);

-- Todo list  
CREATE TABLE todos (
  id SERIAL PRIMARY KEY,
  user_id VARCHAR(50) NOT NULL,
  task TEXT NOT NULL,
  due_date TIMESTAMP,
  status VARCHAR(20) DEFAULT 'open',
  created_at TIMESTAMP DEFAULT NOW()
);
```

## 🔧 Development
**Project structure:**
```
voice-telegram-pi/
├── src/
│   ├── bot.py          # Telegram entrypoint
│   ├── audio/         # STT/TTS modules
│   ├── core/          # Pipeline & intent logic
│   ├── llm/           # LLM client
│   └── rds/           # Database client
├── .env.example
├── requirements.txt
└── README.md
```

**Add new intents:**
1. Update `intent_router.py` with keyword patterns
2. Add handler in `core/handlers.py`
3. Test with voice: "What's on my shopping list?"

**Conventions:**
- PEP8 + type hints (`mypy`)
- Structured logging
- Virtualenv required

## 📈 Roadmap
- [ ] Unit tests for intent routing
- [ ] Multi-language STT/TTS
- [ ] RDS connection pooling
- [ ] Voice command history
- [ ] Docker deployment

***

**👤 Author**: Diogo M
