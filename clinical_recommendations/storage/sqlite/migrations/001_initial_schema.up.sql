/*
 * There are few issues with sqlc and sqlite that is 
 * making it harder than it should.
 * See: https://github.com/sqlc-dev/sqlc-gen-python/issues/57
*/


PRAGMA journal_mode = WAL;
PRAGMA busy_timeout = 5000;

CREATE TABLE IF NOT EXISTS recommendations (
    recommendation_id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    recommendation TEXT NOT NULL,
    timestamp DATETIME NOT NULL
);

-- Index on recommendation_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_recommendations_recommendation_id ON recommendations(recommendation_id);
