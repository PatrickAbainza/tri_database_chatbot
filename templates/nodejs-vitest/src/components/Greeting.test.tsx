/**
 * Tests for the Greeting component using Vitest and React Testing Library (RTL).
 */

// Import testing utilities from React Testing Library
// - render: Renders a React component into a virtual DOM.
// - screen: Provides methods to query the virtual DOM (e.g., getByRole, findByText).
import { render, screen } from "@testing-library/react";

// Import test structure functions (describe, it) and assertion functions (expect) from Vitest.
// These are often globally available due to `globals: true` in vitest.config.ts, but explicit imports are also fine.
import { describe, expect, it } from "vitest";

// Import the component being tested.
import Greeting from "./Greeting";

// 'describe' groups related tests together for better organization.
describe("Greeting Component", () => {
  // 'it' defines an individual test case. Alias: 'test'.
  it("should render the greeting with the provided name", () => {
    // 1. Arrange: Render the component with specific props.
    render(<Greeting name="World" />);

    // 2. Act/Assert: Query the DOM and make assertions.
    // - screen.getByRole: Finds an element by its accessible role and name.
    //   (Uses accessibility tree, preferred querying method).
    // - expect(...): Vitest's assertion function.
    // - .toBeInTheDocument(): A matcher from '@testing-library/jest-dom'
    //   (imported via setupTests.ts) checking if the element exists in the DOM.
    expect(
      screen.getByRole("heading", { name: /Hello, World!/i })
    ).toBeInTheDocument();
  });
});
