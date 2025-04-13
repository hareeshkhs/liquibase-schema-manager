FROM public.ecr.aws/docker/library/alpine:3.18
RUN apk upgrade
RUN apk add --update \
  python3 \
  python3-dev \
  py-pip \
  postgresql14-client \
  build-base \
  openjdk8-jre \
  && pip install --ignore-installed distlib virtualenv \
  && rm -rf /var/cache/apk/*
RUN apk add --no-cache --update bash
RUN apk add --no-cache --update py-pip
RUN adduser -h /home/liquibase-schema-manager -D liquibase-schema-manager
ENV PATH=/home/liquibase-schema-manager/.local/bin:$PATH
ARG ARTIFACTORY_USERNAME
ARG ARTIFACTORY_PASSWORD
ARG TAG

USER liquibase-schema-manager
COPY requirements.txt .
RUN pip3 install --no-cache-dir --user -r requirements.txt --prefer-binary
RUN rm -rf /var/lib/apt/lists/*
COPY --chown=liquibase-schema-manager:liquibase-schema-manager . /home/liquibase-schema-manager/
USER liquibase-schema-manager
WORKDIR /home/liquibase-schema-manager

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV TAG=$TAG
CMD ["sh", "-c", "python3 main.py"]
