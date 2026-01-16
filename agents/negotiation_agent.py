"""
Negotiation Agent

Analyzes negotiation opportunities and leverage points in contract documents.
"""

import os
from agno.agent import Agent
from agno.models.mistral import MistralChat


class NegotiationAgent:
    """
    Agent specialized in identifying negotiation opportunities in contracts.
    
    Responsibilities:
    - Identify favorable and unfavorable terms
    - Find negotiation leverage points
    - Suggest possible modifications
    - Assess bargaining positions
    """
    
    INSTRUCTIONS = """You are a Contract Negotiation Expert. Analyze contracts for negotiation opportunities.

Provide a brief, readable analysis covering:
- **Favorable Terms**: What's good in this contract?
- **Unfavorable Terms**: What needs negotiation?
- **Quick Wins**: Easy changes likely to be accepted
- **Negotiation Score**: Rate 1-10 with brief explanation

Keep your response concise and easy to read. Use bullet points and short paragraphs."""

    def __init__(self):
        """Initialize the Negotiation Agent with Mistral model."""
        self.agent = Agent(
            name="Negotiation Agent",
            model=MistralChat(
                id="mistral-large-latest",
                api_key=os.getenv("MISTRAL_API_KEY"),
            ),
            instructions=self.INSTRUCTIONS,
            markdown=True,
        )
    
    async def analyze(self, contract_text: str) -> dict:
        """
        Analyze negotiation opportunities in a contract document.
        
        Args:
            contract_text: The full text of the contract to analyze
            
        Returns:
            Dictionary containing the negotiation analysis results
        """
        prompt = f"""Analyze this contract for negotiation opportunities briefly:

{contract_text[:8000]}

Provide a short, readable summary of negotiation points."""

        try:
            response = await self.agent.arun(prompt)
            return {
                "agent": "Negotiation Agent",
                "analysis_type": "negotiation",
                "content": response.content,
                "run_id": str(response.run_id) if response.run_id else None,
            }
        except Exception as e:
            return {
                "agent": "Negotiation Agent",
                "analysis_type": "negotiation",
                "content": f"⚠️ Analysis failed: {str(e)}",
                "error": str(e),
            }
