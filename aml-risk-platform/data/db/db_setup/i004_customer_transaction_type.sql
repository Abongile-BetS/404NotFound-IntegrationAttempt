INSERT INTO public.customer_transaction_type
(
    transaction_type_name,
    description
)
VALUES
(
    'Cash Deposit',
    'Customer deposits funds using cash.'
),
(
    'EFT Deposit',
    'Customer deposits funds via electronic funds transfer.'
),
(
    'Credit Card Deposit',
    'Customer deposits using a credit or debit card.'
),
(
    'Online Deposit',
    'Customer deposits through an online banking channel.'
),
(
    'Bank Deposit',
    'Customer deposits directly into a bank account.'
),
(
    'Wallet Deposit',
    'Customer deposits via a digital wallet provider.'
),
(
    'Mobile Money Deposit',
    'Customer deposits via a mobile money platform.'
),
(
    'Cash Withdrawal',
    'Customer withdraws funds as cash.'
),
(
    'EFT Withdrawal',
    'Customer withdraws funds via electronic funds transfer.'
),
(
    'Online Withdrawal',
    'Customer withdraws through an online banking channel.'
),
(
    'Instant Money Withdrawal',
    'Customer withdraws using an instant money service.'
),
(
    'eWallet Withdrawal',
    'Customer withdraws to an electronic wallet.'
),
(
    'Cash Send Withdrawal',
    'Customer withdraws through a cash send service.'
),
(
    'Retail Withdrawal',
    'Customer withdraws at a participating retail outlet.'
),
(
    'Stake',
    'Stake placed by customer on a betting or gaming event.'
),
(
    'Stake Return',
    'Returned stake where the original bet was voided, cancelled or otherwise returned to the customer.'
),
(
    'Payout',
    'Payout made to the customer as a result of a winning bet or settled gaming activity.'
),
(
    'Refunded',
    'Refund issued to reverse a previous transaction or return customer funds.'
);