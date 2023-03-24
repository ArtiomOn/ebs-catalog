FROM python:3.10-slim-buster

RUN apt-get  update \
&& apt-get install -y  curl unzip wget


# Chrome dependency Instalation
RUN apt-get update && apt-get install -y \
    fonts-liberation libasound2 libatk-bridge2.0-0 libatk1.0-0 libatspi2.0-0 libcups2 libdbus-1-3 libdrm2 libgbm1 \
    libgtk-3-0 libnspr4 libnss3 libwayland-client0 libxcomposite1 libxdamage1 libxfixes3 libxkbcommon0 \
    libxrandr2 xdg-utils libu2f-udev libvulkan1
 # Chrome instalation
RUN curl -LO http://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_104.0.5112.79-1_amd64.deb
RUN apt-get install -y ./google-chrome-stable_104.0.5112.79-1_amd64.deb
RUN rm google-chrome-stable_104.0.5112.79-1_amd64.deb
# Check chrome version
RUN echo "Chrome: " && google-chrome --version
# Install Chrome Driver
RUN wget https://chromedriver.storage.googleapis.com/104.0.5112.79/chromedriver_linux64.zip && \
    unzip chromedriver_linux64.zip && \
    mv chromedriver /usr/bin/chromedriver && chown root:root /usr/bin/chromedriver && chmod +x /usr/bin/chromedriver


RUN apt-get install libxrender1 -y


WORKDIR /app
EXPOSE 8000

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip --default-timeout=100 install --no-cache-dir --trusted-host pypi.python.org --trusted-host files.pythonhosted.org --trusted-host pypi.org poetry

COPY . .

RUN poetry config virtualenvs.create false --local && \
    poetry install

CMD ["gunicorn", "validator.wsgi:application", "--bind", "0.0.0.0:8000"]
