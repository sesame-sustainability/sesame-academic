-- :name hourly_generation :many
SELECT
  *
FROM
  arp_generation
WHERE
  state = :state
  AND year >= :start_year
  AND year < (:end_year + 1)
;
