CREATE TABLE sent_email (
    id SERIAL PRIMARY KEY,
    from_email VARCHAR(120) NOT NULL,
    to_email VARCHAR(120) NOT NULL,
    subject VARCHAR(120) NOT NULL,
    message_body TEXT NOT NULL
);
