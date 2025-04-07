/**
 * A simple React component example.
 *
 * This component is intentionally basic to serve as a clear target for
 * demonstrating Test-Driven Development (TDD) using Vitest and
 * React Testing Library in this Node.js project template.
 * See Greeting.test.tsx for the corresponding tests.
 */
import React from "react";

type GreetingProps = {
  name: string;
};

const Greeting: React.FC<GreetingProps> = ({ name }) => {
  return <h1>Hello, {name}!</h1>;
};

export default Greeting;
