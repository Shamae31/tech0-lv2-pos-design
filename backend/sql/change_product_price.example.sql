-- Example procedure for changing a product price without losing its price history.
-- Replace these example values before running in a MySQL client.
START TRANSACTION;
SET @product_code = '4900000000010';
SET @new_unit_price = 130.00;
SELECT product_id, current_unit_price FROM products WHERE product_code = @product_code FOR UPDATE;
INSERT INTO product_price_histories (product_id, unit_price, applicable_from)
SELECT product_id, @new_unit_price, NOW() FROM products WHERE product_code = @product_code;
UPDATE products SET current_unit_price = @new_unit_price WHERE product_code = @product_code;
COMMIT;
