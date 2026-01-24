FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Environment variables
ENV JWT_ALGORITHM=HS256
ENV JWT_SECRET_KEY="secret"
ENV LOGIC_LAYER_SERVICE_URL=http://solitaire_logic:8000
ENV LEADERBOARD_URL=http://solitaire_leaderboard_adapter:8000

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]