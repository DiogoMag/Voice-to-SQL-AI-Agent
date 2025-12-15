import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import configparser

# Load config values from ../config/config.ini
config = configparser.ConfigParser()
config.read('../config/config.ini')

TOKEN = config['telegram']['TOKEN']



# -----------------------------
# Função para obter preço BTC
# -----------------------------
def get_btc_price_usd():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": "bitcoin", "vs_currencies": "usd"}
    response = requests.get(url, params=params).json()
    return response["bitcoin"]["usd"]

# -----------------------------
# Função para obter Fear & Greed
# -----------------------------
def get_fng():
    url = "https://api.alternative.me/fng/"
    response = requests.get(url).json()
    value = response["data"][0]["value"]
    classification = response["data"][0]["value_classification"]
    return value, classification

# -----------------------------
# Comando /btc
# -----------------------------
async def btc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        price = get_btc_price_usd()
        await update.message.reply_text(f"💰 BTC: {price} USD")
    except:
        await update.message.reply_text("Erro ao obter o preço do BTC.")

# -----------------------------
# Comando /fng
# -----------------------------
async def fng(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        value, classification = get_fng()
        await update.message.reply_text(
            f"📊 Fear & Greed Index\n\nValor: {value}\nSentimento: {classification}"
        )
    except:
        await update.message.reply_text("Erro ao obter o Fear & Greed Index.")

# -----------------------------
# Comando /market (BTC + FNG)
# -----------------------------
async def market(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        price = get_btc_price_usd()
        value, classification = get_fng()

        await update.message.reply_text(
            f"📈 **Market Overview**\n\n"
            f"💰 BTC: {price} USD\n"
            f"📊 Fear & Greed: {value} ({classification})"
        )

    except:
        await update.message.reply_text("Erro ao obter dados do mercado.")

# -----------------------------
# Comando /shouldibuy
# -----------------------------
async def should_i_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        value, classification = get_fng()
        value = int(value)

        if value < 25:
            await update.message.reply_text(
                f"🤔 Should you buy?\n\n"
                f"📊 Fear & Greed: {value} ({classification})\n"
                f"✅ O índice está abaixo de 25 — zona de medo.\n"
                f"💡 Pode ser uma boa altura para comprar."
            )
        else:
            await update.message.reply_text(
                f"🤔 Should you buy?\n\n"
                f"📊 Fear & Greed: {value} ({classification})\n"
                f"❌ O índice está acima de 25.\n"
                f"💡 Não recomendo comprar agora."
            )

    except:
        await update.message.reply_text("Erro ao obter dados para análise.")

# -----------------------------
# Start
# -----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bot is On! Commands avaiable:\n"
        "/btc - Bitcoin Price\n"
        "/fng - Fear & Greed Index\n"
        "/market - Market Vision\n"
        "/shouldibuy - Ask a recomendation based on FnG"
    )

# -----------------------------
# Main
# -----------------------------
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("btc", btc))
    app.add_handler(CommandHandler("fng", fng))
    app.add_handler(CommandHandler("market", market))
    app.add_handler(CommandHandler("shouldibuy", should_i_buy))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()