FROM python:3.8

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./run.py /app/run.py
COPY . .
COPY ./ /app/

CMD ["sh", "-c", "pip install -r requirements.txt && python /app/run.py"]
