#!/bin/sh
set -e
mkdir -p out
printf '%s' "$PANEL_KEY" > /tmp/k
openssl enc -d -aes-256-cbc -pbkdf2 -in panel.enc -out out/index.html -pass file:/tmp/k
rm -f /tmp/k
cp -r highlights out/highlights
test -s out/index.html
# Kontent plan: rəhbərlik üçün yan-yana cədvəl (kp-board.js), əsas paneldən sonra yüklənir
V=$(date +%s)
cp kp-board.js out/kp-board.js
sed -i "s#</body>#<script src=\"/kp-board.js?v=$V\"></script></body>#" out/index.html
grep -q 'kp-board.js' out/index.html
