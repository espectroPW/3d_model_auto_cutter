# STL 3D Model Splitter - Docker Container
# Multi-stage build for optimal size and security

FROM python:3.9-slim as python-base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgl1-mesa-dri \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    trimesh==3.23.5 \
    numpy==1.24.3 \
    matplotlib==3.7.1

# Final stage with PHP
FROM php:8.1-apache

# Install system dependencies for PHP and Python
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    libzip-dev \
    zip \
    unzip \
    gcc \
    g++ \
    libgl1-mesa-dri \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install PHP extensions
RUN docker-php-ext-install zip

# Install Python packages using system Python
RUN pip3 install --no-cache-dir --break-system-packages \
    trimesh==3.23.5 \
    numpy==1.24.3 \
    matplotlib==3.7.1

# Set up Apache
RUN a2enmod rewrite
RUN a2enmod headers

# Configure PHP
RUN echo "upload_max_filesize = 50M" >> /usr/local/etc/php/conf.d/uploads.ini \
    && echo "post_max_size = 50M" >> /usr/local/etc/php/conf.d/uploads.ini \
    && echo "max_execution_time = 300" >> /usr/local/etc/php/conf.d/uploads.ini \
    && echo "memory_limit = 512M" >> /usr/local/etc/php/conf.d/uploads.ini \
    && echo "file_uploads = On" >> /usr/local/etc/php/conf.d/uploads.ini

# Create application directory
WORKDIR /var/www/html

# Copy application files
COPY index.html .
COPY stl_splitter_api.php .
COPY stl_processor.py .

# Set permissions
RUN chmod 755 stl_processor.py \
    && chmod 644 index.html \
    && chmod 644 stl_splitter_api.php \
    && chown -R www-data:www-data /var/www/html

# Create temp directory with proper permissions
RUN mkdir -p /tmp/stl_splitter \
    && chmod 777 /tmp/stl_splitter

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# Expose port
EXPOSE 80

# Start Apache
CMD ["apache2-foreground"]
