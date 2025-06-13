FROM python:3.12
WORKDIR /usr/local/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd app
USER app

COPY . .
EXPOSE 8000

CMD ["python","app.py"]
