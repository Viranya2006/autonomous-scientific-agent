"""
Setup Validation Script
=======================
Quick validation that Phase 1 setup is complete.

Run this after setup_project.py to verify everything is ready.
"""

import sys
from pathlib import Path


def check_mark(passed: bool) -> str:
    """Return checkmark or X."""
    return "✅" if passed else "❌"


def main():
    """Run validation checks."""
    print("=" * 60)
    print("  PHASE 1 SETUP VALIDATION")
    print("=" * 60)

    project_root = Path(__file__).parent.parent
    all_passed = True

    # Check Python version
    print("\n📋 Python Environment:")
    version = sys.version_info
    is_311 = version.major == 3 and version.minor == 11
    print(f"{check_mark(is_311)} Python {version.major}.{version.minor}.{version.micro}")
    if not is_311:
        print("   ⚠️ Recommended: Python 3.11.x")

    # Check critical files
    print("\n📄 Critical Files:")
    files_to_check = [
        "requirements.txt",
        ".env.example",
        ".gitignore",
        "README.md",
        "API_SETUP_GUIDE.md",
    ]

    for file in files_to_check:
        path = project_root / file
        exists = path.exists()
        print(f"{check_mark(exists)} {file}")
        if not exists:
            all_passed = False

    # Check source structure
    print("\n📂 Source Code Structure:")
    src_modules = [
        "src/__init__.py",
        "src/config/settings.py",
        "src/api/gemini_client.py",
        "src/api/huggingface_client.py",
        "src/api/materials_project_client.py",
        "src/utils/logger.py",
        "src/utils/helpers.py",
    ]

    for module in src_modules:
        path = project_root / module
        exists = path.exists()
        print(f"{check_mark(exists)} {module}")
        if not exists:
            all_passed = False

    # Check scripts
    print("\n🔧 Scripts:")
    scripts = [
        "scripts/setup_project.py",
        "scripts/test_all_apis.py",
    ]

    for script in scripts:
        path = project_root / script
        exists = path.exists()
        print(f"{check_mark(exists)} {script}")
        if not exists:
            all_passed = False

    # Check data directories
    print("\n📁 Data Directories:")
    dirs = [
        "data/papers",
        "data/results",
        "data/cache",
        "logs",
        "tests",
        "notebooks",
    ]

    for dir_path in dirs:
        path = project_root / dir_path
        exists = path.exists() and path.is_dir()
        print(f"{check_mark(exists)} {dir_path}/")
        if not exists:
            all_passed = False

    # Check for .env
    print("\n🔑 Configuration:")
    env_file = project_root / ".env"
    env_exists = env_file.exists()
    print(f"{check_mark(env_exists)} .env file exists")

    if not env_exists:
        print("   ⚠️ Run: Copy-Item .env.example .env")
        print("   ⚠️ Then add your API keys (see API_SETUP_GUIDE.md)")

    # Try to import modules
    print("\n🐍 Python Imports:")
    try:
        sys.path.insert(0, str(project_root / "src"))

        from config.settings import Settings
        print("✅ config.settings")

        from api.gemini_client import GeminiClient
        print("✅ api.gemini_client")

        from api.huggingface_client import HuggingFaceClient
        print("✅ api.huggingface_client")

        from api.materials_project_client import MaterialsProjectClient
        print("✅ api.materials_project_client")

        from utils.logger import setup_logger
        print("✅ utils.logger")

        from utils.helpers import save_json
        print("✅ utils.helpers")

    except ImportError as e:
        print(f"❌ Import failed: {e}")
        all_passed = False

    # Final summary
    print("\n" + "=" * 60)
    if all_passed and env_exists:
        print("✅ PHASE 1 SETUP COMPLETE!")
        print("\n📋 Next steps:")
        print("  1. Add API keys to .env (if not done)")
        print("  2. Run: python scripts/test_all_apis.py")
        print("  3. Explore: notebooks/01_phase1_testing.ipynb")
        print("  4. Ready for Phase 2! 🎉")
    else:
        print("⚠️ SETUP INCOMPLETE")
        print("\nIssues found. Please:")
        print("  1. Run: python scripts/setup_project.py")
        print("  2. Check for error messages above")
        print("  3. Ensure all files were created")

    print("=" * 60)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
