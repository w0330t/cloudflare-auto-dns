FROM python:3

WORKDIR /usr/src/app

RUN mkdir CloudflareSpeedTest && \
    wget -q -O - "https://github.com/XIU2/CloudflareSpeedTest/releases/download/v2.2.4/CloudflareST_linux_amd64.tar.gz" \
    | tar -xzf - -C  ./CloudflareSpeedTest && \
    chmod -R +x ./CloudflareSpeedTest
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "-u", "./main.py" ]