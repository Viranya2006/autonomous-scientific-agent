"""
Test SessionManager functionality
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from utils.session_manager import SessionManager


def test_session_manager():
    """Test basic SessionManager operations"""
    
    print("🧪 Testing SessionManager...")
    
    # Initialize
    session_mgr = SessionManager(db_path="data/test_sessions.db")
    print("✅ SessionManager initialized")
    
    # Create session
    session_id = session_mgr.create_session(
        research_topic="Test Research Topic",
        max_papers=10,
        max_hypotheses=5,
        iterations=1,
        ai_model="gemini"
    )
    print(f"✅ Session created: {session_id}")
    
    # Get session
    session = session_mgr.get_session(session_id)
    print(f"✅ Session retrieved: {session['research_topic']}")
    
    # Update progress
    session_mgr.update_session_progress(
        session_id,
        progress=50,
        phase="Testing",
        message="Test progress update"
    )
    print("✅ Progress updated to 50%")
    
    # Update status
    session_mgr.update_session_status(session_id, "running")
    print("✅ Status updated to 'running'")
    
    # List sessions
    sessions = session_mgr.list_sessions()
    print(f"✅ Listed {len(sessions)} sessions")
    
    # Get logs
    logs = session_mgr.get_session_logs(session_id)
    print(f"✅ Retrieved {len(logs)} log entries")
    
    # Mark complete
    session_mgr.update_session_status(session_id, "completed")
    print("✅ Session marked as completed")
    
    # Save results path
    session_mgr.save_session_results(session_id, "data/test_results")
    print("✅ Results path saved")
    
    # Verify final state
    final_session = session_mgr.get_session(session_id)
    assert final_session['status'] == 'completed'
    assert final_session['progress'] == 50
    assert final_session['results_path'] == 'data/test_results'
    
    print("\n🎉 All tests passed!")
    print(f"\nFinal session state:")
    print(f"  ID: {final_session['session_id']}")
    print(f"  Topic: {final_session['research_topic']}")
    print(f"  Status: {final_session['status']}")
    print(f"  Progress: {final_session['progress']}%")
    print(f"  Results: {final_session['results_path']}")
    
    # Cleanup
    session_mgr.delete_session(session_id)
    print(f"\n🧹 Test session deleted")


if __name__ == "__main__":
    test_session_manager()
