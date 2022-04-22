FROM nginx:mainline-alpine

RUN rm /etc/nginx/nginx.conf
COPY nginx.conf /etc/nginx/
RUN rm /etc/nginx/conf.d/default.conf
COPY smartrade.conf /etc/nginx/conf.d/
