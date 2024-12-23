FROM postgres:15

COPY init.sql /docker-entrypoint-initdb.d/
COPY postgresql.conf /etc/postgresql-custom/postgresql.conf
COPY pg_hba.conf /etc/postgresql-custom/pg_hba.conf

CMD ["postgres", "-c", "config_file=/etc/postgresql-custom/postgresql.conf"]
