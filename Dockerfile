FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

WORKDIR /app

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Set data directory to a persistent volume path
ENV DATA_DIR="/app/data"

# Create the data directory so it exists even if volume isn't mounted yet
RUN mkdir -p /app/data

# Run the main script
CMD ["python", "-u", "main.py"]
