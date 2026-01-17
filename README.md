# Multi-Agent Contract Analysis System

AI-powered contract analysis using multiple specialized agents running in parallel.

## Features

- **4 Specialized AI Agents:**
  - 🏗️ **Structure Agent** - Document organization & section analysis
  - ⚖️ **Legal Agent** - Compliance & risk assessment
  - 🤝 **Negotiation Agent** - Leverage points & strategies
  - 👔 **Manager Agent** - Consolidated executive report

- **Two Interfaces:**
  - 🌐 Streamlit Web App
  - 🤖 Telegram Bot

- **Supported Formats:** PDF, DOCX

---

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the template file and add your API keys:

```bash
copy ENV_TEMPLATE.txt .env
```

Edit `.env` with your keys:

```
MISTRAL_API_KEY=your_mistral_api_key_here
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
```

---

## Running the Application

### Option 1: Streamlit Web App

```bash
streamlit run app.py
```

Then open http://localhost:8501 in your browser.

### Option 2: Telegram Bot

```bash
python telegram_bot.py
```

---

## Telegram Bot Setup

### Getting Your Bot Token from BotFather

1. Open Telegram and search for **@BotFather**
2. Start a chat and send `/newbot`
3. Follow the prompts:
   - Enter a name for your bot (e.g., "Contract Analyzer")
   - Enter a username (must end in `bot`, e.g., `ContractAnalyzer_bot`)
4. BotFather will give you a token like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`
5. Copy this token to your `.env` file:

```
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
```

### Using the Telegram Bot

1. **Start the bot:**
   ```bash
   python telegram_bot.py
   ```

2. **In Telegram:**
   - Search for your bot by its username
   - Send `/start` to see the welcome message
   - Upload a PDF or DOCX contract file
   - Wait for the multi-agent analysis (30-60 seconds)
   - Receive detailed reports from all 4 agents

### Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message & instructions |
| `/help` | Show help information |

---

## Project Structure

```
contract-agent-system/
├── app.py                 # Streamlit web interface
├── telegram_bot.py        # Telegram bot interface
├── agents/
│   ├── contract_agent.py  # Structure analysis agent
│   ├── legal_agent.py     # Legal framework agent
│   ├── negotiation_agent.py # Negotiation strategy agent
│   └── manager_agent.py   # Consolidation manager agent
├── utils/
│   └── document_processor.py # PDF/DOCX text extraction
├── requirements.txt
├── ENV_TEMPLATE.txt
└── README.md
```

---

## API Keys Required

| Service | Purpose | Get it from |
|---------|---------|-------------|
| Mistral AI | LLM for agents | [console.mistral.ai](https://console.mistral.ai/api-keys/) |
| Telegram | Bot interface | [@BotFather](https://t.me/botfather) |

---

## License

MIT

