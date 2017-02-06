FROM python:3.6.0

COPY ./app /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD python app.py
