FROM nginx

COPY ./default.conf /etc/nginx/conf.d/default.conf
COPY /etc/letsencrypt/live/encoderlist.click/cert.pem /etc/nginx/cert.pem
COPY /etc/letsencrypt/live/encoderlist.click/privkey.pem /etc/nginx/privkey.key

