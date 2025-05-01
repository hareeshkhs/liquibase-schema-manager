FROM public.ecr.aws/docker/library/alpine:3.18

# Upgrade and install dependencies
RUN apk upgrade && apk add --no-cache \
  python3 \
  py3-pip \
  postgresql14-client \
  openjdk8-jre \
  build-base \
  bash

# Add liquibase user
RUN adduser -h /home/liquibase-schema-manager -D liquibase-schema-manager

# Set user environment
ENV PATH=/home/liquibase-schema-manager/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Optional build-time args
ARG ARTIFACTORY_USERNAME
ARG ARTIFACTORY_PASSWORD
ARG TAG
ENV TAG=$TAG

# Switch to liquibase user
USER liquibase-schema-manager

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt --prefer-binary

# Copy application files
COPY --chown=liquibase-schema-manager:liquibase-schema-manager . /home/liquibase-schema-manager/

WORKDIR /home/liquibase-schema-manager

# Debug log before running the app
CMD ["sh", "-c", "echo 'Starting container...' && echo 'ENV TAG: $TAG' && ls -al && echo 'Launching app...' && python3 main.py || echo 'App failed. Check logs.'"]