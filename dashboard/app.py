"""
Streamlit Dashboard for Autonomous Scientific Agent
Beautiful web interface for monitoring and exploring research
"""

from src.utils.session_manager import SessionManager
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json
from datetime import datetime
import sys
import threading

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Page config
st.set_page_config(
    page_title="Autonomous Scientific Agent",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .stTab {
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">🧬 Autonomous Scientific Agent</h1>',
            unsafe_allow_html=True)
st.markdown("*AI-powered autonomous research system*")

# Initialize session manager
session_mgr = SessionManager()

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")

    data_dir = st.text_input("Data Directory", "data/agent_results")

    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

    st.markdown("---")
    st.markdown("### 📊 System Status")
    st.success("✅ System Active")
    st.info("🤖 GROQ Online")
    st.info("💎 Gemini Online")
    st.info("🔬 Materials Project Connected")

# Load data


@st.cache_data
def load_data(data_dir):
    """Load all data files"""
    path = Path(data_dir)
    data = {}

    try:
        if (path / "papers.csv").exists():
            data['papers'] = pd.read_csv(path / "papers.csv")

        if (path / "hypotheses.csv").exists():
            data['hypotheses'] = pd.read_csv(path / "hypotheses.csv")

        if (path / "test_results.csv").exists():
            data['test_results'] = pd.read_csv(path / "test_results.csv")

        if (path / "discoveries.json").exists():
            with open(path / "discoveries.json", 'r') as f:
                data['discoveries'] = json.load(f)

        if (path / "summary.json").exists():
            with open(path / "summary.json", 'r') as f:
                data['summary'] = json.load(f)
    except Exception as e:
        st.error(f"Error loading data: {e}")

    return data


data = load_data(data_dir)

# Main tabs
tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Home",
    "📊 Overview",
    "📚 Papers",
    "💡 Hypotheses",
    "🧪 Experiments",
    "🎉 Discoveries"
])

# Tab 0: Home - Interactive Research Launcher
with tab0:
    st.header("🏠 Research Control Center")

    # Two columns: Launch new research | Active sessions
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🚀 Launch New Research")

        with st.form("launch_research"):
            research_topic = st.text_area(
                "Research Topic",
                placeholder="Enter your research topic (e.g., 'high-entropy alloys for hydrogen storage')",
                height=100
            )

            col_a, col_b = st.columns(2)
            with col_a:
                max_papers = st.number_input(
                    "Max Papers", min_value=5, max_value=100, value=20)
                max_hypotheses = st.number_input(
                    "Max Hypotheses", min_value=3, max_value=50, value=10)

            with col_b:
                iterations = st.number_input(
                    "Iterations", min_value=1, max_value=10, value=3)
                ai_model = st.selectbox("AI Model", ["gemini", "groq"])

            submit = st.form_submit_button(
                "🚀 Start Research", use_container_width=True)

            if submit and research_topic:
                try:
                    session_id = session_mgr.create_session(
                        research_topic=research_topic,
                        max_papers=max_papers,
                        max_hypotheses=max_hypotheses,
                        iterations=iterations,
                        ai_model=ai_model
                    )
                    st.success(f"✅ Research session created: {session_id}")
                    st.info(
                        "⚠️ Note: Use scripts/run_agent.py to execute the research with this session_id")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error creating session: {e}")
            elif submit:
                st.error("Please enter a research topic")

    with col2:
        st.subheader("📋 Active Sessions")

        sessions = session_mgr.list_sessions()

        if sessions:
            for session in sessions[:5]:  # Show last 5 sessions
                status_emoji = {
                    'pending': '⏳',
                    'running': '🔄',
                    'completed': '✅',
                    'failed': '❌'
                }.get(session['status'], '❓')

                with st.expander(f"{status_emoji} {session['research_topic'][:50]}..."):
                    col_x, col_y = st.columns([2, 1])

                    with col_x:
                        st.write(f"**Status:** {session['status']}")
                        st.write(f"**Created:** {session['created_at']}")
                        if session['current_phase']:
                            st.write(f"**Phase:** {session['current_phase']}")
                        if session['progress']:
                            st.progress(session['progress'] / 100)
                            st.caption(f"Progress: {session['progress']}%")

                    with col_y:
                        if st.button("🗑️ Delete", key=f"del_{session['session_id']}"):
                            session_mgr.delete_session(session['session_id'])
                            st.success("Deleted!")
                            st.rerun()

                        if session['results_path']:
                            st.caption(f"📁 {session['results_path']}")

                    if session['error_message']:
                        st.error(f"Error: {session['error_message']}")
        else:
            st.info("No research sessions yet. Create one above!")

    st.markdown("---")

    # Quick stats
    st.subheader("📊 Session Statistics")
    if sessions:
        col_a, col_b, col_c, col_d = st.columns(4)

        total = len(sessions)
        completed = len([s for s in sessions if s['status'] == 'completed'])
        running = len([s for s in sessions if s['status'] == 'running'])
        failed = len([s for s in sessions if s['status'] == 'failed'])

        col_a.metric("Total Sessions", total)
        col_b.metric("✅ Completed", completed)
        col_c.metric("🔄 Running", running)
        col_d.metric("❌ Failed", failed)

# Tab 1: Overview
with tab1:
    st.header("Research Overview")

    # Metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        papers_count = len(data.get('papers', []))
        st.metric("📚 Papers Collected", papers_count)

    with col2:
        hypotheses_count = len(data.get('hypotheses', []))
        st.metric("💡 Hypotheses Generated", hypotheses_count)

    with col3:
        tests_count = len(data.get('test_results', []))
        st.metric("🧪 Tests Completed", tests_count)

    with col4:
        discoveries_count = len(data.get('discoveries', []))
        st.metric("🎉 Discoveries", discoveries_count)

    st.markdown("---")

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Hypothesis Novelty Distribution")
        if 'hypotheses' in data and not data['hypotheses'].empty:
            if 'novelty_score' in data['hypotheses'].columns:
                fig = px.histogram(
                    data['hypotheses'],
                    x='novelty_score',
                    nbins=20,
                    title="Novelty Scores",
                    color_discrete_sequence=['#667eea']
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No novelty scores available")
        else:
            st.info("No hypotheses data available")

    with col2:
        st.subheader("Feasibility Analysis")
        if 'hypotheses' in data and not data['hypotheses'].empty:
            if 'feasibility_level' in data['hypotheses'].columns:
                feasibility_counts = data['hypotheses']['feasibility_level'].value_counts(
                )
                fig = px.pie(
                    values=feasibility_counts.values,
                    names=feasibility_counts.index,
                    title="Feasibility Levels",
                    color_discrete_sequence=['#667eea', '#764ba2', '#f093fb']
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No feasibility data available")
        else:
            st.info("No hypotheses data available")

    # Test results
    if 'test_results' in data and not data['test_results'].empty:
        st.subheader("Test Results Overview")
        if 'test_result' in data['test_results'].columns:
            result_counts = data['test_results']['test_result'].value_counts()

            fig = go.Figure(data=[
                go.Bar(
                    x=result_counts.index,
                    y=result_counts.values,
                    marker_color=['#10b981', '#ef4444', '#f59e0b']
                )
            ])
            fig.update_layout(
                title="Test Results Distribution",
                xaxis_title="Result",
                yaxis_title="Count",
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)

# Tab 2: Papers
with tab2:
    st.header("Research Papers")

    if 'papers' in data and not data['papers'].empty:
        papers_df = data['papers'].copy()

        # Check for failed analyses
        failed_papers = pd.DataFrame()
        if 'key_findings' in papers_df.columns:
            # Identify failed papers (empty key_findings or "Analysis failed" message)
            failed_mask = (
                papers_df['key_findings'].isna() |
                (papers_df['key_findings'] == '') |
                (papers_df['key_findings'].astype(str).str.contains(
                    'Analysis failed', case=False, na=False))
            )
            failed_papers = papers_df[failed_mask]
            # Show only successful ones initially
            papers_df = papers_df[~failed_mask]

        # Display failed papers section if any exist
        if not failed_papers.empty:
            with st.expander(f"⚠️ Failed Analyses ({len(failed_papers)} papers)", expanded=False):
                st.warning(
                    f"The following {len(failed_papers)} papers failed analysis due to API errors or timeouts.")

                for idx, paper in failed_papers.iterrows():
                    col_a, col_b = st.columns([4, 1])

                    with col_a:
                        st.markdown(f"**{paper.get('title', 'Untitled')}**")
                        st.caption(f"Authors: {paper.get('authors', 'N/A')}")

                        # Show error message if available
                        if 'research_significance' in paper and pd.notna(paper['research_significance']):
                            if 'failed' in str(paper['research_significance']).lower():
                                st.caption(
                                    f"❌ {paper['research_significance']}")

                    with col_b:
                        if st.button("🔄 Retry", key=f"retry_{idx}"):
                            st.info(
                                "Note: Re-run the agent with skip_cache=True to retry failed papers")

                        if 'arxiv_id' in paper and pd.notna(paper['arxiv_id']):
                            st.markdown(
                                f"[📑 arXiv](https://arxiv.org/abs/{paper['arxiv_id']})", unsafe_allow_html=True)

                    st.markdown("---")

        # Filters
        col1, col2 = st.columns([3, 1])
        with col1:
            search = st.text_input("🔍 Search papers", "")
        with col2:
            sort_by = st.selectbox(
                "Sort by", ["relevance_score", "title", "published"])

        # Apply search
        if search:
            mask = papers_df.apply(
                lambda row: search.lower() in str(row).lower(), axis=1)
            papers_df = papers_df[mask]

        # Sort
        if sort_by in papers_df.columns:
            papers_df = papers_df.sort_values(sort_by, ascending=False)

        # Display successful papers
        st.write(f"Showing {len(papers_df)} successfully analyzed papers")

        for idx, paper in papers_df.iterrows():
            with st.expander(f"📄 {paper.get('title', 'Untitled')}"):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(f"**Authors:** {paper.get('authors', 'N/A')}")
                    st.markdown(
                        f"**Published:** {paper.get('published', 'N/A')}")
                    st.markdown(
                        f"**Abstract:** {paper.get('summary', 'N/A')[:300]}...")

                    if 'key_findings' in paper and pd.notna(paper['key_findings']):
                        st.markdown(
                            f"**Key Findings:** {paper['key_findings']}")

                with col2:
                    if 'relevance_score' in paper:
                        st.metric(
                            "Relevance", f"{paper['relevance_score']:.1f}/10")

                    if 'arxiv_id' in paper:
                        st.markdown(
                            f"[📑 View on arXiv](https://arxiv.org/abs/{paper['arxiv_id']})")
    else:
        st.info("No papers data available. Run the agent to collect papers.")

# Tab 3: Hypotheses
with tab3:
    st.header("Generated Hypotheses")

    if 'hypotheses' in data and not data['hypotheses'].empty:
        # Filters
        col1, col2, col3 = st.columns(3)

        with col1:
            novelty_filter = st.slider("Min Novelty Score", 0.0, 1.0, 0.0)

        with col2:
            if 'feasibility_level' in data['hypotheses'].columns:
                feasibility_options = [
                    'All'] + list(data['hypotheses']['feasibility_level'].unique())
                feasibility_filter = st.selectbox(
                    "Feasibility", feasibility_options)
            else:
                feasibility_filter = 'All'

        with col3:
            search = st.text_input("🔍 Search hypotheses", "")

        hypotheses_df = data['hypotheses'].copy()

        # Apply filters
        if 'novelty_score' in hypotheses_df.columns:
            hypotheses_df = hypotheses_df[hypotheses_df['novelty_score']
                                          >= novelty_filter]

        if feasibility_filter != 'All' and 'feasibility_level' in hypotheses_df.columns:
            hypotheses_df = hypotheses_df[hypotheses_df['feasibility_level']
                                          == feasibility_filter]

        if search:
            mask = hypotheses_df.apply(
                lambda row: search.lower() in str(row).lower(), axis=1)
            hypotheses_df = hypotheses_df[mask]

        st.write(f"Showing {len(hypotheses_df)} hypotheses")

        # Display
        for idx, hyp in hypotheses_df.iterrows():
            with st.expander(f"💡 {hyp.get('hypothesis', 'Untitled')[:100]}..."):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(
                        f"**Hypothesis:** {hyp.get('hypothesis', 'N/A')}")
                    st.markdown(
                        f"**Materials:** {hyp.get('materials', 'N/A')}")
                    st.markdown(f"**Method:** {hyp.get('method', 'N/A')}")
                    st.markdown(
                        f"**Expected Outcome:** {hyp.get('expected_outcome', 'N/A')}")

                with col2:
                    if 'novelty_score' in hyp:
                        st.metric("Novelty", f"{hyp['novelty_score']:.2f}")
                    if 'feasibility_score' in hyp:
                        st.metric("Feasibility",
                                  f"{hyp['feasibility_score']:.2f}")
                    if 'priority_score' in hyp:
                        st.metric("Priority", f"{hyp['priority_score']:.2f}")
    else:
        st.info("No hypotheses data available. Run the agent to generate hypotheses.")

# Tab 4: Experiments
with tab4:
    st.header("Experimental Results")

    if 'test_results' in data and not data['test_results'].empty:
        # Filter by result
        result_filter = st.multiselect(
            "Filter by result",
            ['PASS', 'FAIL', 'INCONCLUSIVE'],
            default=['PASS', 'FAIL', 'INCONCLUSIVE']
        )

        tests_df = data['test_results'].copy()

        if 'test_result' in tests_df.columns:
            tests_df = tests_df[tests_df['test_result'].isin(result_filter)]

        st.write(f"Showing {len(tests_df)} test results")

        # Display results
        for idx, test in tests_df.iterrows():
            result = test.get('test_result', 'UNKNOWN')
            color = {'PASS': '🟢', 'FAIL': '🔴',
                     'INCONCLUSIVE': '🟡'}.get(result, '⚪')

            with st.expander(f"{color} {test.get('hypothesis', 'Untitled')[:100]}..."):
                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(
                        f"**Hypothesis:** {test.get('hypothesis', 'N/A')}")
                    st.markdown(f"**Result:** {result}")

                    if 'test_evidence' in test:
                        st.markdown("**Evidence:**")
                        try:
                            evidence = json.loads(test['test_evidence']) if isinstance(
                                test['test_evidence'], str) else test['test_evidence']
                            st.json(evidence)
                        except:
                            st.write(test['test_evidence'])

                with col2:
                    if 'test_confidence' in test:
                        confidence = test['test_confidence']
                        st.metric("Confidence", f"{confidence:.2%}")
                        st.progress(confidence)
    else:
        st.info("No test results available. Run the agent to test hypotheses.")

# Tab 5: Discoveries
with tab5:
    st.header("🎉 Research Discoveries")

    if 'discoveries' in data and data['discoveries']:
        st.success(f"Found {len(data['discoveries'])} promising discoveries!")

        for i, discovery in enumerate(data['discoveries'], 1):
            with st.container():
                st.markdown(f"### Discovery #{i}")

                col1, col2 = st.columns([3, 1])

                with col1:
                    st.markdown(
                        f"**Hypothesis:** {discovery.get('hypothesis', 'N/A')}")
                    st.markdown(
                        f"**Evidence:** {discovery.get('evidence', 'N/A')}")

                with col2:
                    confidence = discovery.get('confidence', 0)
                    st.metric("Confidence", f"{confidence:.2%}")
                    st.progress(confidence)
                    st.caption(
                        f"Iteration: {discovery.get('iteration', 'N/A')}")

                st.markdown("---")
    else:
        st.info("No discoveries yet. Run the agent to start autonomous research!")

        st.markdown("""
        ### How to get started:
        
        1. **Configure API keys** in `.env` file
        2. **Run the agent** using `scripts/run_agent.py`
        3. **Monitor progress** in this dashboard
        4. **Review discoveries** and validated hypotheses
        
        The autonomous agent will:
        - 📚 Collect relevant research papers
        - 🤖 Analyze and extract knowledge gaps
        - 💡 Generate novel hypotheses
        - 🧪 Test hypotheses computationally
        - 🎉 Identify promising discoveries
        """)

# Footer
st.markdown("---")
st.markdown("*Built with Streamlit, Plotly, and ❤️*")
