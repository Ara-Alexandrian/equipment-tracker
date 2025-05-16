FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Add a non-root user to run the application
RUN groupadd -r gearvue && useradd -r -g gearvue gearvue

# Install dependencies needed for application
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=run.py \
    FLASK_ENV=production \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Copy requirements file first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories with correct permissions
RUN mkdir -p logs output app/data Resources \
    && chown -R gearvue:gearvue /app

# Copy application code
COPY . .

# Set proper permissions
RUN chown -R gearvue:gearvue /app \
    && chmod +x start.sh \
    && find /app -type d -exec chmod 755 {} \; \
    && find /app -type f -exec chmod 644 {} \; \
    && find /app -name "*.sh" -exec chmod 755 {} \; \
    && find /app -name "*.py" -exec chmod 644 {} \;

# Expose port
EXPOSE 5000

# Switch to non-root user
USER gearvue

# Health check to ensure the app is running properly
HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
  CMD curl -f http://localhost:5000/ || exit 1

# Run the application with Gunicorn
CMD ["gunicorn", "--workers=4", "--threads=2", "--bind", "0.0.0.0:5000", "--access-logfile", "-", "--error-logfile", "-", "run:app"]