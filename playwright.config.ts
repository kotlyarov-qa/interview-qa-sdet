import { defineConfig } from '@playwright/test';
export default defineConfig({ testDir: './e2e', use: { baseURL: process.env.UI_URL ?? 'http://localhost:3082', trace: 'retain-on-failure' } });
