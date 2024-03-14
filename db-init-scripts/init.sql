CREATE TABLE IF NOT EXISTS jobs (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(255) UNIQUE,
    link VARCHAR(255),
    title VARCHAR(255),
    company VARCHAR(255),
    date_posted VARCHAR(255),
    location VARCHAR(255),
    description TEXT,
    timestamp TIMESTAMP DEFAULT current_timestamp
);

CREATE TABLE IF NOT EXISTS feedback (
    id SERIAL PRIMARY KEY,
    rating INT NOT NULL,
    feedback TEXT NOT NULL,
    email VARCHAR(255) NOT NULL,
    date TIMESTAMP NOT NULL
);
