with staged as (
    select * from {{ ref('stg_movies') }}
),

unnested as (
    select
        movie_id,
        title,
        vote_average,
        vote_count,
        popularity,
        genre_id
    from staged,
    unnest(genre_ids) as genre_id
)

select
    genre_id,
    count(distinct movie_id) as movie_count,
    round(avg(vote_average), 2) as avg_rating,
    round(avg(popularity), 2) as avg_popularity,
    sum(vote_count) as total_votes
from unnested
group by genre_id
order by avg_rating desc
