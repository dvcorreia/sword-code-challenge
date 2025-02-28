-- name: GetRecommendation :one
SELECT * FROM recommendations WHERE recommendation_id = ?;

-- name: InsertRecommendation :exec
INSERT INTO recommendations (
    recommendation_id,
    patient_id,
    recommendation,
    timestamp
) VALUES (?, ?, ?, ?);

