# Contributing to Autonomous Scientific Agent

Thank you for your interest in contributing! 🎉

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/yourusername/autonomous-scientific-agent/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Your environment (Python version, OS, etc.)
   - Error messages and logs

### Suggesting Features

1. Check existing [Issues](https://github.com/yourusername/autonomous-scientific-agent/issues) for similar suggestions
2. Create a new issue with:
   - Clear feature description
   - Use case and benefits
   - Possible implementation approach

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes
4. Run tests: `python tests/test_functional.py`
5. Update documentation if needed
6. Commit with clear messages: `git commit -m "Add feature: description"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Open a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/autonomous-scientific-agent.git
cd autonomous-scientific-agent

# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # Windows
source venv/bin/activate      # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Run tests
python tests/test_functional.py
```

## Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings to functions and classes
- Keep functions focused and modular
- Comment complex logic

## Testing

- Add tests for new features
- Ensure all tests pass before submitting PR
- Test coverage should not decrease

## Documentation

- Update README.md if adding features
- Update HOW_TO_USE.md for user-facing changes
- Add docstrings to new code
- Update PHASE4_README.md for technical changes

## Questions?

Open a [Discussion](https://github.com/yourusername/autonomous-scientific-agent/discussions) or reach out in Issues!

Thank you for contributing! 🙏
