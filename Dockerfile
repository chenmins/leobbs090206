ARG LEO_BBS_BASE_IMAGE=debian:trixie-slim
ARG LEO_BBS_NODE_IMAGE=node:22-bookworm-slim
FROM ${LEO_BBS_NODE_IMAGE} AS mobile-web
WORKDIR /app
COPY mobile/web/package*.json ./
RUN npm ci
COPY mobile/web/ ./
RUN npm run build

FROM ${LEO_BBS_BASE_IMAGE}

# Install Apache, Perl and required modules
RUN apt-get -o Acquire::Retries=3 update && apt-get -o Acquire::Retries=3 install -y \
    apache2 \
    tzdata \
    perl \
    libcgi-pm-perl \
    libgd-perl \
    libimage-exiftool-perl \
    libio-compress-perl \
    libdigest-md5-perl \
    libmime-base64-perl \
    libnet-perl \
    && rm -rf /var/lib/apt/lists/*

# Enable Apache CGI and rewrite modules
RUN a2enmod cgi cgid rewrite headers deflate

# Configure Apache for LeoBBS
RUN echo '<VirtualHost *:80>\n\
    ServerAdmin webmaster@localhost\n\

    DocumentRoot /var/www/html\n\
\n\
    RewriteEngine On\n\
    RewriteRule ^/?cgi-bin/leobbs\.htm$ /cgi-bin/leobbs.cgi [PT,L]\n\
    RewriteRule ^/?cgi-bin/forums-([0-9]+)-([0-9]+)\.htm$ /cgi-bin/forums.cgi?forum=$1&show=$2 [PT,L]\n\
    RewriteRule ^/?cgi-bin/topic-([0-9]+)-([0-9]+)-0-0-\.htm$ /cgi-bin/topic.cgi?forum=$1&topic=$2&start=0&show=0 [PT,L]\n\
    ScriptAlias /cgi-bin/ /var/www/html/cgi-bin/\n\
\n\
    <Directory /var/www/html>\n\
        AllowOverride None\n\
        Options Indexes FollowSymLinks\n\
        Require all granted\n\
    </Directory>\n\
\n\
    <Directory /var/www/html/cgi-bin>\n\
        AllowOverride All\n\
        Options +ExecCGI -MultiViews +SymLinksIfOwnerMatch\n\
        AddHandler cgi-script .cgi .pl\n\
        Require all granted\n\
    </Directory>\n\
\n\
    ErrorLog ${APACHE_LOG_DIR}/error.log\n\
    CustomLog ${APACHE_LOG_DIR}/access.log combined\n\
</VirtualHost>\n' > /etc/apache2/sites-available/000-default.conf

# Copy forum files
COPY cgi-bin /var/www/html/cgi-bin
COPY non-cgi /var/www/html/non-cgi
COPY --from=mobile-web /app/dist/ /var/www/html/m/
COPY --chmod=755 seo/index.cgi /opt/leobbs-seo/index.cgi
COPY --chmod=755 mobile/api/index.cgi /opt/leobbs-mobile/index.cgi
COPY mobile/api/apache.conf /etc/apache2/conf-available/leobbs-mobile.conf
RUN a2enconf leobbs-mobile

# Copy .htaccess for URL rewriting (伪静态)
COPY addon/.htaccess /var/www/html/cgi-bin/.htaccess

# Prepare a startup script that fixes bind-mount permissions on launch.
COPY docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

# Normalize Windows line endings so Apache can exec Perl CGI scripts.
RUN find /var/www/html/cgi-bin /var/www/html/non-cgi -type f \( -name "*.cgi" -o -name "*.pl" -o -name "*.pm" -o -name ".htaccess" \) -exec sed -i 's/\r$//' {} +

# Set permissions for CGI scripts and data directories
RUN chmod -R 755 /var/www/html/cgi-bin/ && \
    find /var/www/html/cgi-bin -name "*.cgi" -exec chmod 755 {} \; && \
    find /var/www/html/cgi-bin -name "*.pl" -exec chmod 755 {} \; && \
    chmod -R 770 /var/www/html/cgi-bin/data && \
    chmod -R 770 /var/www/html/cgi-bin/members && \
    chmod -R 770 /var/www/html/cgi-bin/messages && \
    chmod -R 770 /var/www/html/cgi-bin/boarddata && \
    chmod -R 770 /var/www/html/cgi-bin/record && \
    chmod -R 770 /var/www/html/cgi-bin/search && \
    chmod -R 770 /var/www/html/cgi-bin/cache && \
    chmod -R 770 /var/www/html/cgi-bin/lock && \
    chmod -R 770 /var/www/html/cgi-bin/ftpdata && \
    chmod -R 770 /var/www/html/cgi-bin/memblock && \
    chmod -R 770 /var/www/html/cgi-bin/memfav && \
    chmod -R 770 /var/www/html/cgi-bin/memfriend && \
    chmod -R 770 /var/www/html/cgi-bin/sale && \
    chmod -R 770 /var/www/html/cgi-bin/ebankdata && \
    chmod -R 775 /var/www/html/non-cgi/usr && \
    chmod -R 775 /var/www/html/non-cgi/usravatars && \
    chown -R www-data:www-data /var/www/html

# Keep a seed copy for bind-mounted directories.
RUN mkdir -p /opt/leobbs-seed/cgi-bin /opt/leobbs-seed/non-cgi && \
    cp -a /var/www/html/cgi-bin/. /opt/leobbs-seed/cgi-bin/ && \
    cp -a /var/www/html/non-cgi/. /opt/leobbs-seed/non-cgi/

RUN chmod 755 /usr/local/bin/docker-entrypoint.sh

EXPOSE 80

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["apachectl", "-D", "FOREGROUND"]
