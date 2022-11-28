FROM python:3.6.1-alpine

RUN pip3 install --upgrade pip

WORKDIR /imageservice-flask-test

ADD . /imageservice-flask-test

RUN pip3 install -r requirements.txt

CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0", "--port=8000","src/app.py"]