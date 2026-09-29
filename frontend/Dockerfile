FROM public.ecr.aws/docker/library/nginx:alpine

# Security patch:
# CVE-2026-93990 requires libexpat >= 2.8.5-r0.
RUN apk upgrade --no-cache libexpat

COPY index.html /usr/share/nginx/html/index.html
COPY style.css /usr/share/nginx/html/style.css
COPY app.js /usr/share/nginx/html/app.js

EXPOSE 80
