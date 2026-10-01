-- Apply once to a database created with the earlier schema, before deploying the new API.
ALTER TABLE transactions ADD COLUMN request_id CHAR(36) NULL, ADD COLUMN request_hash CHAR(64) NULL;
CREATE UNIQUE INDEX uq_transactions_request_id ON transactions (request_id);
