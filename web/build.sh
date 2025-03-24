set -e
pnpm run build
sudo cp -r dist/* /var/www/html/
echo "Build completato e distribuito in /var/www/html"

