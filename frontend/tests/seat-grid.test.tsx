import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { AppShell } from "../src/components/AppShell";

const seat = (index: number) => ({
  seatId: `seat-${index}`,
  displayName: `Seat ${index}`,
  providerLabel: "Local llama.cpp",
  modelLabel: `Model ${index}`,
  status: "idle" as const,
});

afterEach(cleanup);

describe("IntelAMP operating shell", () => {
  it("renders named shell regions and keyboard-reachable navigation", () => {
    render(<AppShell seats={[seat(1)]} />);

    expect(screen.getByRole("navigation", { name: "Workspace navigation" })).toBeInTheDocument();
    expect(screen.getByRole("banner", { name: "Run status" })).toBeInTheDocument();
    expect(screen.getByRole("main", { name: "Seat workspace" })).toBeInTheDocument();
    expect(screen.getByRole("form", { name: "Prompt composer" })).toBeInTheDocument();
    expect(screen.getByRole("complementary", { name: "Inspector" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Threads" })).toHaveAttribute("type", "button");
  });

  it("distinguishes one-seat and six-seat layouts without changing semantics", () => {
    const { rerender } = render(<AppShell seats={[seat(1)]} />);
    const one = screen.getByTestId("seat-grid");
    expect(one).toHaveAttribute("data-seat-count", "1");
    expect(one).toHaveAttribute("data-layout", "single");
    expect(within(one).getAllByRole("article")).toHaveLength(1);

    rerender(<AppShell seats={Array.from({ length: 6 }, (_, index) => seat(index + 1))} />);
    const six = screen.getByTestId("seat-grid");
    expect(six).toHaveAttribute("data-seat-count", "6");
    expect(six).toHaveAttribute("data-layout", "six");
    expect(within(six).getAllByRole("article")).toHaveLength(6);
  });

  it("provides a focused-seat selector for narrow-screen operation", () => {
    render(<AppShell seats={[seat(1), seat(2)]} />);
    const selector = screen.getByRole("combobox", { name: "Focused seat" });
    expect(selector).toBeInTheDocument();
    expect(within(selector).getAllByRole("option")).toHaveLength(2);
  });
});
