#!/bin/sh
set -e
mkdir -p out
printf '%s' "$PANEL_KEY" > /tmp/k
openssl enc -d -aes-256-cbc -pbkdf2 -in panel.enc -out out/index.html -pass file:/tmp/k
rm -f /tmp/k
cp -r highlights out/highlights
test -s out/index.html
