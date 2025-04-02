FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories if they don't exist
RUN mkdir -p data/tafsirs vector_db

# Expose ports for FastAPI and Streamlit
EXPOSE 8000 8501

# Create entry point script
RUN echo '#!/bin/sh\n\
if [ "$1" = "api" ]; then\n\
    exec uvicorn app.api:app --host 0.0.0.0 --port 8000\n\
elif [ "$1" = "streamlit" ]; then\n\
    exec streamlit run app/streamlit_app.py --server.port 8501 --server.address 0.0.0.0\n\
else\n\
    echo "Please specify either 'api' or 'streamlit' as the command"\n\
    exit 1\n\
fi' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["api"]
