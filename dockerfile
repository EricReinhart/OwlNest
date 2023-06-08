FROM python:3.9

RUN apt-get update && apt-get install -y libpq-dev
RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt
COPY . /code/
ENV DJANGO_SETTINGS_MODULE=OwlNest.settings
ENV PYTHONUNBUFFERED=1
COPY gunicorn.conf /code/ 
CMD ["/code/release.sh"]