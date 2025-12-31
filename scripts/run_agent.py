"""
Run Autonomous Scientific Agent
Simple launcher for autonomous research
"""

from utils.logger import setup_logger
from agent.autonomous_agent import AutonomousScientist
from utils.session_manager import SessionManager
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


logger = setup_logger()


def main():
    """Run autonomous research agent"""

    # Configuration
    # Change this to your research topic, or pass session_id to resume
    query = "lithium ion battery solid electrolyte"
    max_papers = 20
    max_hypotheses = 20
    max_iterations = 1

    # Optional: Provide a session_id from the dashboard to track progress
    # Example: session_id = "session_20241231_143022"
    session_id = None

    logger.info("🚀 Starting Autonomous Scientific Agent")
    logger.info(f"Query: {query}")
    logger.info(f"Max papers: {max_papers}")
    logger.info(f"Max hypotheses: {max_hypotheses}")
    logger.info(f"Max iterations: {max_iterations}")

    if session_id:
        logger.info(f"Session ID: {session_id}")

    # Create agent
    agent = AutonomousScientist(domain="materials science")

    # Run research
    try:
        summary = agent.run(
            query=query,
            max_papers=max_papers,
            max_hypotheses=max_hypotheses,
            max_iterations=max_iterations,
            session_id=session_id
        )

        # Save results
        agent.save_results(session_id=session_id)

        # Print summary
        logger.success("\n" + "="*60)
        logger.success("RESEARCH COMPLETE")
        logger.success("="*60)
        logger.info(f"Papers collected: {summary['papers_collected']}")
        logger.info(f"Research gaps: {summary['gaps_identified']}")
        logger.info(f"Hypotheses generated: {summary['hypotheses_generated']}")
        logger.info(f"Hypotheses tested: {summary['hypotheses_tested']}")
        logger.success(f"Discoveries: {summary['discoveries']}")
        logger.info("\nResults saved to: data/agent_results/")
        logger.info("\n🎉 Done! View results in Streamlit dashboard:")
        logger.info("   streamlit run dashboard/app.py")

    except Exception as e:
        logger.error(f"Research failed: {e}")

        # Mark session as failed if session_id provided
        if session_id:
            try:
                session_mgr = SessionManager()
                session_mgr.update_session_status(session_id, "failed", str(e))
            except Exception as session_error:
                logger.warning(
                    f"Could not update session status: {session_error}")

        raise


if __name__ == "__main__":
    main()
