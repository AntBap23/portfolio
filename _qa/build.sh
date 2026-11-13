#!/usr/bin/env bash
# Build the site using GitHub Pages Jekyll configuration

set -e

cd "$(dirname "$0")"

echo "Installing dependencies..."
bundle config set --local path 'vendor/bundle'
bundle install

echo "Building site..."
bundle exec jekyll build --source .. --destination _site

echo "Build complete. Output in _qa/_site/"

# Verify _qa/ itself is excluded from build
if [ -d "_site/_qa" ]; then
    echo "WARNING: _qa/ was included in build output (should be excluded by Jekyll)"
    exit 1
else
    echo "✓ Verified: _qa/ excluded from build output"
fi
