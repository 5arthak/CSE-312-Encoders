docker run -it --rm --name certbot \
            -p 242:80 -p 443:443 \
            -v "/srv/nginx/cert:/etc/letsencrypt" \
            certbot/certbot certonly --standalone -d www.encoderlist.click -d encoderlist.click \
                 --non-interactive --agree-tos \
                 --email mweng@buffalo.edu --expand