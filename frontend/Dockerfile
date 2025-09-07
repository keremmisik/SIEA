# Frontend Dockerfile
# Build stage
FROM node:18-alpine as build

WORKDIR /app

# Package files kopyala
COPY package*.json ./

# Dependencies yükle
RUN npm ci --only=production

# Source code kopyala
COPY . .

# Build
RUN npm run build

# Production stage
FROM nginx:alpine

# Nginx config
COPY --from=build /app/build /usr/share/nginx/html

# Custom nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
