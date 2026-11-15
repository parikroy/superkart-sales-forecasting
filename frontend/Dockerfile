# Lightweight Python base image
FROM python:3.11-slim

# Working directory inside the container
WORKDIR /app

# Copy the Streamlit app and its requirements
COPY . .

# Install dependencies without caching to keep the image small
RUN pip install --no-cache-dir -r requirements.txt

# Run Streamlit on port 8501, reachable from outside the container
# (XSRF protection is disabled so file uploads work behind the Codespaces proxy)
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableXsrfProtection=false"]
