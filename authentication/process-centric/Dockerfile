FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# Environment variables
ENV JWT_ALGORITHM=HS256
ENV JWT_SECRET_KEY="secret"
ENV ACCESS_TOKEN_MINUTES=60
ENV REFRESH_TOKEN_MINUTES=1
ENV GOOGLE_AUTH_URL="http://google_auth:8000"
ENV GOOGLE_REDIRECT_URL="http://google_auth:8000"
ENV GOOGLE_AUTH_EXTERNAL_URL="http://localhost:8004"
ENV UI_REDIRECT_URL="http://localhost:3000/auth"
ENV LOGIC_LAYER_URL="http://auth_logic:8000"

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]