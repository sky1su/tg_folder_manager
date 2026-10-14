# Contributing to Telegram Folder Manager

First off, thank you for considering contributing to this project! It's people like you that make the open-source community such a great place to learn, innovate, and collaborate.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Pull Requests](#pull-requests)
- [Development Workflow](#development-workflow)
  - [Setup](#setup)
  - [Coding Standards](#coding-standards)
  - [Testing](#testing)

## Code of Conduct

By participating in this project, you agree to abide by our community standards of behavior: be respectful, kind, and professional in all communications.

## How Can I Contribute?

### Reporting Bugs

If you find a bug, please report it using the [GitHub Issues](https://github.com/sky1su/tg_folder_manager/issues) page.

**Please include as much information as possible:**
- A clear and descriptive title.
- Steps to reproduce the behavior.
- **Expected** vs. **Actual** behavior.
- Environment details (OS, Python version, Telegram API version if applicable).
- Screenshots or logs (if helpful).

### Suggesting Enhancements

We love new ideas! If you want to improve the project, please open an [Issue](https://github.com/sky1su/tg_folder_manager/issues) with the tag `enhancement` and describe:
- The problem you want to solve.
- How the proposed solution would work.

### Pull Requests

1.  **Fork** the repository.
2.  **Create a branch** for your feature or bug fix: `feature/description-of-change` or `fix/description-of-fix`.
3.  **Commit** your changes with clear, concise messages.
4.  **Push** the branch to your fork.
5.  **Open a Pull Request** against the `main` branch.

---

## Development Workflow

### Setup

To start developing, clone the repository and set up a virtual environment:

```bash
# Clone the repository
git clone https://github.com/sky1su/tg_folder_manager.git
cd tg_folder_manager

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Coding Standards

This project follows a **Layered Modular Architecture**. When contributing, please adhere to the following rules:

- **Separation of Concerns (SoC)**: Business logic must stay in the `tg_folder_manager/` or `tg_summarise_chat/` modules.
- **Infrastructure Independence**: Business logic modules must **not** directly access the filesystem or the Telegram API via raw calls. They must use the services provided in the `core/` layer (Dependency Injection).
- **No Hardcoding**: All configuration must flow through the `core.config` (Pydantic) layer. Avoid using `os.getenv` or raw `yaml.load` inside business logic.

### Testing

We use `pytest` for testing. Before submitting a Pull Request, ensure that all existing tests pass and that you have added tests for your new code:

```bash
# Run tests
pytest
```

## License

By contributing, you agree that your contributions will be licensed under the project's [MIT License](LICENSE).
