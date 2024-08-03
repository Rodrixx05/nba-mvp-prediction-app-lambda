FROM nginx:1.23.1

ARG MLFLOW_AUTH_USERNAME
ARG MLFLOW_AUTH_PASSWORD

ENV BASIC_USERNAME=$MLFLOW_AUTH_USERNAME
ENV BASIC_PASSWORD=$MLFLOW_AUTH_PASSWORD

RUN rm /etc/nginx/nginx.conf
COPY nginx.conf /etc/nginx/

RUN rm /etc/nginx/conf.d/default.conf
COPY project_dev.conf /etc/nginx/conf.d/

COPY ./static ./static

RUN apt-get update && apt-get update && apt-get -y install apache2-utils

COPY run.sh ./
RUN chmod 0755 ./run.sh
CMD [ "./run.sh" ]