import { expect, test } from "@playwright/test";

test("login screen renders the Discord CTA", async ({ page }) => {
  await page.goto("/login");
  await expect(page.getByRole("button", { name: "Discord로 시작하기" })).toBeVisible();
});
