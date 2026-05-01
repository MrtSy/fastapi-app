FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv "passlib[bcrypt]" "bcrypt==4.0.1" python-jose[cryptography] python-multipart
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
