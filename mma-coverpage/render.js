// Renders the cover page to PNG at 1x and 2x, as the mockup and as clean artwork.
const { chromium } = require('playwright');
const path = require('path');

const shots = [
  { scale: 1, suffix: '' },
  { scale: 2, suffix: '@2x' },
];

(async () => {
  const browser = await chromium.launch({ args: ['--no-sandbox', '--font-render-hinting=none'] });

  for (const { scale, suffix } of shots) {
    const page = await browser.newPage({
      viewport: { width: 1080, height: 1920 },
      deviceScaleFactor: scale,
    });
    await page.goto('file://' + path.resolve(__dirname, 'coverpage.html'));
    try { await page.evaluate(() => document.fonts.ready); } catch (e) {}
    await page.waitForTimeout(2500);

    await (await page.$('#page')).screenshot({
      path: path.resolve(__dirname, `APEX-MMA-coverpage${suffix}.png`),
    });
    await (await page.$('#poster')).screenshot({
      path: path.resolve(__dirname, `APEX-MMA-poster${suffix}.png`),
    });
    console.log(`rendered at ${scale}x`);
    await page.close();
  }

  await browser.close();
})();
