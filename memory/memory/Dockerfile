FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY main.py .

# Environment variables
ENV JWT_ALGORITHM=HS256
ENV JWT_SECRET_KEY="secret"
ENV LOGIC_LAYER_SERVICE_URL=http://memory_logic:8000

# Expose the port
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]