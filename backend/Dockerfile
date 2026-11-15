# Lightweight Python base image
FROM python:3.11-slim

# Working directory inside the container
WORKDIR /app

# Copy the app, the model and the requirements
COPY . .

# Install dependencies without caching to keep the image small
RUN pip install --no-cache-dir -r requirements.txt

# Serve the Flask app with Gunicorn: 4 workers on port 7860, all interfaces
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7860", "app:superkart_api"]
