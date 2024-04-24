FROM python:3.12.2-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt -i https://mirrors.cloud.tencent.com/pypi/simple

COPY image_replacer_webhook .

RUN addgroup --gid 1001 --system app && \
    adduser --no-create-home --shell /bin/false --disabled-password --uid 1001 --system --group app

USER app

CMD [ "python", "main.py" ]