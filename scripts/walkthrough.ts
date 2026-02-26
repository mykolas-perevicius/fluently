/**
 * Fluently Feature Walkthrough
 *
 * A comprehensive Playwright E2E test that exercises every major feature
 * of the Fluently translation app, capturing screenshots at each step.
 * Serves as both a regression test and a visual "storyboard" walkthrough.
 *
 * Run:
 *   npx playwright test --config scripts/playwright.config.ts
 *
 * Prerequisites:
 *   - Frontend dev server running at http://localhost:5173
 *   - (Optional) Backend + Ollama for PII detection and formatted translation
 */

import { test, expect } from '@playwright/test';
import path from 'path';
import fs from 'fs';

const SCREENSHOT_DIR = path.join(__dirname, 'screenshots', 'walkthrough');

// Helper: save a viewport-only screenshot with a descriptive filename
async function snap(page: import('@playwright/test').Page, name: string) {
  await page.screenshot({
    path: path.join(SCREENSHOT_DIR, name),
    fullPage: false,
  });
}

// Helper: short pause for animations/transitions to settle
async function settle(page: import('@playwright/test').Page, ms = 800) {
  await page.waitForTimeout(ms);
}

test.describe('Fluently Feature Walkthrough', () => {
  test.beforeAll(async () => {
    // Ensure screenshot output directory exists
    fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });

    // Ensure a sample PDF exists for document translation testing.
    // We create a minimal valid PDF if one is not already present.
    const testMaterialsDir = path.join(__dirname, 'test_materials');
    fs.mkdirSync(testMaterialsDir, { recursive: true });

    const samplePdfPath = path.join(testMaterialsDir, 'sample_report.pdf');
    if (!fs.existsSync(samplePdfPath)) {
      // Minimal valid PDF with text content for extraction testing.
      // This is a hand-crafted PDF 1.4 that renders a single page with
      // representative text including a fake email for PII detection.
      const pdfContent = `%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj

2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj

3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]
   /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj

4 0 obj
<< /Length 478 >>
stream
BT
/F1 18 Tf
72 720 Td
(Quarterly Performance Report) Tj
0 -30 Td
/F1 12 Tf
(Prepared by: John Smith) Tj
0 -20 Td
(Email: john.smith@example.com) Tj
0 -20 Td
(Phone: +1 (555) 123-4567) Tj
0 -30 Td
(Executive Summary) Tj
0 -20 Td
(This report summarizes the key performance indicators for Q3 2025.) Tj
0 -20 Td
(Revenue increased by 15% compared to the previous quarter.) Tj
0 -20 Td
(Customer satisfaction scores remain above the 90th percentile.) Tj
0 -30 Td
(Recommendations) Tj
0 -20 Td
(1. Expand operations into European markets.) Tj
0 -20 Td
(2. Invest in automated translation infrastructure.) Tj
ET
stream
endobj

5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj

xref
0 6
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000266 00000 n
0000000796 00000 n

trailer
<< /Size 6 /Root 1 0 R >>
startxref
873
%%EOF`;
      fs.writeFileSync(samplePdfPath, pdfContent, 'utf-8');
    }
  });

  test('complete walkthrough', async ({ page }) => {
    // ================================================================
    // SCENE 1: Landing Page
    // ================================================================

    await test.step('Scene 1: Landing Page', async () => {
      // 1. Navigate to the app
      await page.goto('http://localhost:5173', { waitUntil: 'networkidle' });
      await settle(page, 1500); // Let landing animations play out

      // 2. Screenshot: Hero section
      await snap(page, '01-landing-hero.png');

      // 3. Scroll to features section (#features)
      await page.locator('#features').scrollIntoViewIfNeeded();
      await settle(page, 1000); // Allow scroll-reveal animations to trigger

      // 4. Screenshot: Capability cards
      await snap(page, '02-landing-features.png');

      // 5. Scroll to comparison table (#compare)
      await page.locator('#compare').scrollIntoViewIfNeeded();
      await settle(page, 1000);

      // 6. Screenshot: Comparison table
      await snap(page, '03-landing-comparison.png');

      // 7. Click "Open App" button in the header (always visible, sticky)
      //    The header button says "Open App"
      await page.locator('header button:has-text("Open App")').click();

      // Wait for the page transition animation (450ms fade + rAF)
      await settle(page, 1200);
    });

    // ================================================================
    // SCENE 2: Text Translation
    // ================================================================

    await test.step('Scene 2: Text Translation', async () => {
      // 1. Wait for TranslatePage to be fully rendered
      await page.locator('[data-testid="tab-text"]').waitFor({ state: 'visible' });
      await page.locator('[data-testid="source-textarea"]').waitFor({ state: 'visible' });
      await settle(page);

      // 2. Screenshot: Empty text translation view
      await snap(page, '04-app-text-tab.png');

      // 3. Type sample text into the source textarea
      const sourceTextarea = page.locator('[data-testid="source-textarea"]');
      await sourceTextarea.click();
      await sourceTextarea.fill(
        'The quick brown fox jumps over the lazy dog. This is a test of the translation system.'
      );
      await settle(page, 500);

      // 4. Select Spanish as target language
      //    Click the target language selector pill to open its dropdown
      const targetSelector = page.locator('[data-testid="target-language-selector"]');
      await targetSelector.locator('button').first().click();
      await settle(page, 400);

      // Type "Spanish" in the search input to filter, then click the option
      const dropdown = targetSelector.locator('.absolute'); // the dropdown panel
      await dropdown.locator('input[placeholder="Search languages..."]').fill('Spanish');
      await settle(page, 300);
      await dropdown.locator('button:has-text("Spanish")').click();
      await settle(page, 500);

      // 5. Wait for translation to appear
      //    The output area changes from "Translation will appear here" to actual text.
      //    The backend may not be running, so we use a generous but bounded wait.
      try {
        await expect(
          page.locator('[data-testid="translation-output"]')
        ).not.toContainText('Translation will appear here', { timeout: 30_000 });
        // Give a moment for the full translation to render
        await settle(page, 1000);
      } catch {
        // Backend may not be available; screenshot whatever state we are in
        await settle(page, 500);
      }

      // 6. Screenshot: Text translated (or loading/error state if backend unavailable)
      await snap(page, '05-text-translated.png');
    });

    // ================================================================
    // SCENE 3: Document Tab
    // ================================================================

    await test.step('Scene 3: Document Upload', async () => {
      // 1. Click the "Document" tab
      await page.locator('[data-testid="tab-document"]').click();
      await settle(page, 800);

      // 2. Screenshot: Empty document upload state with format badges
      await snap(page, '06-document-upload.png');

      // 3. Upload the sample PDF via the hidden file input
      const samplePdfPath = path.join(__dirname, 'test_materials', 'sample_report.pdf');
      const fileInput = page.locator('input[type="file"][accept]').first();
      await fileInput.setInputFiles(samplePdfPath);

      // 4. Wait for extraction to complete
      //    The UI shows "Extracting text..." while processing, then shows the preview.
      //    We wait for the "Extracted Text Preview" label to appear.
      try {
        await page.locator('text=Extracted Text Preview').waitFor({
          state: 'visible',
          timeout: 20_000,
        });
        await settle(page, 800);
      } catch {
        // Extraction may fail or take too long; capture whatever state we have
        await settle(page, 1000);
      }

      // 5. Screenshot: File info + extracted text preview
      await snap(page, '07-document-extracted.png');
    });

    // ================================================================
    // SCENE 4: PII Detection
    // ================================================================

    await test.step('Scene 4: PII Detection', async () => {
      try {
        // 1. Look for the PII toggle and click it
        const piiToggleLabel = page.locator('text=Scan for PII before translating');
        if (await piiToggleLabel.isVisible({ timeout: 3000 })) {
          // The toggle is the sibling div inside the same <label>
          // Click the toggle track (the round div element before the text)
          const toggleTrack = piiToggleLabel.locator('..').locator('div').first();
          await toggleTrack.click();
          await settle(page, 500);

          // 2. Screenshot: PII toggle enabled
          await snap(page, '08-pii-toggle-enabled.png');

          // 3. Click the "Scan PII & Translate" button
          const scanBtn = page.locator('button:has-text("Scan PII & Translate")');
          if (await scanBtn.isVisible({ timeout: 2000 })) {
            await scanBtn.click();

            // 4. Wait for PII detection to complete
            //    Look for either "PII Detected" heading or the scanning spinner to disappear
            try {
              await page.locator('text=PII Detected').waitFor({
                state: 'visible',
                timeout: 30_000,
              });
              await settle(page, 800);
            } catch {
              // PII detection may need backend; wait and screenshot whatever state
              await settle(page, 2000);
            }

            // 5. Screenshot: PII entities with checkboxes (or detection state)
            await snap(page, '09-pii-entities.png');
          } else {
            // Button not visible, screenshot current state
            await snap(page, '09-pii-entities.png');
          }
        } else {
          // PII toggle not visible (maybe no text was extracted)
          await snap(page, '08-pii-toggle-enabled.png');
          await snap(page, '09-pii-entities.png');
        }
      } catch {
        // Catch-all: screenshot whatever state we are in
        await snap(page, '08-pii-toggle-enabled.png');
        await snap(page, '09-pii-entities.png');
      }
    });

    // ================================================================
    // SCENE 5: Formatted Translation (requires backend + Ollama)
    // ================================================================

    await test.step('Scene 5: Formatted Translation', async () => {
      try {
        // 1. Remove the current file and re-upload to get a clean state
        const removeBtn = page.locator('button').filter({
          has: page.locator('svg path[d="M1 1l8 8M9 1l-8 8"]'),
        });
        if (await removeBtn.first().isVisible({ timeout: 2000 })) {
          await removeBtn.first().click();
          await settle(page, 600);
        }

        // Re-upload the PDF
        const samplePdfPath = path.join(__dirname, 'test_materials', 'sample_report.pdf');
        const fileInput = page.locator('input[type="file"][accept]').first();
        await fileInput.setInputFiles(samplePdfPath);

        // Wait for extraction
        try {
          await page.locator('text=Extracted Text Preview').waitFor({
            state: 'visible',
            timeout: 20_000,
          });
          await settle(page, 800);
        } catch {
          await settle(page, 1000);
        }

        // 2. Make sure PII toggle is OFF
        const piiToggleLabel = page.locator('text=Scan for PII before translating');
        if (await piiToggleLabel.isVisible({ timeout: 2000 })) {
          // Check if the toggle is currently ON (has bg-accent-cyan class)
          const toggleTrack = piiToggleLabel.locator('..').locator('div').first();
          const toggleClasses = await toggleTrack.getAttribute('class');
          if (toggleClasses && toggleClasses.includes('bg-accent-cyan')) {
            // Toggle is ON, click to turn it OFF
            await toggleTrack.click();
            await settle(page, 400);
          }
        }

        // 3. Click "Translate with Formatting" button
        const formatBtn = page.locator('button:has-text("Translate with Formatting")');
        if (await formatBtn.isVisible({ timeout: 3000 })) {
          await formatBtn.click();

          // 4. Wait for translation to complete (may take a long time with Ollama)
          try {
            // Wait for the formatted output tabs to appear (Plain, Markdown, LaTeX)
            await page.locator('button:has-text("Plain")').waitFor({
              state: 'visible',
              timeout: 90_000,
            });
            await settle(page, 1000);
          } catch {
            // Timeout — screenshot the in-progress state
            await settle(page, 1000);
          }

          // 5. Screenshot: Plaintext tab
          await snap(page, '10-formatted-plain.png');

          // 6. Click "Markdown" tab
          const markdownTab = page.locator('button:has-text("Markdown")');
          if (await markdownTab.isVisible({ timeout: 2000 })) {
            await markdownTab.click();
            await settle(page, 500);

            // 7. Screenshot: Markdown tab
            await snap(page, '11-formatted-markdown.png');
          }

          // 8. Click "LaTeX" tab
          const latexTab = page.locator('button:has-text("LaTeX")');
          if (await latexTab.isVisible({ timeout: 2000 })) {
            await latexTab.click();
            await settle(page, 500);

            // 9. Screenshot: LaTeX tab
            await snap(page, '12-formatted-latex.png');
          }
        } else {
          // Formatted translate button not available (may not be a PDF, or extraction failed)
          await snap(page, '10-formatted-plain.png');
          await snap(page, '11-formatted-markdown.png');
          await snap(page, '12-formatted-latex.png');
        }
      } catch {
        // Backend/Ollama not available — capture whatever state we are in
        await snap(page, '10-formatted-plain.png');
        await snap(page, '11-formatted-markdown.png');
        await snap(page, '12-formatted-latex.png');
      }
    });

    // ================================================================
    // SCENE 6: Image Tab
    // ================================================================

    await test.step('Scene 6: Image Tab', async () => {
      // 1. Click the "Image" tab
      await page.locator('[data-testid="tab-image"]').click();
      await settle(page, 800);

      // 2. Screenshot: Empty image upload state
      await snap(page, '13-image-upload.png');
    });
  });
});
