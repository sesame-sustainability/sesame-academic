-- :name yearly_generation :many
SELECT
  year,
  sum(co2) / NULLIF(sum(generation), 0) AS emission_intensity,
  state,
  status,
  type
FROM
  arp_generation
WHERE
  state = :state
  AND year >= :start_year
  AND year < (:end_year + 1)
GROUP BY
  year,
  state,
  status,
  type
;
