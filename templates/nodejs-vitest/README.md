# React + TypeScript + Vite + Vitest Template

This template provides a minimal setup to get React working in Vite with HMR, ESLint, TypeScript, and Vitest for unit/integration testing using React Testing Library, focusing on a Test-Driven Development (TDD) approach.

## Getting Started

1.  **Install Dependencies:**

    ```bash
    npm install
    ```

2.  **Run Development Server:**

    ```bash
    npm run dev
    ```

    This starts the Vite development server with Hot Module Replacement (HMR). Open your browser to the URL provided (usually `http://localhost:5173`).

## Running Tests

You can run the tests in several ways:

- **VS Code Task:** Use the built-in VS Code task runner. Open the Command Palette (Ctrl+Shift+P or Cmd+Shift+P) and select "Tasks: Run Task", then choose "Run Node Tests". This will execute the tests in watch mode within the integrated terminal.
- **Command Line (Watch Mode):**
  ```bash
  npm test
  # or
  npx vitest
  ```
  This runs the test suite using Vitest in watch mode. Press `q` to quit.
- **Command Line (Single Run):**
  ```bash
  npm run test:run
  # or
  npx vitest run
  ```
  This runs the tests once and exits.

## Running Tests with Coverage

The `npm test` script is configured to run tests with coverage enabled using `@vitest/coverage-v8`. Coverage reports (including HTML, LCOV, JSON, and text summaries) are generated in the `./coverage` directory.

Coverage options, including reporters and potential thresholds, are configured within the `test.coverage` section of `vitest.config.ts`.

## TDD Setup Explained

- **`vitest.config.ts`**: Configures Vitest, merging with `vite.config.ts`. Sets up the testing environment (`jsdom`), global setup files, and coverage options.
- **`src/setupTests.ts`**: (If present, or configure via `globals` in `vitest.config.ts`) Run before tests start. Used to import testing utilities like `@testing-library/jest-dom` for helpful DOM matchers.
- **`src/__mocks__`**: This directory is intended for manual mocks, particularly useful for mocking modules or APIs that are external dependencies.
- **`src/main.test.tsx`**: An example test file demonstrating basic testing setup with Vitest and React Testing Library. It serves as a starting point for your application's tests.
- **React Testing Library**: Used for rendering components in a realistic way and querying the DOM as a user would.

## Recommended VS Code Extensions

The `.vscode/extensions.json` file recommends extensions to enhance the development experience:

- **`vitest.explorer` (Vitest Explorer):** Provides a UI within VS Code to view, run, and debug your Vitest tests.
- **`dbaeumer.vscode-eslint` (ESLint):** Integrates ESLint into VS Code for real-time linting.
- **`esbenp.prettier-vscode` (Prettier - Code formatter):** Automatically formats your code according to Prettier rules.

## Basic TDD Workflow Example (React Component)

1.  **Write a Failing Test:** Create a test file (e.g., `MyComponent.test.tsx`) for a new component. Write a test case describing the desired behavior (e.g., rendering specific text based on props). Run the tests; it should fail because the component doesn't exist or doesn't meet the criteria.

    ```typescript jsx
    // src/components/MyComponent.test.tsx
    import { render, screen } from "@testing-library/react";
    import { describe, it, expect } from "vitest";
    // import MyComponent from './MyComponent'; // Component doesn't exist yet

    describe("MyComponent", () => {
      it("should display the correct message", () => {
        // render(<MyComponent message="Test Message" />); // This would fail initially
        // expect(screen.getByText(/Test Message/i)).toBeInTheDocument();
        expect(true).toBe(false); // Placeholder failing test
      });
    });
    ```

2.  **Write Minimal Code to Pass:** Create the component file (e.g., `MyComponent.tsx`). Write the simplest code possible to make the failing test pass.

    ```typescript jsx
    // src/components/MyComponent.tsx
    import React from "react";

    type MyComponentProps = {
      message: string;
    };

    const MyComponent: React.FC<MyComponentProps> = ({ message }) => {
      return <div>{message}</div>;
    };

    export default MyComponent;
    ```

    Update the test to use the actual component and assertion. Run tests; they should now pass.

3.  **Refactor (Optional):** Improve the component's code or the test's clarity while ensuring all tests still pass.

Repeat this cycle for new features or behaviors.

## Debugging

This template includes VS Code launch configurations (`.vscode/launch.json`) for debugging your Vitest tests:

- **Node: Vitest All:** Runs `npm test` in debug mode, allowing you to debug the entire test suite.
- **Node: Vitest Current File:** Runs `npm test -- <current_file>` in debug mode, focusing the debugger on the currently open test file.

Set breakpoints in your test files or source code and use these configurations via the VS Code Run and Debug panel (usually accessible via the play button with a bug icon in the sidebar).

## Docker Support

This template includes a `Dockerfile` and a `.dockerignore` file to facilitate containerizing the application.

- **`Dockerfile`:** Defines the steps to build a Docker image for the project using a Node.js base image. It installs dependencies using `npm ci`, copies the application code, exposes the Vite development port (5173), and sets the default command to start the development server.
- **`.dockerignore`:** Lists files and directories (like `node_modules`, `dist`, `.env`) that should be excluded from the Docker build context to optimize image size and build speed.

To build the Docker image:

```bash
docker build -t nodejs-vitest-app .
```

To run the container and map the port:

```bash
docker run -it --rm -p 5173:5173 nodejs-vitest-app
```

## Security Scanning

Dependency security scanning is integrated using `npm audit`:

- **CI Integration:** The GitHub Actions workflow (`.github/workflows/nodejs-ci.yml`) includes a step to run `npm audit --audit-level=high` after installing dependencies. This checks for high-severity vulnerabilities during the CI process.
- **Pre-commit Hook:** The `lint-staged` configuration in `package.json` is set up to run `npm audit --audit-level=high` whenever `package.json` or `package-lock.json` files are staged for commit. This provides an early check for vulnerabilities before code is committed, though it might slightly increase commit times.

## Static Code Analysis

This template incorporates several tools for static code analysis to enhance code quality and maintainability:

- **ESLint:** Used for identifying and reporting on patterns found in ECMAScript/JavaScript code. It's configured with:
  - Standard recommended rules (`@eslint/js`, `typescript-eslint`).
  - React-specific rules (`eslint-plugin-react-hooks`, `eslint-plugin-react-refresh`).
  - **Complexity Check:** The `eslint-plugin-complexity` is added to warn if a function's cyclomatic complexity exceeds a defined threshold (currently 10 in `eslint.config.js`).
- **JSCPD:** Detects copy/paste duplicated code in your source files. Helps identify areas that could be refactored into reusable components or functions.
- **Dependency Cruiser:** Analyzes and visualizes module dependencies. Helps understand the structure of the codebase, identify circular dependencies, and enforce architectural rules.

### VS Code Tasks for Analysis

Corresponding VS Code tasks (`.vscode/tasks.json`) are available:

- **`Run ESLint`:** Executes `npm run lint` (which should run `eslint .`) to check for linting errors and complexity warnings.
- **`Run JSCPD Duplication Check`:** Executes `npx jscpd src/ --min-lines 5 --threshold 0` to find duplicated code blocks.
- **`Run Dependency Cruiser Graph (JSON)`:** Executes `npx depcruise --include-only "^src" --output-type archi src > analysis_results/dependency-graph.json` to generate a dependency graph in JSON format (suitable for analysis or visualization tools) in the `analysis_results` directory.
- **`Run All Node Analyses`:** A convenience task that runs ESLint, JSCPD, and Dependency Cruiser.

To run these tasks, open the Command Palette (Cmd+Shift+P or Ctrl+Shift+P), type "Tasks: Run Task", and select the desired analysis task.

## Logging

For frontend components like the examples in this template, standard browser console methods are typically sufficient for debugging during development:

- `console.log()`: General output.
- `console.warn()`: Warnings.
- `console.error()`: Errors.

If you were to extend this project with a Node.js backend, consider using a dedicated structured logging library like `winston` or `pino`. These libraries offer features like log levels, different output formats (e.g., JSON), and transports (e.g., writing to files or external services), which are crucial for managing logs effectively in production environments.
