CREATE TABLE IF NOT EXISTS recommendations (
    id uuid PRIMARY KEY,
    patient_id TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS recommendation_items (
    item_id SERIAL PRIMARY KEY,
    recommendation_id uuid NOT NULL REFERENCES recommendations(id) ON DELETE CASCADE,
    text TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_recommendation_items_recommendation_id ON recommendation_items(recommendation_id);
