import { test, expect } from '@playwright/test';

test.describe('LibreChat Browser Smoke', () => {
  test('user can log in and view utility charges', async ({ page }) => {
    const userEmail = process.env.TEST_USER_EMAIL ?? 'pavel@test.local';
    const userPassword = process.env.TEST_USER_PASSWORD ?? '12345678';

    // 1. Navigate to login
    await page.goto('/login');
    await page.waitForSelector('#email');

    // 2. Perform authentication
    await page.fill('#email', userEmail);
    await page.fill('#password', userPassword);
    await page.click('button[type="submit"]');

    // 3. Wait for chat view
    await page.waitForURL('**/c/**');

    // 4. Send inquiry message
    const textarea = page.locator('#prompt-textarea, textarea').first();
    await expect(textarea).toBeVisible();
    await textarea.fill('Начисления 10001 за 2026-08');
    await page.keyboard.press('Enter');

    // 5. Assert agent response in chat bubble
    const replyLocator = page.locator('text=150000').first();
    await expect(replyLocator).toBeVisible({ timeout: 15000 });

    const accountLocator = page.locator('text=10001').first();
    await expect(accountLocator).toBeVisible();
  });
});
