FROM ubuntu:20.04

RUN apt-get update && \
  apt-get install -y python3 python3-pip python3-dev
# Create app directory
WORKDIR /app

# Install app dependencies
COPY requirements.txt .

RUN pip install -r requirements.txt
RUN python3 -m playwright install
ENV DEBIAN_FRONTEND="noninteractive"
RUN python3 -m playwright install-deps
# Bundle app source
COPY . /app

CMD ["python3", "main.py"]
