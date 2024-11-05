FROM python:3.12

WORKDIR /app

COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt

# create the logs file
RUN mkdir -p /app/logs

COPY . .

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
