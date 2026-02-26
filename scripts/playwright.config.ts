import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: '.',
  testMatch: 'walkthrough.ts',
  timeout: 120_000,
  expect: {
    timeout: 15_000,
  },
  use: {
    baseURL: 'http://localhost:5173',
    screenshot: 'on',
    video: 'on',
    launchOptions: {
      slowMo: 300,
    },
    viewport: { width: 1440, height: 900 },
    actionTimeout: 10_000,
  },
  reporter: [['list']],
});
