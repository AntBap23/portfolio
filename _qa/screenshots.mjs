#!/usr/bin/env node
/**
 * Capture full-page screenshots of all site pages at desktop and mobile viewports.
 * Scrolls pages to trigger reveal animations, waits for fonts, disables animations.
 */

import { chromium } from '@playwright/test';
import { spawn } from 'child_process';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { existsSync, mkdirSync } from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const PAGES = [
  { path: '/', slug: 'home' },
  { path: '/consulting/', slug: 'consulting' },
  { path: '/consulting/services/', slug: 'consulting-services' },
  { path: '/consulting/about/', slug: 'consulting-about' },
  { path: '/consulting/samples/', slug: 'consulting-samples' },
  { path: '/consulting/samples/ai-workflow/', slug: 'consulting-samples-ai-workflow' },
  { path: '/consulting/samples/analytics-clarity/', slug: 'consulting-samples-analytics-clarity' },
  { path: '/consulting/samples/reporting-dashboard/', slug: 'consulting-samples-reporting-dashboard' },
  { path: '/consulting/process/', slug: 'consulting-process' },
  { path: '/research/', slug: 'research' },
  { path: '/projects/', slug: 'projects' },
  { path: '/experience/', slug: 'experience' },
  { path: '/competitions/', slug: 'competitions' },
  { path: '/resume/', slug: 'resume' }
];

const VIEWPORTS = {
  desktop: { width: 1280, height: 800 },
  mobile: { width: 390, height: 844 }
};

async function startServer(baseDir) {
  const serverPort = 8080;
  
  return new Promise((resolve, reject) => {
    const server = spawn('python3', ['-m', 'http.server', serverPort.toString()], {
      cwd: baseDir,
      stdio: 'pipe'
    });
    
    server.stdout.on('data', (data) => {
      if (data.toString().includes('Serving')) {
        resolve({ server, port: serverPort });
      }
    });
    
    server.stderr.on('data', (data) => {
      if (data.toString().includes('Serving')) {
        resolve({ server, port: serverPort });
      }
    });
    
    setTimeout(() => {
      resolve({ server, port: serverPort });
    }, 1000);
    
    server.on('error', reject);
  });
}

async function captureScreenshots(baseUrl, outputDir) {
  const browser = await chromium.launch();
  
  for (const [viewportName, viewport] of Object.entries(VIEWPORTS)) {
    console.log(`\nCapturing ${viewportName} screenshots (${viewport.width}x${viewport.height})...`);
    
    const context = await browser.newContext({
      viewport,
      deviceScaleFactor: 1
    });
    
    // Inject CSS to disable animations and transitions
    await context.addInitScript(() => {
      const style = document.createElement('style');
      style.textContent = `
        *, *::before, *::after {
          animation-duration: 0s !important;
          animation-delay: 0s !important;
          transition-duration: 0s !important;
          transition-delay: 0s !important;
        }
      `;
      document.addEventListener('DOMContentLoaded', () => {
        document.head.appendChild(style);
      });
    });
    
    const page = await context.newPage();
    
    for (const pageInfo of PAGES) {
      const url = `${baseUrl}${pageInfo.path}`;
      const outputFile = join(outputDir, `${pageInfo.slug}-${viewportName}.png`);
      
      console.log(`  ${pageInfo.path} -> ${pageInfo.slug}-${viewportName}.png`);
      
      try {
        await page.goto(url, { waitUntil: 'networkidle' });
        
        // Wait for fonts to load
        await page.waitForFunction(() => document.fonts.ready);
        
        // Scroll page in steps to trigger reveal animations
        const scrollHeight = await page.evaluate(() => document.body.scrollHeight);
        const viewportHeight = viewport.height;
        const steps = Math.ceil(scrollHeight / viewportHeight);
        
        for (let i = 0; i < steps; i++) {
          await page.evaluate((offset) => window.scrollTo(0, offset), i * viewportHeight);
          await page.waitForTimeout(100);
        }
        
        // Scroll back to top
        await page.evaluate(() => window.scrollTo(0, 0));
        await page.waitForTimeout(200);
        
        // Capture full page screenshot
        await page.screenshot({
          path: outputFile,
          fullPage: true
        });
      } catch (error) {
        console.error(`    Error capturing ${pageInfo.path}: ${error.message}`);
      }
    }
    
    await context.close();
  }
  
  await browser.close();
}

async function main() {
  const args = process.argv.slice(2);
  let baseUrl = args[0];
  let serverProcess = null;
  
  // Determine base directory and URL
  if (!baseUrl) {
    // Start local server
    const baseDir = join(__dirname, '..');
    console.log(`Starting local server from ${baseDir}...`);
    const { server, port } = await startServer(baseDir);
    serverProcess = server;
    baseUrl = `http://localhost:${port}`;
    console.log(`Server running at ${baseUrl}`);
  }
  
  // Create output directory
  const outputDir = join(__dirname, 'baseline');
  if (!existsSync(outputDir)) {
    mkdirSync(outputDir, { recursive: true });
  }
  
  try {
    await captureScreenshots(baseUrl, outputDir);
    console.log(`\n✓ Screenshots saved to ${outputDir}`);
  } finally {
    if (serverProcess) {
      serverProcess.kill();
    }
  }
}

main().catch(console.error);
