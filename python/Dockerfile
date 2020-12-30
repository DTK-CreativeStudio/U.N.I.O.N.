FROM python:latest

USER root

ENV PYTHONUNBUFFERED 1

COPY requirements.txt /

ARG DEPENDENCIES="python3-pip \
                  python3-dev \
                  libusb-dev \
                  python-usb \
                  usbip"

RUN apt-get update && \
    apt-get install -y --no-install-recommends ${DEPENDENCIES} && \
    rm -rf /var/lib/apt/lists/*

RUN pip install -U pip && \
    pip install --no-cache-dir -r requirements.txt