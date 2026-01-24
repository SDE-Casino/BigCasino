FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Environment variables
ENV GOOGLE_CLIENT_ID=645998742216-kk51klibkolmspoaus3g2gfr97jsd376.apps.googleusercontent.com
ENV GOOGLE_CLIENT_SECRET=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
ENV GOOGLE_REDIRECT_URI=http://localhost:8004/auth/google/callback
ENV JWT_SECRET="secret"
ENV DATABASE_URL=postgresql://postgres:postgres@auth_db:5432/authentication
ENV IDP_URL=http://localhost:8009

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]