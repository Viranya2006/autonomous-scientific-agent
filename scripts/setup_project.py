"""
Project Setup Script
====================
Automated setup for the Autonomous Scientific Agent project.

This script:
1. Checks Python version compatibility
2. Creates virtual environment
3. Installs dependencies
4. Creates necessary folders
5. Sets up .env file
6. Initializes logging

Run this script once to set up the complete development environment.
"""

import sys
import subprocess
import platform
from pathlib import Path
from typing import Tuple


def print_header(text: str) -> None:
    """Print formatted section header."""
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print('=' * 60)


def print_step(emoji: str, text: str) -> None:
    """Print step with emoji."""
    print(f"{emoji} {text}")


def check_python_version() -> Tuple[bool, str]:
    """
    Check if Python version is compatible (3.11.x).

    Returns:
        Tuple of (is_compatible, version_string)
    """
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    # Check for Python 3.11.x
    if version.major == 3 and version.minor == 11:
        return True, version_str

    return False, version_str


def create_venv(venv_path: Path) -> bool:
    """
    Create Python virtual environment.

    Args:
        venv_path: Path to virtual environment directory

    Returns:
        True if successful
    """
    try:
        print_step("🔨", "Creating virtual environment...")
        subprocess.run(
            [sys.executable, "-m", "venv", str(venv_path)],
            check=True,
            capture_output=True
        )
        print_step("✅", f"Virtual environment created: {venv_path}")
        return True
    except subprocess.CalledProcessError as e:
        print_step("❌", f"Failed to create virtual environment: {e}")
        return False


def get_pip_executable(venv_path: Path) -> str:
    """Get path to pip executable in virtual environment."""
    if platform.system() == "Windows":
        return str(venv_path / "Scripts" / "pip.exe")
    else:
        return str(venv_path / "bin" / "pip")


def install_dependencies(venv_path: Path, requirements_file: Path) -> bool:
    """
    Install Python packages from requirements.txt.

    Args:
        venv_path: Path to virtual environment
        requirements_file: Path to requirements.txt

    Returns:
        True if successful
    """
    pip_exe = get_pip_executable(venv_path)

    try:
        print_step(
            "📦", "Installing dependencies (this may take a few minutes)...")

        # Upgrade pip first
        subprocess.run(
            [pip_exe, "install", "--upgrade", "pip"],
            check=True,
            capture_output=True
        )

        # Install requirements
        result = subprocess.run(
            [pip_exe, "install", "-r", str(requirements_file)],
            check=True,
            capture_output=True,
            text=True
        )

        print_step("✅", "All packages installed successfully")
        return True

    except subprocess.CalledProcessError as e:
        print_step("❌", f"Failed to install dependencies: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False


def create_folder_structure(project_root: Path) -> None:
    """Create all necessary project folders."""
    print_step("📁", "Creating folder structure...")

    folders = [
        "data/papers",
        "data/results",
        "data/cache",
        "logs",
        "notebooks",
        "scripts",
        "tests",
        "src/config",
        "src/api",
        "src/utils",
        "src/core",
    ]

    for folder in folders:
        folder_path = project_root / folder
        folder_path.mkdir(parents=True, exist_ok=True)

    print_step("✅", "Folder structure created")


def setup_env_file(project_root: Path) -> None:
    """Create .env file from .env.example if it doesn't exist."""
    env_file = project_root / ".env"
    env_example = project_root / ".env.example"

    if env_file.exists():
        print_step("ℹ️", ".env file already exists (keeping existing)")
    elif env_example.exists():
        # Copy .env.example to .env
        with open(env_example, 'r') as src:
            content = src.read()
        with open(env_file, 'w') as dst:
            dst.write(content)
        print_step("✅", "Created .env file from template")
    else:
        print_step("⚠️", ".env.example not found - please create .env manually")


def print_next_steps() -> None:
    """Print instructions for what to do next."""
    print_header("📋 NEXT STEPS")

    system = platform.system()

    print("\n1️⃣  Activate virtual environment:")
    if system == "Windows":
        print("   venv\\Scripts\\Activate.ps1   (PowerShell)")
        print("   venv\\Scripts\\activate.bat   (Command Prompt)")
    else:
        print("   source venv/bin/activate")

    print("\n2️⃣  Get API keys (see API_SETUP_GUIDE.md):")
    print("   - Google Gemini      (5 minutes)")
    print("   - Hugging Face       (3 minutes)")
    print("   - Materials Project  (5 minutes)")

    print("\n3️⃣  Add your API keys to .env file")
    print("   Edit .env and replace placeholder values")

    print("\n4️⃣  Test all APIs:")
    print("   python scripts/test_all_apis.py")

    print("\n5️⃣  Ready for Phase 2! 🎉")
    print()


def main():
    """Main setup routine."""
    print_header("🚀 Autonomous Scientific Agent - Project Setup")

    # Get project root (where this script is located)
    project_root = Path(__file__).parent.parent

    # Check Python version
    print_step("🔍", "Checking Python version...")
    is_compatible, version = check_python_version()

    if is_compatible:
        print_step("✅", f"Python {version} detected (compatible)")
    else:
        print_step("⚠️", f"Python {version} detected (recommended: 3.11.x)")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Setup cancelled.")
            sys.exit(1)

    # Create virtual environment
    venv_path = project_root / "venv"
    if venv_path.exists():
        print_step("ℹ️", "Virtual environment already exists (skipping creation)")
    else:
        if not create_venv(venv_path):
            print("\n❌ Setup failed at virtual environment creation")
            sys.exit(1)

    # Install dependencies
    requirements_file = project_root / "requirements.txt"
    if not requirements_file.exists():
        print_step(
            "⚠️", "requirements.txt not found - skipping package installation")
    else:
        if not install_dependencies(venv_path, requirements_file):
            print("\n❌ Setup failed at dependency installation")
            sys.exit(1)

    # Create folder structure
    create_folder_structure(project_root)

    # Setup .env file
    setup_env_file(project_root)

    # Print success and next steps
    print_header("✅ Setup Complete!")
    print_next_steps()


if __name__ == "__main__":
    main()
