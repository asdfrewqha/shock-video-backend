FROM python:3.13-alpine

RUN apk add --no-cache \
    build-base \
    cmake \
    pkgconfig \
    jpeg-dev \
    zlib-dev \
    libjpeg \
    libpng \
    libwebp \
    libavif \
    libressl-dev

COPY ./requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]