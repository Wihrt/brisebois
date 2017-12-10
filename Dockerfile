FROM python:3.6.3-jessie

LABEL maintainer="arnaud.hatzenbuhler@gmail.com"

ENV MONGO_HOST=mongo MONGO_PORT=27019

COPY ./brisebois /brisebois
RUN pip install --no-cache-dir -r /brisebois/requirements.txt
WORKDIR /brisebois
CMD ["python", "bot.py"]
