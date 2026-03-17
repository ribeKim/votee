import { render, screen } from "@testing-library/react";
import { vi } from "vitest";

import { LoginPage } from "./LoginPage";

vi.mock("../hooks/useSession", () => ({
  useSession: () => ({ data: null })
}));

describe("LoginPage", () => {
  it("renders the Discord CTA", () => {
    render(<LoginPage />);
    expect(screen.getByRole("button", { name: "Discord로 시작하기" })).toBeInTheDocument();
  });
});

