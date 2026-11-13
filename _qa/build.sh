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

# Copy static files Jekyll may not emit into _site so fail-closed checks can see them
for f in CNAME llms.txt robots.txt; do
  if [ -f "$REPO_ROOT/$f" ]; then
    cp "$REPO_ROOT/$f" "$SCRIPT_DIR/_site/$f"
    echo "Copied $f into _qa/_site/"
  else
    echo "WARNING: $f missing from repo root"
    exit 1
  fi
done

echo "Build complete. Output in _qa/_site/"

# Verify _qa/ itself is excluded from build
if [ -d "$SCRIPT_DIR/_site/_qa" ]; then
  echo "WARNING: _qa/ was included in build output (should be excluded by Jekyll)"
  exit 1
else
  echo "Verified: _qa/ excluded from build output"
fi
