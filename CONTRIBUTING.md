# Contributing to TDD Project Templates

## Introduction

Thank you for considering contributing! The goal of this repository is to maintain high-quality, robust project templates that strongly emphasize Test-Driven Development (TDD). Your contributions help ensure these templates remain useful and adhere to best practices.

## Getting Started

Before contributing, please familiarize yourself with the project structure and the specific template you wish to modify. Refer to the main [README.md](README.md) and the README file within the relevant template directory:

- [Python Template README](templates/python-uv/README.md)
- [Node.js Template README](templates/nodejs-vitest/README.md)

## Development Workflow

### Test-Driven Development (TDD)

**TDD is mandatory for all code changes within the templates.** This includes new features, bug fixes, and refactoring.

1.  **Red:** Write a failing test that clearly defines the desired behavior or exposes the bug.
2.  **Green:** Write the simplest possible code to make the test pass.
3.  **Refactor:** Improve the code structure and clarity while ensuring all tests still pass.

New code contributions _must_ include corresponding tests. Pull requests without adequate tests or that break existing tests will not be merged.

### Dependencies

Manage dependencies carefully within each template's directory:

- **Python (`templates/python-uv/`):**
  - Use `uv add <package>` for runtime dependencies.
  - Use `uv add --dev <package>` for development/testing dependencies.
  - Commit the updated `pyproject.toml` and `uv.lock` files.
- **Node.js (`templates/nodejs-vitest/`):**
  - Use `npm install --save-dev <package>` for development/testing dependencies.
  - Use `npm install <package>` for runtime dependencies.
  - Commit the updated `package.json` and `package-lock.json` files.

### Running Tests

Ensure all tests pass before submitting changes. Refer to the template-specific READMEs or VS Code task configurations for detailed instructions on how to run the test suites.

- **Python:** Typically `uv run pytest` within `templates/python-uv/`.
- **Node.js:** Typically `npm test` or `npm run test:ui` within `templates/nodejs-vitest/`.

## Code Style & Quality

Code style and quality are enforced automatically using pre-commit hooks.

- **Python:** Uses `ruff` for linting and formatting.
- **Node.js:** Uses `eslint` for linting and `prettier` for formatting.

**Before committing:**

1.  **Install Hooks:**
    - Run `uv run pre-commit install` in the project root directory.
    - Run `npx husky install` within the `templates/nodejs-vitest/` directory.
2.  **Run Hooks:** The hooks will run automatically when you attempt to commit changes (`git commit`). Fix any reported issues before finalizing your commit.

## Submitting Changes

(Optional: Add specific guidelines for pull requests here, e.g., branching strategy, PR titles, descriptions, linking issues.)

1.  Fork the repository.
2.  Create a new branch for your changes (e.g., `git checkout -b feature/my-new-feature` or `fix/address-bug-xyz`).
3.  Make your changes, following the TDD workflow and ensuring all tests pass and pre-commit hooks succeed.
4.  Push your branch to your fork.
5.  Open a pull request against the main repository branch.
6.  Provide a clear description of your changes in the pull request.
