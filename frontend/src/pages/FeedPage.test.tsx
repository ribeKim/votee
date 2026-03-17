import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { FeedPage } from "./FeedPage";
import { TestProviders } from "../test/render";

describe("FeedPage", () => {
  it("renders a voting match and submits a vote", async () => {
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            pair_view_id: "pair-1",
            left: { id: "a", title: "Alpha", image_url: "/alpha.png", owner_slug: "alpha-user" },
            right: { id: "b", title: "Beta", image_url: "/beta.png", owner_slug: "beta-user" }
          }),
          { status: 200, headers: { "Content-Type": "application/json" } }
        )
      )
      .mockResolvedValueOnce(
        new Response(JSON.stringify({ winner_rating: 1212, loser_rating: 1188 }), {
          status: 200,
          headers: { "Content-Type": "application/json" }
        })
      )
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            pair_view_id: "pair-2",
            left: { id: "c", title: "Gamma", image_url: "/gamma.png", owner_slug: "gamma-user" },
            right: { id: "d", title: "Delta", image_url: "/delta.png", owner_slug: "delta-user" }
          }),
          { status: 200, headers: { "Content-Type": "application/json" } }
        )
      );

    render(
      <TestProviders>
        <FeedPage />
      </TestProviders>
    );

    expect(await screen.findByText("Alpha")).toBeInTheDocument();
    await userEvent.click(screen.getAllByRole("button", { name: "이 아바타 선택" })[0]);

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/votes",
        expect.objectContaining({
          credentials: "include",
          method: "POST"
        })
      );
    });

    fetchMock.mockRestore();
  });
});

