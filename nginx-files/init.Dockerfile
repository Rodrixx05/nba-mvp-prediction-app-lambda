FROM nginx:1.23.1

RUN rm /etc/nginx/nginx.conf
COPY nginx.conf /etc/nginx/

RUN rm /etc/nginx/conf.d/default.conf
COPY project_init.conf /etc/nginx/conf.d/

COPY ./static ./static