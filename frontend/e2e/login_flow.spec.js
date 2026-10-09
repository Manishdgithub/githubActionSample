import { test, expect } from '@playwright/test';

test.describe('E2E UI & Authentication Behavior', () => {
  test('should display login screen and accept inputs', async ({ page }) => {
    await page.goto('/');

    const title = page.locator('h1');
    await expect(title).toContainText('Production Operations Hub');

    const emailInput = page.getByTestId('email-input');
    const passwordInput = page.getByTestId('password-input');
    const submitBtn = page.getByTestId('login-submit');

    await emailInput.fill('admin@enterprise.com');
    await passwordInput.fill('SuperSecret123!');
    await expect(emailInput).toHaveValue('admin@enterprise.com');
    await expect(submitBtn).toBeVisible();
  });
});
