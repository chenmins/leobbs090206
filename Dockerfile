FROM debian:bullseye-slim

# Install Apache, Perl and required modules
RUN apt-get update && apt-get install -y \
    apache2 \
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
RUN a2enmod cgi cgid rewrite

# Configure Apache for LeoBBS
RUN echo '<VirtualHost *:80>\n\
    ServerAdmin webmaster@localhost\n\
    DocumentRoot /var/www/html\n\
\n\
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

# Copy .htaccess for URL rewriting (伪静态)
COPY addon/.htaccess /var/www/html/cgi-bin/.htaccess

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

EXPOSE 80

CMD ["apachectl", "-D", "FOREGROUND"]
