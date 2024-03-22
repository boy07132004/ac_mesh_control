FROM python:3.9-slim-buster

RUN apt update \
	&& apt install -y build-essential cron tzdata ntpdate\
	&& rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt requirements.txt

RUN python3 -m pip install --no-cache-dir -r requirements.txt
COPY ./run.sh run.sh
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
	&& echo $TZ > /etc/timezone \
	&& dpkg-reconfigure -f noninteractive tzdata \
	&& chmod +x ./run.sh

CMD ["./run.sh"]
