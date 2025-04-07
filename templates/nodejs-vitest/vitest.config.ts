/// <reference types="vitest" />
/// <reference types="vite/client" />

import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  // Vitest configuration block: https://vitest.dev/config/
  test: {
    // Enables global APIs (describe, it, expect, etc.) like Jest.
    // This avoids needing to import them in every test file.
    globals: true,
    // Sets the testing environment to simulate a browser DOM using jsdom.
    // Required for testing React components that interact with the DOM.
    environment: "jsdom",
    // Specifies setup files to run before each test file.
    // Used here to import Jest DOM matchers from '@testing-library/jest-dom'.
    setupFiles: "./src/setupTests.ts",
    // Enables processing of CSS files imported within components.
    // Set to true if your components import CSS modules or global styles.
    css: true,
    // Configures test reporters. 'default' provides console output.
    // 'json' outputs results to a JSON file (vitest-results.json), useful for CI/CD integration.
    reporters: ["default", "json"],
    // Coverage configuration: https://vitest.dev/guide/coverage.html
    coverage: {
      provider: "v8", // Use V8's built-in coverage
      reporter: ["text", "json", "html", "lcov"], // Generate multiple report formats
      reportsDirectory: "./coverage", // Output directory for coverage reports
      // Optional: Add thresholds to enforce minimum coverage
      // thresholds: {
      //   lines: 80,
      //   functions: 80,
      //   branches: 80,
      //   statements: 80
      // }
    },
  },
});
