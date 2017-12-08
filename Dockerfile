FROM hub.c.163.com/library/python:2.7

MAINTAINER forin

# Set the timezone.
RUN echo "Asia/Chongqing" > /etc/timezone && dpkg-reconfigure -f noninteractive tzdata

RUN mkdir -p /usr/src/stock
WORKDIR /usr/src/stock

COPY ./requirements.txt  /usr/src/stock/

RUN pip install -r requirements.txt -i http://pypi.douban.com/simple --trusted-host pypi.douban.com

COPY . /usr/src/stock

EXPOSE 5000

ENV PYTHONUNBUFFERED TRUE

CMD ["gunicorn", "--access-logfile=-", "--workers=4", "--capture-output", "--timeout=300", "-b 0.0.0.0:5000", "wsgi:stock"]

