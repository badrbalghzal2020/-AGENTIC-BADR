"""
Manager Agent

Consolidates outputs from all specialized agents with traceable reasoning.
"""

import os
import json
from typing import Dict, Any
from agno.agent import Agent
from agno.models.mistral import MistralChat


class ManagerAgent:
    """
    Agent that consolidates and synthesizes outputs from all specialized agents.
    
    Responsibilities:
    - Consolidate findings from all agents
    - Identify conflicts or inconsistencies
    - Provide traceable reasoning
    - Generate executive summary and recommendations
    - Prioritize action items
    """
    
    INSTRUCTIONS = """You are a Contract Analysis Manager. Consolidate findings from other agents into an executive summary.

Provide a brief, readable report covering:
- **Executive Summary**: 2-3 sentence overview
- **Overall Score**: Rate 1-10 for contract quality
- **Top 3 Concerns**: Most important issues to address
- **Recommendation**: Should they sign? (Yes/No/With changes)
- **Next Steps**: 3-5 action items

Keep your response concise and actionable. Use bullet points and short paragraphs."""

    def __init__(self):
        """Initialize the Manager Agent with Mistral model."""
        self.agent = Agent(
            name="Manager Agent",
            model=MistralChat(
                id="mistral-large-latest",
                api_key=os.getenv("MISTRAL_API_KEY"),
            ),
            instructions=self.INSTRUCTIONS,
            markdown=True,
        )
    
    async def analyze(self, agent_results: Dict[str, Any]) -> dict:
        """
        Consolidate results from all specialized agents.
        
        Args:
            agent_results: Dictionary containing results from all agents
                - structure: Results from Contract Structure Agent
                - legal: Results from Legal Framework Agent
                - negotiation: Results from Negotiation Agent
                
        Returns:
            Dictionary containing the consolidated analysis
        """
        # Format the agent results for the prompt
        structure_analysis = agent_results.get("structure", {}).get("content", "No structural analysis available")
        legal_analysis = agent_results.get("legal", {}).get("content", "No legal analysis available")
        negotiation_analysis = agent_results.get("negotiation", {}).get("content", "No negotiation analysis available")
        
        prompt = f"""Consolidate these agent findings into a brief executive summary:

**Structure Analysis:**
{structure_analysis}

**Legal Analysis:**
{legal_analysis}

**Negotiation Analysis:**
{negotiation_analysis}

Provide a short, actionable summary with your recommendation."""

        try:
            response = await self.agent.arun(prompt)
            return {
                "agent": "Manager Agent",
                "analysis_type": "consolidated",
                "content": response.content,
                "run_id": str(response.run_id) if response.run_id else None,
            }
        except Exception as e:
            return {
                "agent": "Manager Agent",
                "analysis_type": "consolidated",
                "content": f"⚠️ Consolidation failed: {str(e)}",
                "error": str(e),
            }
