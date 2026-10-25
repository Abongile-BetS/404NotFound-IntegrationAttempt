# Behavioural features

`engine.features(transactions, as_of)` computes 7-day deposits/withdrawals/counts, 30-day deposits, previous 30-day deposits, growth percent (null without baseline), withdrawal/deposit ratio, mean deposit, dormancy, and row count. Uses transaction timestamps and a point-in-time reference; does not use future transactions. Does not yet calculate betting turnover or true deposit-withdrawal sequences.
