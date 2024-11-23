FROM alpine:latest

LABEL Name="bsky_analyzer"
LABEL Version="0.1-alpha"
LABEL AuthorName="mcbazza"
LABEL AuthorProfile="https://bsky.app/profile/mcbazza.com"
LABEL description="A tool for analysing posts from a Bluesky account and graphing them by hour/day/week/month"

RUN apk update

RUN apk add --update --no-cache git wget python3 py3-pip

RUN ln -sf python3 /usr/bin/python
RUN python3 -m pip install --break-system-packages  --upgrade pip

RUN git clone https://github.com/mcbazza/bsky_analyzer/ --branch 0.1-alpha
RUN cd bsky_analyzer

RUN pip install --break-system-packages argparse numpy datetime requests
RUN pip install -U --break-system-packages atproto

RUN pip install --break-system-packages https://github.com/nyurik/py-ascii-graph/archive/refs/heads/fix-python310.zip

COPY bsky_analyzer.py /bsky_analyzer/

WORKDIR /bsky_analyzer

ENV docker_env=true

ENTRYPOINT [ "python3", "./bsky_analyzer.py", "--name"]
