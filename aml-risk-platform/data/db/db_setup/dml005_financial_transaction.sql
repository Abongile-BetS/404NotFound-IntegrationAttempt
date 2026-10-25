UPDATE public.account
SET balance = ROUND(
    (500 + random() * 99500)::numeric,
    2
);