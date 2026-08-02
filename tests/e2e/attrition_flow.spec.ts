import { test, expect } from '@playwright/test';

test.describe('AttritionIQ E2E User Journey', () => {
  test('landing page renders correctly', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/AttritionIQ/);
    await expect(page.getByText('Predict Attrition')).toBeVisible();
    await expect(page.getByRole('link', { name: 'Sign In' })).toBeVisible();
  });

  test('user can log in with demo credentials and view dashboard', async ({ page }) => {
    await page.goto('/login');

    // Fill login form
    await page.fill('input[placeholder="john.doe@company.com"]', 'admin@attritioniq.com');
    await page.fill('input[placeholder="••••••••"]', 'Admin@123');
    await page.click('button:has-text("Sign In")');

    // Should navigate to dashboard
    await expect(page).toHaveURL('/dashboard');
    await expect(page.getByText('Dashboard')).toBeVisible();
    await expect(page.getByText('Workforce analytics overview')).toBeVisible();
  });

  test('user can navigate to prediction page and run a prediction', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[placeholder="john.doe@company.com"]', 'admin@attritioniq.com');
    await page.fill('input[placeholder="••••••••"]', 'Admin@123');
    await page.click('button:has-text("Sign In")');

    // Navigate to prediction
    await page.click('a[href="/predictions"]');
    await expect(page).toHaveURL('/predictions');

    // Click Predict
    await page.click('button:has-text("Predict Attrition Risk")');

    // Verify result card appears
    await expect(page.getByText('Attrition Probability')).toBeVisible({ timeout: 10000 });
  });

  test('user can view employees table', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[placeholder="john.doe@company.com"]', 'admin@attritioniq.com');
    await page.fill('input[placeholder="••••••••"]', 'Admin@123');
    await page.click('button:has-text("Sign In")');

    await page.click('a[href="/employees"]');
    await expect(page).toHaveURL('/employees');
    await expect(page.getByText('Employees')).toBeVisible();
  });
});
