"""
Multi-Agent Contract Analysis System - Agents Package

This package contains specialized agents for contract analysis:
- ContractStructureAgent: Analyzes document structure and organization
- LegalFrameworkAgent: Analyzes legal compliance and risks
- NegotiationAgent: Analyzes negotiation opportunities and leverage points
- ManagerAgent: Consolidates all agent outputs with traceable reasoning
"""

from agents.contract_agent import ContractStructureAgent
from agents.legal_agent import LegalFrameworkAgent
from agents.negotiation_agent import NegotiationAgent
from agents.manager_agent import ManagerAgent

__all__ = [
    "ContractStructureAgent",
    "LegalFrameworkAgent",
    "NegotiationAgent",
    "ManagerAgent",
]
# Agent modules initialization
