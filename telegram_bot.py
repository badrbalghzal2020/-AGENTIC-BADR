"""
Telegram Bot for Multi-Agent Contract Analysis

Allows users to upload contract documents (PDF/DOCX) via Telegram
and receive comprehensive AI-powered analysis from multiple agents.
"""

import os
import asyncio
from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from agents.contract_agent import ContractStructureAgent
from agents.legal_agent import LegalFrameworkAgent
from agents.negotiation_agent import NegotiationAgent
from agents.manager_agent import ManagerAgent
from utils.document_processor import extract_text_from_pdf, extract_text_from_docx

# Load environment variables
load_dotenv()

# Constants
MAX_MESSAGE_LENGTH = 4096  # Telegram message limit


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /start command - send welcome message with instructions.
    """
    welcome_message = """
📄 *Welcome to Contract Analysis Bot!*

I use multiple AI agents to analyze your contract documents:

🏗️ *Structure Agent* - Document organization & flow
⚖️ *Legal Agent* - Compliance & risk assessment  
🤝 *Negotiation Agent* - Leverage points & strategies
👔 *Manager Agent* - Consolidated executive report

*How to use:*
Simply upload a contract file (PDF or DOCX) and I'll analyze it for you!

_Supported formats: PDF, DOCX_
"""
    await update.message.reply_text(welcome_message, parse_mode="Markdown")


async def run_agents(contract_text: str) -> dict:
    """
    Run all specialized agents in parallel, then consolidate with manager.
    
    Args:
        contract_text: Extracted text from the contract document
        
    Returns:
        Dictionary with all agent results and consolidated report
    """
    # Initialize agents
    structure_agent = ContractStructureAgent()
    legal_agent = LegalFrameworkAgent()
    negotiation_agent = NegotiationAgent()
    manager_agent = ManagerAgent()
    
    # Phase 1: Run 3 agents in parallel
    structure_result, legal_result, negotiation_result = await asyncio.gather(
        structure_agent.analyze(contract_text),
        legal_agent.analyze(contract_text),
        negotiation_agent.analyze(contract_text),
    )
    
    agent_results = {
        "structure": structure_result,
        "legal": legal_result,
        "negotiation": negotiation_result,
    }
    
    # Phase 2: Manager consolidates all results
    manager_result = await manager_agent.analyze(agent_results)
    
    return {
        "agents": agent_results,
        "consolidated": manager_result,
    }


def format_agent_result(title: str, icon: str, result: dict) -> str:
    """
    Format a single agent's result for Telegram message.
    
    Args:
        title: Display title for the agent
        icon: Emoji icon
        result: Agent result dictionary
        
    Returns:
        Formatted string for Telegram
    """
    content = result.get("content", "No analysis available")
    
    # Handle content that might be an object
    if hasattr(content, 'content'):
        content = content.content
    
    content = str(content)
    
    # Truncate if too long
    if len(content) > 3000:
        content = content[:3000] + "\n\n_...truncated for length_"
    
    return f"{icon} *{title}*\n\n{content}"


async def send_results(update: Update, results: dict) -> None:
    """
    Format and send analysis results to user in multiple messages.
    
    Args:
        update: Telegram update object
        results: Dictionary containing all agent results
    """
    agent_results = results["agents"]
    consolidated = results["consolidated"]
    
    # Send each agent's analysis
    messages = [
        ("Structure Analysis", "🏗️", agent_results.get("structure", {})),
        ("Legal Analysis", "⚖️", agent_results.get("legal", {})),
        ("Negotiation Analysis", "🤝", agent_results.get("negotiation", {})),
    ]
    
    for title, icon, result in messages:
        formatted = format_agent_result(title, icon, result)
        await send_long_message(update, formatted)
        await asyncio.sleep(0.5)  # Small delay between messages
    
    # Send consolidated report
    await update.message.reply_text("─" * 30)
    consolidated_text = format_agent_result(
        "Executive Report", "👔", consolidated
    )
    await send_long_message(update, consolidated_text)


async def send_long_message(update: Update, text: str) -> None:
    """
    Send a message, splitting if it exceeds Telegram's limit.
    
    Args:
        update: Telegram update object
        text: Message text to send
    """
    # Split into chunks if needed
    if len(text) <= MAX_MESSAGE_LENGTH:
        await update.message.reply_text(text, parse_mode="Markdown")
    else:
        # Split at paragraph breaks when possible
        chunks = []
        current_chunk = ""
        
        for line in text.split("\n"):
            if len(current_chunk) + len(line) + 1 <= MAX_MESSAGE_LENGTH:
                current_chunk += line + "\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = line + "\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        for chunk in chunks:
            try:
                await update.message.reply_text(chunk, parse_mode="Markdown")
            except Exception:
                # Fallback without markdown if parsing fails
                await update.message.reply_text(chunk)
            await asyncio.sleep(0.3)


async def document_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle uploaded document files - download, extract text, and run analysis.
    """
    document = update.message.document
    file_name = document.file_name.lower()
    
    # Validate file type
    if not (file_name.endswith(".pdf") or file_name.endswith(".docx")):
        await update.message.reply_text(
            "❌ *Unsupported file format*\n\n"
            "Please upload a PDF or DOCX file.",
            parse_mode="Markdown"
        )
        return
    
    # Send processing message
    status_msg = await update.message.reply_text(
        "📥 *Downloading file...*",
        parse_mode="Markdown"
    )
    
    try:
        # Download file from Telegram servers
        file = await context.bot.get_file(document.file_id)
        file_bytes = await file.download_as_bytearray()
        file_bytes = bytes(file_bytes)
        
        # Update status
        await status_msg.edit_text("📖 *Extracting text from document...*", parse_mode="Markdown")
        
        # Extract text based on file type
        if file_name.endswith(".pdf"):
            contract_text = extract_text_from_pdf(file_bytes)
        else:
            contract_text = extract_text_from_docx(file_bytes)
        
        if not contract_text.strip():
            await status_msg.edit_text(
                "❌ *Could not extract text from document*\n\n"
                "The file appears to be empty or contains only images.",
                parse_mode="Markdown"
            )
            return
        
        # Update status
        await status_msg.edit_text(
            "🔄 *Running multi-agent analysis...*\n\n"
            "This may take a minute. Analyzing with:\n"
            "• 🏗️ Structure Agent\n"
            "• ⚖️ Legal Agent\n"
            "• 🤝 Negotiation Agent\n"
            "• 👔 Manager Agent",
            parse_mode="Markdown"
        )
        
        # Run the analysis
        results = await run_agents(contract_text)
        
        # Delete status message
        await status_msg.delete()
        
        # Send completion header
        await update.message.reply_text(
            f"✅ *Analysis Complete!*\n\n"
            f"📄 File: `{document.file_name}`\n"
            f"📏 Characters analyzed: {len(contract_text):,}",
            parse_mode="Markdown"
        )
        
        # Send results
        await send_results(update, results)
        
    except Exception as e:
        error_message = str(e)
        await status_msg.edit_text(
            f"❌ *Error during analysis*\n\n"
            f"Something went wrong: {error_message}\n\n"
            f"Please try again or contact support.",
            parse_mode="Markdown"
        )


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    help_text = """
📚 *Help - Contract Analysis Bot*

*Commands:*
/start - Welcome message & instructions
/help - Show this help message

*How to analyze a contract:*
1. Upload a PDF or DOCX file
2. Wait for the analysis to complete
3. Receive detailed reports from 4 AI agents

*Agents explained:*
🏗️ *Structure* - Analyzes document organization
⚖️ *Legal* - Identifies risks & compliance issues
🤝 *Negotiation* - Finds leverage points
👔 *Manager* - Consolidates all findings

_Analysis typically takes 30-60 seconds._
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")


def main() -> None:
    """Main entry point - initialize and run the Telegram bot."""
    # Get bot token from environment
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    
    if not token:
        print("❌ Error: TELEGRAM_BOT_TOKEN not found in environment variables!")
        print("Please add your bot token to the .env file:")
        print("TELEGRAM_BOT_TOKEN=your_token_here")
        return
    
    # Check for Mistral API key
    if not os.getenv("MISTRAL_API_KEY"):
        print("❌ Error: MISTRAL_API_KEY not found in environment variables!")
        return
    
    print("🤖 Starting Contract Analysis Telegram Bot...")
    
    # Build application
    application = Application.builder().token(token).build()
    
    # Register handlers
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(CommandHandler("help", help_handler))
    application.add_handler(MessageHandler(filters.Document.ALL, document_handler))
    
    # Run the bot
    print("✅ Bot is running! Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()

