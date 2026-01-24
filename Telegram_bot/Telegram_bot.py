import os
import json
import configparser
import tempfile
from pathlib import Path

import whisper
from openai import OpenAI
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Add FFmpeg to PATH (required for audio processing)
os.environ["PATH"] += os.pathsep + r"D:\Software\ffmpeg-8.0-full_build\bin"

# Load config values from ../config/config.ini
config = configparser.ConfigParser()
config_path = Path(__file__).parent.parent / 'config' / 'config.ini'
config.read(config_path)

TELEGRAM_TOKEN = config['telegram']['TOKEN']
OPENAI_API_KEY = config['openai']['api_key']
OPENAI_MODEL = config['openai']['model']
OPENAI_TEMPERATURE = float(config['openai']['temperature'])

# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Create OpenAI Assistant with function calling
print("Creating OpenAI Assistant...")
assistant = openai_client.beta.assistants.create(
    name="Shopping Assistant",
    instructions="You are a helpful assistant. Use the get_shopping_list function when the user asks about their shopping list, groceries, or what they need to buy. Keep responses concise and conversational.",
    model=OPENAI_MODEL,
    tools=[{
        "type": "function",
        "function": {
            "name": "get_shopping_list",
            "description": "Get items from the user's shopping list",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["pending", "completed", "all"],
                        "description": "Filter by item status. Use 'pending' for items still to buy, 'completed' for bought items, 'all' for everything."
                    }
                },
                "required": []
            }
        }
    }]
)
print(f"Assistant created with ID: {assistant.id}")

# Load Whisper model (use "base" for speed, "medium" or "large" for accuracy)
print("Loading Whisper model...")
whisper_model = whisper.load_model("base").to("cuda")
print("Whisper model loaded!")


# -----------------------------
# Speech-to-Text (Whisper)
# -----------------------------
def transcribe_audio(audio_path: str) -> str:
    """Convert audio file to text using Whisper."""
    result = whisper_model.transcribe(audio_path)
    text = result["text"]
    if isinstance(text, str):
        return text.strip()
    return str(text).strip()


# -----------------------------
# Shopping List Helper
# -----------------------------
def get_shopping_list_from_json(status: str = "pending") -> list:
    """Read shopping list from JSON file."""
    data_path = Path(__file__).parent.parent / "data" / "shopping_list.json"
    with open(data_path, "r") as f:
        data = json.load(f)
    
    if status == "all":
        return data["items"]
    return [item for item in data["items"] if item["status"] == status]


# -----------------------------
# LLM Response (OpenAI Assistants API v2)
# -----------------------------
def get_llm_response(user_message: str) -> str:
<<<<<<< Current (Your changes)
    """Get response from OpenAI LLM."""
    response = openai_client.chat.completions.create(
        model=OPENAI_MODEL,
        temperature=OPENAI_TEMPERATURE,
        messages=[
            {"role": "system", "content": (
                "You are a voice assistant. The user is speaking to you via voice messages "
                "which are transcribed to text. Your response will be converted to speech "
                "and played back to the user. Keep responses concise, natural, and conversational. "
                "Avoid using markdown, bullet points, or special formatting since your response "
                "will be spoken aloud."
            )},
            {"role": "user", "content": user_message}
        ]
=======
    """Get response from OpenAI Assistant with function calling."""
    # 1. Create thread and add message
    thread = openai_client.beta.threads.create()
    openai_client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=user_message
    )
    
    # 2. Run assistant and poll for completion
    run = openai_client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id
>>>>>>> Incoming (Background Agent changes)
    )
    
    # 3. Handle function calls if needed
    if run.status == "requires_action":
        tool_outputs = []
        for tool_call in run.required_action.submit_tool_outputs.tool_calls:
            if tool_call.function.name == "get_shopping_list":
                # Parse arguments
                args = json.loads(tool_call.function.arguments)
                status = args.get("status", "pending")
                
                # Get shopping list from JSON
                result = get_shopping_list_from_json(status)
                print(f"Function called: get_shopping_list(status={status})")
                print(f"Result: {result}")
                
                tool_outputs.append({
                    "tool_call_id": tool_call.id,
                    "output": json.dumps(result)
                })
        
        # Submit tool outputs and poll for final response
        run = openai_client.beta.threads.runs.submit_tool_outputs_and_poll(
            thread_id=thread.id,
            run_id=run.id,
            tool_outputs=tool_outputs
        )
    
    # 4. Get final response
    if run.status == "completed":
        messages = openai_client.beta.threads.messages.list(thread_id=thread.id)
        # Get the latest assistant message
        for msg in messages.data:
            if msg.role == "assistant":
                return msg.content[0].text.value
    
    return "Sorry, I couldn't generate a response."


# -----------------------------
# Text-to-Speech (OpenAI TTS)
# -----------------------------
def text_to_speech(text: str, output_path: str, voice: str = "coral") -> None:
    """Convert text to audio file using OpenAI TTS."""
    with openai_client.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice=voice,
        input=text,
        speed=1.25
    ) as response:
        response.stream_to_file(output_path)


# -----------------------------
# Voice Message Handler
# -----------------------------
async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming voice messages."""
    if update.message is None or update.message.voice is None:
        return

    await update.message.reply_text("🎤 Processing your voice message...")

    try:
        # Create temp directory for audio files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Download voice message
            voice_file = await update.message.voice.get_file()
            input_path = os.path.join(temp_dir, "input.ogg")
            await voice_file.download_to_drive(input_path)

            # STT: Convert voice to text
            user_text = transcribe_audio(input_path)
            print(f"User said: {user_text}")

            # Send transcription to user
            await update.message.reply_text(f"📝 You said: {user_text}")

            # LLM: Get response
            llm_response = get_llm_response(user_text)
            print(f"LLM response: {llm_response}")

            # TTS: Convert response to audio
            output_path = os.path.join(temp_dir, "response.mp3")
            text_to_speech(llm_response, output_path)

            # Send audio response
            with open(output_path, "rb") as audio_file:
                await update.message.reply_voice(voice=audio_file)

            # Also send text response
            await update.message.reply_text(f"💬 {llm_response}")

    except Exception as e:
        print(f"Error processing voice message: {e}")
        await update.message.reply_text(f"❌ Error processing voice message: {str(e)}")


# -----------------------------
# Command /start
# -----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        return
    await update.message.reply_text(
        "🎤 Voice Assistant Bot\n\n"
        "Send me a voice message and I'll:\n"
        "1. Convert it to text\n"
        "2. Process it with AI\n"
        "3. Reply with voice!\n\n"
        "Just record and send a voice message to get started."
    )


# -----------------------------
# Main
# -----------------------------
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))

    # Voice message handler
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
