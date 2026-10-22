FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
COPY skills ./skills
RUN pip install --no-cache-dir .
ENV HOST=0.0.0.0 PORT=8000
CMD ["uvicorn", "bu_agent.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]

