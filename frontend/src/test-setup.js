import { afterEach, vi } from "vitest";
import { cleanup } from "@testing-library/react";

// jsdom doesn't implement scrolling; Layout scrolls to the top on navigation.
window.scrollTo = vi.fn();

afterEach(() => {
  cleanup();
  vi.clearAllMocks();
});
