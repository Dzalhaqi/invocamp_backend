FROM python:3.10.6-slim-buster
ENV PIP_NO_CACHE_DIR off
ENV PIP_DISABLE_PIP_VERSION_CHECK on
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV COLUMNS 80
RUN apt-get update \
  && apt-get install -y --force-yes \
  nano python3-pip gettext binutils libproj-dev gdal-bin libgdal-dev chrpath libssl-dev libxft-dev \
  libfreetype6 libfreetype6-dev postgis libfontconfig1 libfontconfig1-dev\
  && rm -rf /var/lib/apt/lists/*
WORKDIR /backend/
COPY requirements.txt .
RUN pip install --trusted-host pypi.python.org -r requirements.txt
COPY . /backend/
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]