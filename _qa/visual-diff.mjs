#!/usr/bin/env node
/**
 * Compare screenshots against baseline and report pixel differences.
 */

import { readFileSync, readdirSync, existsSync } from 'fs';
import { join } from 'path';
import { PNG } from 'pngjs';
import pixelmatch from 'pixelmatch';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

function compareImages(baselinePath, currentPath) {
  if (!existsSync(currentPath)) {
    return { error: 'Current screenshot not found' };
  }
  
  const baseline = PNG.sync.read(readFileSync(baselinePath));
  const current = PNG.sync.read(readFileSync(currentPath));
  
  if (baseline.width !== current.width || baseline.height !== current.height) {
    return {
      error: `Dimension mismatch: baseline ${baseline.width}x${baseline.height}, current ${current.width}x${current.height}`
    };
  }
  
  const { width, height } = baseline;
  const diff = new PNG({ width, height });
  
  const numDiffPixels = pixelmatch(
    baseline.data,
    current.data,
    diff.data,
    width,
    height,
    { threshold: 0.1 }
  );
  
  const totalPixels = width * height;
  const percentDiff = (numDiffPixels / totalPixels * 100).toFixed(2);
  
  return {
    numDiffPixels,
    totalPixels,
    percentDiff
  };
}

async function main() {
  const args = process.argv.slice(2);
  const currentDir = args[0] || join(__dirname, 'current');
  const baselineDir = join(__dirname, 'baseline');
  
  if (!existsSync(baselineDir)) {
    console.error(`Baseline directory not found: ${baselineDir}`);
    process.exit(1);
  }
  
  if (!existsSync(currentDir)) {
    console.error(`Current screenshots directory not found: ${currentDir}`);
    process.exit(1);
  }
  
  const baselineFiles = readdirSync(baselineDir).filter(f => f.endsWith('.png'));
  
  console.log(`Comparing screenshots...\n`);
  console.log(`Baseline: ${baselineDir}`);
  console.log(`Current:  ${currentDir}\n`);
  
  let totalDiffPixels = 0;
  let hasErrors = false;
  
  for (const filename of baselineFiles.sort()) {
    const baselinePath = join(baselineDir, filename);
    const currentPath = join(currentDir, filename);
    
    const result = compareImages(baselinePath, currentPath);
    
    if (result.error) {
      console.log(`✗ ${filename}: ${result.error}`);
      hasErrors = true;
    } else {
      const status = result.numDiffPixels === 0 ? '✓' : '△';
      console.log(`${status} ${filename}: ${result.numDiffPixels.toLocaleString()} pixels differ (${result.percentDiff}%)`);
      totalDiffPixels += result.numDiffPixels;
    }
  }
  
  console.log(`\nTotal diff pixels: ${totalDiffPixels.toLocaleString()}`);
  
  if (hasErrors) {
    console.log('\n✗ Some comparisons failed');
    process.exit(1);
  } else if (totalDiffPixels === 0) {
    console.log('\n✓ All screenshots match baseline perfectly');
  } else {
    console.log('\n△ Some differences detected');
  }
}

main().catch(console.error);
