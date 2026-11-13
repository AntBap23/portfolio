#!/usr/bin/env bash
# Build the site using GitHub Pages Jekyll configuration.
# Run from repo root: bash _qa/build.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$SCRIPT_DIR"

echo "Installing dependencies..."
bundle config set --local path 'vendor/bundle'
bundle install

echo "Building site..."
bundle exec jekyll build --source "$REPO_ROOT" --destination "$SCRIPT_DIR/_site"

# CNAME is not emitted by Jekyll into _site; copy it so fail-closed checks can verify it.
# Do NOT copy llms.txt or robots.txt: Jekyll already emits them byte-identical from source.
# Copying them would hide a real publish failure if Jekyll stopped emitting either file.
if [ -f "$REPO_ROOT/CNAME" ]; then
  cp "$REPO_ROOT/CNAME" "$SCRIPT_DIR/_site/CNAME"
  echo "Copied CNAME into _qa/_site/"
else
  echo "WARNING: CNAME missing from repo root"
  exit 1
fi

if [ ! -f "$SCRIPT_DIR/_site/llms.txt" ]; then
  echo "WARNING: Jekyll did not emit llms.txt into _site"
  exit 1
fi
if [ ! -f "$SCRIPT_DIR/_site/robots.txt" ]; then
  echo "WARNING: Jekyll did not emit robots.txt into _site"
  exit 1
fi

echo "Build complete. Output in _qa/_site/"

# Verify _qa/ itself is excluded from build
if [ -d "$SCRIPT_DIR/_site/_qa" ]; then
  echo "WARNING: _qa/ was included in build output (should be excluded by Jekyll)"
  exit 1
else
  echo "Verified: _qa/ excluded from build output"
fi
