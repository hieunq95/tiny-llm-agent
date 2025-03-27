FROM nginx:alpine

# Remove default Nginx config
# Disable entrypoint interference
RUN mv /docker-entrypoint.sh /docker-entrypoint-disabled.sh && \
    echo '#!/bin/sh' > /docker-entrypoint.sh && \
    echo 'exec nginx -g "daemon off;"' >> /docker-entrypoint.sh && \
    chmod +x /docker-entrypoint.sh

COPY nginx.conf /etc/nginx/nginx.conf
RUN rm -rf /etc/nginx/conf.d/*

CMD ["nginx", "-g", "daemon off;"]