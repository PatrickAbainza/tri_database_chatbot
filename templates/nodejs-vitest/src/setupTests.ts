/**
 * Vitest Setup File
 *
 * This file is executed before each test file runs, as configured by the
 * `setupFiles` option in `vitest.config.ts`.
 *
 * It's used for global test setup tasks.
 */

// Import Jest DOM matchers from React Testing Library.
// This extends Vitest's `expect` function with useful DOM-specific assertions
// like `.toBeInTheDocument()`, `.toHaveAttribute()`, etc.
// These matchers make writing tests for DOM structure and attributes easier.
import "@testing-library/jest-dom";

// --- Optional Global Setup ---
// You can add other global configurations or mocks here if needed for your tests.
// Example: Mocking global objects like `fetch` or setting up a mock server (like MSW).
// import { server } from './__mocks__/server'; // Example MSW setup
// beforeAll(() => server.listen());
// afterEach(() => server.resetHandlers());
// afterAll(() => server.close());
