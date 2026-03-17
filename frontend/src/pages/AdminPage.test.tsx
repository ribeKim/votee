import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

import { AdminPage } from "./AdminPage";
import { TestProviders } from "../test/render";

vi.mock("../hooks/useSession", () => ({
  useSession: () => ({
    isLoading: false,
    data: {
      user: {
        id: "admin-1",
        display_name: "Admin",
        username: "admin",
        slug: "admin",
        avatar_url: null,
        bio: null,
        is_admin: true
      },
      avatars: []
    }
  })
}));

describe("AdminPage", () => {
  it("renders reports and sends a hide request", async () => {
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify([
            {
              id: "report-1",
              avatar_id: "avatar-1",
              avatar_title: "Flagged Avatar",
              reporter_slug: "reporter",
              reason: "부적절함",
              status: "open",
              created_at: "2026-03-17T00:00:00Z"
            }
          ]),
          { status: 200, headers: { "Content-Type": "application/json" } }
        )
      )
      .mockResolvedValueOnce(new Response(null, { status: 204 }))
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify([]),
          { status: 200, headers: { "Content-Type": "application/json" } }
        )
      );

    render(
      <TestProviders>
        <AdminPage />
      </TestProviders>
    );

    expect(await screen.findByText("Flagged Avatar")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "숨김" }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "/api/admin/avatars/avatar-1/hide",
        expect.objectContaining({
          credentials: "include",
          method: "POST"
        })
      );
    });

    fetchMock.mockRestore();
  });
});
