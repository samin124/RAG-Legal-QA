# Contributing Guidelines

Thank you for considering contributing to the Legal Document Q&A Assistant.

## Development Workflow

### Branch Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Production-ready, stable code |
| `feature/*` | New feature development |
| `fix/*` | Bug fixes |
| `docs/*` | Documentation updates |
| `refactor/*` | Code improvements |

### Commit Convention

This project follows [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>: <description>

[optional body]
```

**Types:**
- `feat` - New features
- `fix` - Bug fixes
- `docs` - Documentation changes
- `refactor` - Code refactoring
- `test` - Test additions or modifications
- `chore` - Maintenance tasks

**Examples:**
```bash
feat: Add PDF multi-document support
fix: Resolve retrieval timeout issue
docs: Update API configuration guide
```

## Getting Started

1. **Fork** the repository
2. **Clone** your fork locally
3. **Create** a feature branch
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Develop** and test your changes
5. **Commit** following the convention above
6. **Push** to your fork
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Open** a Pull Request

## Code Standards

- Follow PEP 8 style guidelines
- Add docstrings to functions and classes
- Include type hints where applicable
- Write unit tests for new functionality

## Pull Request Process

1. Ensure all tests pass
2. Update documentation if needed
3. Request review from maintainers
4. Address feedback promptly

## Questions?

Open an issue for any questions or discussions.
