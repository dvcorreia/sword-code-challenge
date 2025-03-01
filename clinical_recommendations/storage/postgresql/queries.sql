-- name: GetRecommendationByID :many
SELECT r.id, r.patient_id, r.timestamp, ri.item_id, ri.text
FROM recommendations r
JOIN recommendation_items ri ON r.id = ri.recommendation_id
WHERE r.id = $1;

-- name: InsertRecommendation :exec
WITH recommendation_insert AS (
    INSERT INTO recommendations (
        id,
        patient_id,
        timestamp
    ) VALUES ($1, $2, $3)
)
INSERT INTO recommendation_items (
    recommendation_id,
    text
) SELECT $1, unnest(@recommendations::text[]) as text;