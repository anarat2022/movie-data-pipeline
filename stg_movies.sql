with source as (
    select * from {{ source('raw', 'movies_raw') }}
),

deduped as (
    select *,
        row_number() over (partition by id order by loaded_at desc) as rn
    from source
),

cleaned as (
    select
        id as movie_id,
        title,
        safe_cast(release_date as date) as release_date,
        genre_ids,
        vote_average,
        vote_count,
        popularity,
        overview,
        loaded_at
    from deduped
    where title is not null
      and rn = 1
)

select * from cleaned
