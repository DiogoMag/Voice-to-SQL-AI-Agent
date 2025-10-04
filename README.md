# Voice-Activated MySQL AI Agent
AI-powered voice interface for MySQL. Converts spoken queries into SQL, retrieves results, and responds in natural language.

## Overview
An AI-powered voice interface for MySQL. Converts spoken queries into SQL, executes them, and returns natural-language responses. Designed for intuitive, hands-free data exploration.

## Features
- 🎙️ Voice input via speech-to-text
- 🧠 Natural language understanding and SQL generation
- 🗄️ Secure MySQL query execution
- 💬 Human-readable response formatting
- 🔒 Input sanitization and query validation

## Architecture

🔄 Data Flow Overview
- Voice Input: User speaks a query.
- Speech-to-Text: Converts voice to text (e.g., Whisper).
- NLP Interpretation: AI agent parses intent and generates SQL.
- SQL Validation: Sanitizes and validates the query.
- Database Execution: Runs the query on MySQL.
- Response Generation: Formats results into natural language.
- (Optional) Text-to-Speech: Speaks the answer back to the user.

🧱 Component Breakdown
- voice_input.py: Captures and transcribes voice.
- nlp_agent.py: Uses LLM to interpret and generate SQL.
- sql_executor.py: Connects to MySQL and runs queries.
- response_builder.py: Converts raw results into readable answers.
- main.py: Orchestrates the full pipeline.

📊 Diagram


## Tech Stack
- Python
- OpenAI / Local LLM
- Whisper / Google Speech API
- MySQL Connector / SQLAlchemy
- Optional: pyttsx3 (Text-to-Speech), Gradio/Streamlit (UI)
  
## 🧰 Tech Stack Mapping
| Component                        | Package(s) in `requirements.txt`                                     |
|----------------------------------|----------------------------------------------------------------------|
| **Python**                       | Base language – no package needed                                    |
| **OpenAI / Local LLM**           | `openai`, `transformers`, `torch`                                    |
| **Whisper / Google Speech API**  | `whisper`, `SpeechRecognition`, `pyaudio`                            |
| **MySQL Connector / SQLAlchemy** | `mysql-connector-python`, `SQLAlchemy` (optional ORM)                |
| **Text-to-Speech (optional)**    | `pyttsx3`                                                             |
| **UI (optional)**                | `gradio` or `streamlit`                                              |
| **Environment Config**           | `python-dotenv`                                                      |

## Setup
```bash
git clone https://github.com/DiogoMag/Voice-to-SQL-AI-Agent.git
cd Voice-to-SQL-AI-Agent
pip install -r requirements.txt
```

## Security
- SQL injection protection
- Role-based query filtering (optional)
- Environment-based credential management

