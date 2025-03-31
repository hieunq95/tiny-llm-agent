FROM nginx:alpine

# Remove default Nginx config
RUN rm -rf /etc/nginx/conf.d/*

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]