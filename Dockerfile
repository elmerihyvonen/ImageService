FROM python:3.7.15-alpine

RUN apk --no-cache add \
    build-base \
    python3 \
    python3-dev \
    python3-tkinter \
    # wget dependency
    openssl \
    # dev dependencies
    bash \
    git \
    meson \
    py3-pip \
    sudo \
    # Pillow dependencies
    freetype-dev \
    fribidi-dev \
    harfbuzz-dev \
    jpeg-dev \
    lcms2-dev \
    libimagequant-dev \
    openjpeg-dev \
    tcl-dev \
    tiff-dev \
    tk-dev \
    zlib-dev \
    linux-headers \
    musl-dev \
    libusb \
    py3-configobj


RUN /usr/sbin/adduser -D pillow \
    && pip3 install --no-cache-dir -I virtualenv \
    && virtualenv /vpy3 \
    && /vpy3/bin/pip install --no-cache-dir --upgrade pip \
    && /vpy3/bin/pip install --no-cache-dir olefile pytest pytest-cov pytest-timeout \
    && /vpy3/bin/pip install --no-cache-dir numpy --only-binary=:all: || true \
    && chown -R pillow:pillow /vpy3

USER pillow
#-------------------------------------------------------------
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --upgrade Pillow

WORKDIR /imageservice-flask-test

ENV FLASK_APP=src/app.py
ENV FLASK_RUN_HOST=0.0.0.0

#Server will reload itself on file changes if in dev mode
ENV FLASK_ENV=development 

# Sudo as the server requires root access
RUN pip3 install uwsgi 

RUN pip3 install -r requirements.txt

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0", "--port=8000"]