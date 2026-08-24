# Contributing to blender-mcp-ultra

Thank you for your interest in contributing! This document provides guidelines and information for contributors.

## Getting Started

### Prerequisites

- Python 3.10+
- Blender 4.0+ (or 5.2 LTS)
- Git

### Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/blender-mcp-ultra.git
   cd blender-mcp-ultra
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate  # Windows
   ```

4. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

5. Run tests:
   ```bash
   pytest tests/ -v
   ```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Follow the coding style (see below)
- Add tests for new functionality
- Update documentation if needed

### 3. Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run linting
ruff check src/
```

### 4. Commit Changes

```bash
git add .
git commit -m "feat: description of your changes"
```

Use conventional commits:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation
- `test:` for tests
- `refactor:` for code refactoring
- `perf:` for performance improvements

### 5. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Coding Style

### Python

- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Use f-strings for string formatting

### Comments

- Use docstrings for all public functions
- Keep comments concise and relevant
- Update comments when code changes

### Testing

- Write tests for all new functionality
- Aim for >80% code coverage
- Use descriptive test names

## Project Structure

```
blender-mcp-ultra/
├── src/
│   ├── core/           # Domain entities and interfaces
│   ├── adapters/       # Blender, LLM, Asset adapters
│   ├── infrastructure/ # Security, Network, Cache, Logging
│   ├── presentation/   # MCP Server, Addon, CLI
│   └── tools/          # 118 tools across 16 categories
├── skills/             # 19 skill definitions
├── tests/              # Unit and integration tests
└── docs/               # Documentation
```

## Adding New Tools

1. Create a new file in `src/tools/your_category/`
2. Define tool metadata in `TOOLS` list
3. Implement handler functions
4. Register handlers in `HANDLERS` dict
5. Add tests in `tests/unit/`
6. Update documentation

Example:

```python
# src/tools/your_category/__init__.py
from core.entities import Tool, ToolCategory, ToolPermission

TOOLS = [
    Tool(
        "your_category.tool_name",
        ToolCategory.YOUR_CATEGORY,
        "Description of the tool",
        ToolPermission.WRITE,
        {"param": {"type": "str", "required": True}},
    ),
]


def tool_handler(param: str) -> Dict:
    """Handler for the tool."""
    return {"success": True, "param": param}


HANDLERS = {
    "your_category.tool_name": tool_handler,
}
```

## Reporting Issues

- Use GitHub Issues
- Include steps to reproduce
- Include expected vs actual behavior
- Include Blender version and Python version

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
