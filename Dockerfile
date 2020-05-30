FROM python:3.7-slim-buster

RUN export DEBIAN_FRONTEND=noninteractive && \
    apt-get update -qq && apt-get upgrade -qq && \
    apt-get install -y --no-install-recommends git && \
    pip3 install -U pip setuptools

RUN pip install git+https://github.com/moscowpython/capaldi.git

CMD ["lp_run_bot"]
