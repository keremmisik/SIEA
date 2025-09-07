#!/bin/bash

# SIEA Production Deployment Script

set -e

echo "🚀 SIEA Production Deployment Starting..."

# Configuration
DOMAIN=${1:-"your-domain.com"}
EMAIL=${2:-"admin@your-domain.com"}

echo "📋 Deployment Configuration:"
echo "   Domain: $DOMAIN"
echo "   Email: $EMAIL"

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed"
    exit 1
fi

# Create production environment file if not exists
if [ ! -f ".env.production" ]; then
    echo "📝 Creating production environment file..."
    cat > .env.production << EOF
# Production Environment Variables
DATABASE_URL=postgresql://siea_user:$(openssl rand -base64 32)@postgres:5432/siea_db
SECRET_KEY=$(openssl rand -base64 64)
ENCRYPTION_KEY=$(openssl rand -base64 32)

# Domain Configuration
DOMAIN=$DOMAIN
EMAIL=$EMAIL

# File Upload
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=jpg,jpeg,png,pdf

# Data Retention
DATA_RETENTION_YEARS=5
EOF
    echo "✅ Production environment file created"
    echo "⚠️  Please review and update .env.production file"
fi

# Build and start services
echo "🏗️  Building and starting services..."
docker-compose -f docker-compose.yml --env-file .env.production up -d --build

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 30

# Run database migrations
echo "🗄️  Running database migrations..."
docker-compose -f docker-compose.yml --env-file .env.production exec backend python database/migrations.py

# Setup SSL with Let's Encrypt (if domain is provided)
if [ "$DOMAIN" != "your-domain.com" ]; then
    echo "🔒 Setting up SSL certificate..."
    docker run --rm -it \
        -v /etc/letsencrypt:/etc/letsencrypt \
        -v /var/lib/letsencrypt:/var/lib/letsencrypt \
        -p 80:80 -p 443:443 \
        certbot/certbot certonly --standalone \
        --email $EMAIL \
        --agree-tos \
        --no-eff-email \
        -d $DOMAIN
fi

# Setup nginx reverse proxy
echo "🌐 Setting up reverse proxy..."
cat > nginx-production.conf << EOF
server {
    listen 80;
    server_name $DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $DOMAIN;
    
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Setup automatic backup
echo "💾 Setting up automatic backup..."
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/siea"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Database backup
docker-compose exec postgres pg_dump -U siea_user siea_db > $BACKUP_DIR/db_backup_$DATE.sql

# Keep only last 30 days of backups
find $BACKUP_DIR -name "db_backup_*.sql" -mtime +30 -delete

echo "Backup completed: $DATE"
EOF

chmod +x backup.sh

# Add to crontab
(crontab -l 2>/dev/null; echo "0 2 * * * /path/to/your/project/backup.sh") | crontab -

echo ""
echo "🎉 Production deployment completed!"
echo ""
echo "📋 Service Information:"
echo "   Frontend: https://$DOMAIN"
echo "   Backend API: https://$DOMAIN/api"
echo "   Database: PostgreSQL (internal)"
echo ""
echo "📝 Important Notes:"
echo "1. Review .env.production file and update secrets"
echo "2. Configure firewall to allow ports 80, 443"
echo "3. Setup monitoring and logging"
echo "4. Update backup script path in crontab"
echo ""
echo "🔧 Management Commands:"
echo "   View logs: docker-compose -f docker-compose.yml --env-file .env.production logs"
echo "   Restart: docker-compose -f docker-compose.yml --env-file .env.production restart"
echo "   Stop: docker-compose -f docker-compose.yml --env-file .env.production down"
