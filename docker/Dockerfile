FROM python:3.11-slim

WORKDIR /app

COPY schemas/ ./schemas/
COPY validators/ ./validators/
COPY tasks/ ./tasks/

CMD ["python3", "validators/validate_task.py", "tasks/examples/valid_task.json"]
