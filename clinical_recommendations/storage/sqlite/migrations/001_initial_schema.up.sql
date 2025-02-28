PRAGMA journal_mode = WAL;
PRAGMA busy_timeout = 5000;

CREATE TABLE IF NOT EXISTS recommendations (
    recommendation_id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    recommendation TEXT NOT NULL,
    timestamp DATETIME NOT NULL
);

-- Index on recommendation_id for faster lookups
CREATE INDEX idx_recommendations_recommendation_id ON recommendations(recommendation_id);
