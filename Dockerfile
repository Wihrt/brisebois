FROM python:3.6-alpine

LABEL maintainer="arnaud.hatzenbuhler@gmail.com"

COPY ./brisebois /
RUN pip install --no-cache-dir -r /brisebois/requirements.txt
CMD ["python", "/brisebois/bot.py"]
