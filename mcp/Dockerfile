
FROM python:3.10-slim
WORKDIR /mcp
COPY . .
RUN pip install fastapi uvicorn pydantic
CMD ["python", "serve.py"]
