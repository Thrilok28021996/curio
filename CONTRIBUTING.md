# Contributing to Curio

Thanks for your interest in contributing!

## How to contribute

1. Fork the repo
2. Create a feature branch
3. Make your changes
4. Run tests: `python tests/test_core.py && python tests/test_validation.py`
5. Submit a pull request

## Ideas for contributions

- New gap detection strategies
- Better lesson extraction
- New source types (APIs, databases, files)
- MCP server improvements
- Documentation improvements
- Bug fixes

## Development setup

```bash
git clone https://github.com/Thrilok28021996/curio.git
cd curio
pip install -e ".[dev]"
python tests/test_core.py
```

## Code style

- Keep it simple
- Add tests for new features
- Update docs if needed
- One commit per logical change
