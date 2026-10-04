FROM public.ecr.aws/docker/library/nginx:alpine

# Security patches:
# CVE-2026-93990: update libexpat.
# CVE-2026-103111: update pcre2 to a fixed release.
RUN apk upgrade --no-cache libexpat pcre2

COPY index.html /usr/share/nginx/html/index.html
COPY style.css /usr/share/nginx/html/style.css
COPY app.js /usr/share/nginx/html/app.js

EXPOSE 80
