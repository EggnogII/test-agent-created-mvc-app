# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Do not generate .pyc files and ensure output is unbuffered
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . /app

# Expose the service port; match the PORT environment variable in app.py
EXPOSE 5000

# Run the web application
CMD ["python", "app.py"]