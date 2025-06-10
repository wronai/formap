# Contributing to Formap

Thank you for your interest in contributing to Formap! We welcome contributions from everyone, regardless of experience level.

## How to Contribute

1. **Fork the repository** and create your branch from `main`.
2. **Install the development dependencies**:
   ```bash
   poetry install
   ```
3. **Create a virtual environment** (if not using Poetry):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e .[dev]
   ```
4. **Make your changes** and ensure tests pass:
   ```bash
   pytest
   ```
5. **Format your code** before committing:
   ```bash
   black .
   isort .
   ```
6. **Commit your changes** with a descriptive commit message.
7. **Push** to your fork and open a pull request.

## Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide.
- Use type hints for all function signatures.
- Write docstrings for all public functions and classes.
- Keep lines under 100 characters.

## Testing

- Write tests for all new features and bug fixes.
- Run tests with `pytest`.
- Aim for at least 80% test coverage.

## Pull Request Process

1. Ensure any install or build dependencies are removed before the end of the layer when doing a build.
2. Update the README.md with details of changes to the interface, including new environment variables, exposed ports, useful file locations, and container parameters.
3. Increase the version number in `formap/__init__.py` and the README.md to the new version that this Pull Request would represent. The versioning scheme we use is [SemVer](http://semver.org/).
4. You may merge the Pull Request once you have the sign-off of two other developers, or if you do not have permission to do that, you may request the second reviewer to merge it for you.

## Reporting Bugs

Use the GitHub issue tracker to report bugs. Please include:

- A clear, descriptive title
- Steps to reproduce the issue
- Expected vs. actual behavior
- Any relevant error messages
- Your Python version and operating system

## Feature Requests

We welcome feature requests! Please open an issue to discuss your idea before implementing it.

## Code of Conduct

This project adheres to the Contributor Covenant [code of conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.
