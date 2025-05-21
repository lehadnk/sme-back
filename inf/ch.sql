CREATE TABLE stock_data
(
    ticker String,
    date Date32,
    open Float64,
    high Float64,
    low Float64,
    close Float64,
    adj_close Float64,
    volume Int32
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (ticker, date);

CREATE TABLE predictions
(
    ticker String,
    date Date,
    estimated_at DateTime,
    model_id String,
    close Float64
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (ticker, date, estimated_at);