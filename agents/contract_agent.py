"""
Contract Structure Agent

Analyzes the structure and organization of contract documents.
"""

import os
from agno.agent import Agent
from agno.models.mistral import MistralChat


class ContractStructureAgent:
    """
    Agent specialized in analyzing contract document structure and organization.
    
    Responsibilities:
    - Identify document sections and their hierarchy
    - Analyze clause breakdown and logical flow
    - Detect missing sections or structural issues
    - Evaluate formatting consistency
    """
    
    INSTRUCTIONS = """You are a Contract Structure Analysis Expert. Analyze contracts for structure and organization.

Provide a brief, readable analysis covering:
- **Sections Found**: List main sections you identified
- **Document Flow**: Is the contract logically organized?
- **Missing Sections**: Any standard sections that are missing?
- **Structure Score**: Rate 1-10 with brief explanation

Keep your response concise and easy to read. Use bullet points and short paragraphs."""

    def __init__(self):
        """Initialize the Contract Structure Agent with Mistral model."""
        self.agent = Agent(
            name="Contract Structure Agent",
            model=MistralChat(
                id="mistral-large-latest",
                api_key=os.getenv("MISTRAL_API_KEY"),
            ),
            instructions=self.INSTRUCTIONS,
            markdown=True,
        )
    
    async def analyze(self, contract_text: str) -> dict:
        """
        Analyze the structure of a contract document.
        
        Args:
            contract_text: The full text of the contract to analyze
            
        Returns:
            Dictionary containing the structural analysis results
        """
        prompt = f"""Analyze this contract's structure briefly:

{contract_text[:8000]}

Provide a short, readable summary of the document structure."""

        try:
            response = await self.agent.arun(prompt)
            return {
                "agent": "Contract Structure Agent",
                "analysis_type": "structural",
                "content": response.content,
                "run_id": str(response.run_id) if response.run_id else None,
            }
        except Exception as e:
            return {
                "agent": "Contract Structure Agent",
                "analysis_type": "structural",
                "content": f"⚠️ Analysis failed: {str(e)}",
                "error": str(e),
            }
