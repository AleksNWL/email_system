FROM nginx:alpine

# Копируем файл конфигурации Nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Копируем статику для отдачи напрямую
COPY ./static /usr/share/nginx/html/static

EXPOSE 80
