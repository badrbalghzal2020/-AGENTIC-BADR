"""
Multi-Agent Contract Analysis System

A Streamlit application that uses multiple AI agents to analyze contract documents.
Agents run in parallel using asyncio for efficient processing.
"""

import os
import asyncio
from dotenv import load_dotenv
import streamlit as st

from agents.contract_agent import ContractStructureAgent
from agents.legal_agent import LegalFrameworkAgent
from agents.negotiation_agent import NegotiationAgent
from agents.manager_agent import ManagerAgent
from utils.document_processor import extract_text_from_file

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Contract Analysis System",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A5F;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .agent-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 4px solid;
    }
    .structure-card { border-left-color: #4CAF50; }
    .legal-card { border-left-color: #2196F3; }
    .negotiation-card { border-left-color: #FF9800; }
    .manager-card { border-left-color: #9C27B0; }
    .stExpander {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


def check_api_key() -> bool:
    """Check if the Mistral API key is configured."""
    api_key = os.getenv("MISTRAL_API_KEY")
    if not api_key or api_key == "your_key_here":
        st.error(
            "⚠️ **MISTRAL_API_KEY not configured!**\n\n"
            "Please set your Mistral API key in the `.env` file:\n"
            "```\nMISTRAL_API_KEY=your_actual_api_key\n```\n\n"
            "Get your API key from: https://console.mistral.ai/api-keys/"
        )
        return False
    return True


async def run_parallel_analysis(contract_text: str) -> dict:
    """
    Run all three specialized agents in parallel.
    
    Args:
        contract_text: The extracted text from the contract document
        
    Returns:
        Dictionary containing results from all agents
    """
    # Initialize agents
    structure_agent = ContractStructureAgent()
    legal_agent = LegalFrameworkAgent()
    negotiation_agent = NegotiationAgent()
    
    # Run all three agents in parallel
    structure_result, legal_result, negotiation_result = await asyncio.gather(
        structure_agent.analyze(contract_text),
        legal_agent.analyze(contract_text),
        negotiation_agent.analyze(contract_text),
    )
    
    return {
        "structure": structure_result,
        "legal": legal_result,
        "negotiation": negotiation_result,
    }


async def run_manager_analysis(agent_results: dict) -> dict:
    """
    Run the manager agent to consolidate all results.
    
    Args:
        agent_results: Results from all specialized agents
        
    Returns:
        Consolidated analysis from the manager agent
    """
    manager_agent = ManagerAgent()
    return await manager_agent.analyze(agent_results)


def display_agent_result(title: str, result: dict, card_class: str, icon: str):
    """Display a single agent's result in a formatted card."""
    with st.expander(f"{icon} {title}", expanded=True):
        # Display the analysis content
        if result and "content" in result:
            content = result["content"]
            # Handle if content is a string or has a content attribute
            if hasattr(content, 'content'):
                content = content.content
            st.markdown(str(content))
        elif result and "error" in result:
            st.error(f"Error: {result['error']}")
        else:
            st.warning("No analysis available")


def main():
    """Main application entry point."""
    # Header
    st.markdown('<p class="main-header">📄 Multi-Agent Contract Analysis</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Upload a contract document (PDF or DOCX) for comprehensive AI-powered analysis</p>',
        unsafe_allow_html=True
    )
    
    # Check API key
    if not check_api_key():
        st.stop()
    
    # Sidebar
    with st.sidebar:
        st.header("📋 About")
        st.markdown("""
        This system uses **4 specialized AI agents** to analyze your contracts:
        
        1. **🏗️ Structure Agent**
           - Document organization
           - Section hierarchy
           - Missing sections
        
        2. **⚖️ Legal Agent**
           - Legal compliance
           - Risk assessment
           - Liability analysis
        
        3. **🤝 Negotiation Agent**
           - Leverage points
           - Modification opportunities
           - Strategy recommendations
        
        4. **👔 Manager Agent**
           - Consolidates all findings
           - Traceable reasoning
           - Action priorities
        """)
        
        st.divider()
        st.caption("Powered by Mistral AI & Agno Framework")
    
    # File uploader - using key to ensure proper state management
    uploaded_file = st.file_uploader(
        "Upload Contract Document",
        type=["pdf", "docx"],
        help="Supported formats: PDF, DOCX",
        key="contract_uploader",
        accept_multiple_files=False
    )
    
    if uploaded_file is not None:
        # Extract text from the document
        with st.spinner("📖 Extracting text from document..."):
            try:
                contract_text = extract_text_from_file(uploaded_file)
            except ValueError as e:
                st.error(f"❌ {str(e)}")
                st.stop()
            except Exception as e:
                st.error(f"❌ Error processing document: {str(e)}")
                st.stop()
        
        # Show extracted text preview
        with st.expander("📝 Document Preview", expanded=False):
            st.text_area(
                "Extracted Text",
                contract_text[:5000] + ("..." if len(contract_text) > 5000 else ""),
                height=200,
                disabled=True
            )
            st.caption(f"Total characters: {len(contract_text):,}")
        
        # Analyze button
        if st.button("🔍 Analyze Contract", type="primary", use_container_width=True):
            # Phase 1: Run parallel agent analysis
            st.markdown("### 🔄 Phase 1: Parallel Agent Analysis")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("Running Structure, Legal, and Negotiation agents in parallel...")
            
            try:
                # Run parallel analysis
                agent_results = asyncio.run(run_parallel_analysis(contract_text))
                progress_bar.progress(60)
                
                # Phase 2: Manager consolidation
                st.markdown("### 🔄 Phase 2: Manager Consolidation")
                status_text.text("Manager agent consolidating results...")
                
                manager_result = asyncio.run(run_manager_analysis(agent_results))
                progress_bar.progress(100)
                status_text.text("✅ Analysis complete!")
                
                # Display results - Vertical layout
                st.markdown("---")
                st.markdown("## 📊 Analysis Results")
                
                # 1. Contract Structure Analysis
                display_agent_result(
                    "Contract Structure Analysis",
                    agent_results.get("structure"),
                    "structure-card",
                    "🏗️"
                )
                
                # 2. Legal Analysis
                display_agent_result(
                    "Legal Analysis",
                    agent_results.get("legal"),
                    "legal-card",
                    "⚖️"
                )
                
                # 3. Negotiation Analysis
                display_agent_result(
                    "Negotiation Analysis",
                    agent_results.get("negotiation"),
                    "negotiation-card",
                    "🤝"
                )
                
                # 4. Manager consolidated report
                st.markdown("---")
                st.markdown("## 👔 Consolidated Executive Report")
                display_agent_result(
                    "Manager Consolidated Analysis",
                    manager_result,
                    "manager-card",
                    "👔"
                )
                
                # Success message
                st.success("✅ Contract analysis completed successfully!")
                
                # Download results option
                st.markdown("---")
                st.markdown("### 📥 Export Results")
                
                # Prepare results for download
                all_results = {
                    "structure_analysis": agent_results.get("structure", {}),
                    "legal_analysis": agent_results.get("legal", {}),
                    "negotiation_analysis": agent_results.get("negotiation", {}),
                    "consolidated_report": manager_result,
                }
                
                import json
                results_json = json.dumps(all_results, indent=2, default=str)
                
                st.download_button(
                    label="📄 Download Full Analysis (JSON)",
                    data=results_json,
                    file_name="contract_analysis_results.json",
                    mime="application/json",
                )
                
            except Exception as e:
                st.error(f"❌ Error during analysis: {str(e)}")
                st.exception(e)


if __name__ == "__main__":
    main()
