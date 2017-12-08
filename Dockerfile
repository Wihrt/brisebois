FROM python:3.6-alpine

COPY ./brisebois /
RUN pip install --no-cache-dir -r /brisebois/requirements.txt
CMD ["python", "/brisebois/boy.py"]
