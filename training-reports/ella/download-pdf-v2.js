const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const stateFile = '/Users/bangcle/.openclaw/workspace/training-reports/ella/oa-working-state.json';
  const outputDir = '/Users/bangcle/.openclaw/agents/ella/workspace/training-reports';
  
  if (!fs.existsSync(stateFile)) {
    console.error('State file not found:', stateFile);
    process.exit(1);
  }

  const browser = await chromium.launch({
    headless: false,
    slowMo: 300,
  });

  const context = await browser.newContext({
    storageState: stateFile,
    acceptDownloads: true,
    viewport: { width: 1440, height: 900 },
  });

  // Intercept network to catch download requests
  const downloadResponses = [];
  context.on('requestfinished', async (request) => {
    const url = request.url();
    if (url.includes('FileDownload') || url.includes('download') || url.includes('fileid')) {
      console.log('[Network] Download URL:', url);
      try {
        const response = request.response();
        if (response) {
          const ct = response.headers()['content-type'] || '';
          console.log('[Network] Content-Type:', ct, 'Status:', response.status());
          if (ct.includes('pdf') || ct.includes('octet-stream') || ct.includes('application')) {
            try {
              const body = await response.body();
              console.log('[Network] Response body size:', body.length, 'bytes');
              if (body.length > 1000) {
                const pdfPath = path.join(outputDir, 'XSZS2604020200脱敏.pdf');
                fs.writeFileSync(pdfPath, body);
                console.log('✅ PDF saved via network intercept:', pdfPath, body.length, 'bytes');
                downloadResponses.push(pdfPath);
              }
            } catch (e) {
              console.log('[Network] Could not read body:', e.message);
            }
          }
        }
      } catch (e) {}
    }
  });

  const page = await context.newPage();
  
  try {
    // Step 1: Navigate to OA contract detail page
    // The contract detail URL pattern from the HTML
    const contractUrl = 'https://oa.bangcle.com/spa/cube/#/customPage?customid=179&mainTableDataId=14242';
    console.log('Navigating to:', contractUrl);
    await page.goto(contractUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(5000);
    
    await page.screenshot({ path: path.join(outputDir, '01-contract-page.png'), fullPage: false });
    console.log('Page loaded, URL:', page.url());

    // Check page title/content
    const title = await page.title();
    console.log('Page title:', title);

    // Step 2: Try the direct download API approach
    console.log('\n[Method 1] Trying direct API download...');
    const fileId = '205115';
    const downloadApiUrl = `https://oa.bangcle.com/weaver/weaver.file.FileDownload?fileid=${fileId}&isFromPdfShow=1`;
    
    try {
      const apiResponse = await page.request.get(downloadApiUrl);
      console.log('API Status:', apiResponse.status());
      console.log('API Content-Type:', apiResponse.headers()['content-type']);
      
      if (apiResponse.ok()) {
        const body = await apiResponse.body();
        console.log('API Response size:', body.length, 'bytes');
        
        if (body.length > 1000) {
          const pdfPath = path.join(outputDir, 'XSZS2604020200脱敏.pdf');
          fs.writeFileSync(pdfPath, body);
          console.log('✅ PDF saved via API:', pdfPath, body.length, 'bytes');
        } else {
          console.log('API returned small response, trying alternative...');
        }
      }
    } catch (e) {
      console.log('API download failed:', e.message);
    }

    // Check if PDF already downloaded
    const pdfPath = path.join(outputDir, 'XSZS2604020200脱敏.pdf');
    if (fs.existsSync(pdfPath) && fs.statSync(pdfPath).size > 1000) {
      console.log('\n✅ PDF already exists:', pdfPath, fs.statSync(pdfPath).size, 'bytes');
    } else {
      // Step 3: Try clicking the download icon on the page
      console.log('\n[Method 2] Trying to click download icon on page...');
      
      // Find download icons
      const downloadIcons = await page.$$('.icon-coms-download');
      console.log('Found', downloadIcons.length, 'download icons');
      
      if (downloadIcons.length > 0) {
        // Wait for download event
        const [download] = await Promise.all([
          page.waitForEvent('download', { timeout: 15000 }),
          downloadIcons[0].click(),
        ]);
        
        const suggestedName = download.suggestedFilename();
        console.log('Download suggested name:', suggestedName);
        
        const savePath = path.join(outputDir, suggestedName || 'XSZS2604020200脱敏.pdf');
        await download.saveAs(savePath);
        console.log('✅ PDF saved via click:', savePath, fs.statSync(savePath).size, 'bytes');
      } else {
        // Try alternative: click the file link
        console.log('\n[Method 3] Trying to click file link...');
        const fileLinks = await page.$$('a.wea-field-link');
        console.log('Found', fileLinks.length, 'file links');
        
        for (const link of fileLinks) {
          const title = await link.getAttribute('title');
          if (title && title.includes('.pdf')) {
            console.log('Clicking file link:', title);
            const [download] = await Promise.all([
              page.waitForEvent('download', { timeout: 15000 }),
              link.click(),
            ]);
            const savePath = path.join(outputDir, download.suggestedFilename());
            await download.saveAs(savePath);
            console.log('✅ PDF saved via link:', savePath, fs.statSync(savePath).size, 'bytes');
            break;
          }
        }
      }
    }

    // Final check
    if (fs.existsSync(pdfPath)) {
      const size = fs.statSync(pdfPath).size;
      console.log('\n✅ Final result: PDF exists at', pdfPath, size, 'bytes');
    } else {
      console.log('\n❌ PDF not found after all attempts');
    }

    // Take final screenshot
    await page.screenshot({ path: path.join(outputDir, '02-final-state.png'), fullPage: false });

  } catch (error) {
    console.error('Error:', error.message);
    await page.screenshot({ path: path.join(outputDir, '02-error-state.png'), fullPage: false }).catch(() => {});
  } finally {
    await browser.close();
  }
})();
