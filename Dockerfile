FROM python:3.10

RUN apt update && apt upgrade -y
RUN apt install git -y
RUN pip install google-generativeai
RUN pip install openai==0.27.0
COPY requirements.txt /requirements.txt

RUN cd /
RUN pip3 install -U pip && pip3 install -U -r requirements.txt
RUN mkdir /Elsa
WORKDIR /Elsa
COPY start.sh /start.sh
CMD ["/bin/bash", "/start.sh"]
