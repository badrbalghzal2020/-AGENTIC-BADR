"""
Legal Framework Agent

Analyzes legal compliance and risks in contract documents.
"""

import os
from agno.agent import Agent
from agno.models.mistral import MistralChat


class LegalFrameworkAgent:
    """
    Agent specialized in analyzing legal compliance and risks in contracts.
    
    Responsibilities:
    - Identify applicable legal frameworks
    - Assess regulatory compliance
    - Detect ambiguous or problematic terms
    - Evaluate liability and indemnification clauses
    - Identify potential litigation risks
    """
    
    INSTRUCTIONS = """You are a Legal Analysis Expert. Analyze contracts for legal risks and compliance.

Provide a brief, readable analysis covering:
- **Governing Law**: What jurisdiction governs this contract?
- **Key Risks**: Top 3-5 legal risks identified
- **Red Flags**: Any concerning clauses or terms?
- **Legal Score**: Rate 1-10 with brief explanation

Keep your response concise and easy to read. Use bullet points and short paragraphs."""

    def __init__(self):
        """Initialize the Legal Framework Agent with Mistral model."""
        self.agent = Agent(
            name="Legal Framework Agent",
            model=MistralChat(
                id="mistral-large-latest",
                api_key=os.getenv("MISTRAL_API_KEY"),
            ),
            instructions=self.INSTRUCTIONS,
            markdown=True,
        )
    
    async def analyze(self, contract_text: str) -> dict:
        """
        Analyze the legal aspects of a contract document.
        
        Args:
            contract_text: The full text of the contract to analyze
            
        Returns:
            Dictionary containing the legal analysis results
        """
        prompt = f"""Analyze this contract for legal risks briefly:

{contract_text[:8000]}

Provide a short, readable summary of legal concerns."""

        try:
            response = await self.agent.arun(prompt)
            return {
                "agent": "Legal Framework Agent",
                "analysis_type": "legal",
                "content": response.content,
                "run_id": str(response.run_id) if response.run_id else None,
            }
        except Exception as e:
            return {
                "agent": "Legal Framework Agent",
                "analysis_type": "legal",
                "content": f"⚠️ Analysis failed: {str(e)}",
                "error": str(e),
            }
