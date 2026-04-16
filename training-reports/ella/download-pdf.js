const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const stateFile = path.resolve(__dirname, 'oa-working-state.json');
  const saveDir = path.resolve(__dirname);
  
  if (!fs.existsSync(stateFile)) {
    console.error('State file not found:', stateFile);
    process.exit(1);
  }

  const storageState = JSON.parse(fs.readFileSync(stateFile, 'utf-8'));

  const browser = await chromium.launch({
    headless: false,
    slowMo: 500,
  });

  const context = await browser.newContext({
    storageState: stateFile,
    acceptDownloads: true,
    viewport: { width: 1440, height: 900 },
  });

  const page = await context.newPage();
  
  // Track downloads
  page.on('download', async download => {
    console.log('Download started:', download.suggestedFilename());
  });

  try {
    // Step 1: Navigate to the OA system
    console.log('Navigating to OA...');
    await page.goto('https://oa.bangcle.com', { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(3000);
    console.log('Page loaded, URL:', page.url());

    // Take screenshot to verify login state
    await page.screenshot({ path: path.join(saveDir, '01-after-oa-nav.png') });

    // Step 2: Navigate to contract detail page
    // customid=179 is the contract ledger (合同台账), customid=272 is contract sub-item
    console.log('Navigating to contract detail...');
    
    // Try the SPA route for the contract detail
    const contractUrl = 'https://oa.bangcle.com/spa/cube/#/customPage?customid=179&mainTableDataId=14242';
    await page.goto(contractUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(5000);
    
    console.log('Contract page loaded, URL:', page.url());
    await page.screenshot({ path: path.join(saveDir, '02-contract-page.png') });

    // Step 3: Find the download button for the PDF
    // The file ID is 205115, the download icon has class 'icon-coms-download'
    console.log('Looking for download icon...');
    
    // Try to find all download icons
    const downloadIcons = await page.$$('.icon-coms-download');
    console.log('Found download icons:', downloadIcons.length);

    if (downloadIcons.length > 0) {
      // Set up download listener
      const [download] = await Promise.all([
        page.waitForEvent('download', { timeout: 15000 }),
        downloadIcons[0].click(),
      ]);
      
      const fileName = download.suggestedFilename();
      console.log('Downloading:', fileName);
      
      const savePath = path.join(saveDir, fileName);
      await download.saveAs(savePath);
      console.log('Saved to:', savePath);
      
      const stats = fs.statSync(savePath);
      console.log('File size:', stats.size, 'bytes');
    } else {
      console.log('No download icons found. Trying alternative approach...');
      
      // Try clicking the file link instead
      const fileLinks = await page.$$('a.wea-field-link');
      console.log('Found file links:', fileLinks.length);
      
      for (const link of fileLinks) {
        const title = await link.getAttribute('title');
        console.log('File link title:', title);
        if (title && title.includes('.pdf')) {
          const [download] = await Promise.all([
            page.waitForEvent('download', { timeout: 15000 }),
            link.click(),
          ]);
          
          const savePath = path.join(saveDir, download.suggestedFilename());
          await download.saveAs(savePath);
          console.log('Saved:', savePath);
          break;
        }
      }
    }

    // Also try the API approach - the file ID is 205115
    console.log('\nTrying API download approach...');
    
    // Common e-cology download URL patterns
    const downloadUrls = [
      `https://oa.bangcle.com/api/portal/doc/docPreview/download?fileid=205115`,
      `https://oa.bangcle.com/weaver/weaver.file.FileDownload?fileid=205115&isFromPdfShow=1`,
      `https://oa.bangcle.com/file/205115`,
    ];

    for (const url of downloadUrls) {
      try {
        const response = await page.request.get(url);
        if (response.ok()) {
          const body = await response.body();
          if (body.length > 1000) { // PDF files are typically > 1KB
            const savePath = path.join(saveDir, 'XSZS2604020200脱敏.pdf');
            fs.writeFileSync(savePath, body);
            console.log('API download success:', savePath, body.length, 'bytes');
            break;
          }
        }
      } catch (e) {
        console.log('API URL failed:', url, e.message);
      }
    }

  } catch (error) {
    console.error('Error:', error.message);
  } finally {
    await page.screenshot({ path: path.join(saveDir, '03-final-state.png') });
    await browser.close();
  }
})();
