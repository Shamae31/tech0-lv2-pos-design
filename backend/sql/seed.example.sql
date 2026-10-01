-- 税率変更時は既存行を変更せず適用終了日時を設定し、新しい期間の行を追加します。
INSERT INTO tax_categories (category_code, category_name) VALUES ('REDUCED', '軽減税率'), ('STANDARD', '標準税率');
INSERT INTO tax_rates (tax_category_id, tax_rate, applicable_from) SELECT tax_category_id, 8.00, '2019-10-01 00:00:00' FROM tax_categories WHERE category_code='REDUCED';
INSERT INTO tax_rates (tax_category_id, tax_rate, applicable_from) SELECT tax_category_id, 10.00, '2019-10-01 00:00:00' FROM tax_categories WHERE category_code='STANDARD';
INSERT INTO products (product_code, product_name, current_unit_price, tax_category_id) SELECT '4900000000010', 'ミネラルウォーター', 120, tax_category_id FROM tax_categories WHERE category_code='REDUCED';
INSERT INTO products (product_code, product_name, current_unit_price, tax_category_id) SELECT '4900000000027', '食パン', 180, tax_category_id FROM tax_categories WHERE category_code='REDUCED';
INSERT INTO products (product_code, product_name, current_unit_price, tax_category_id) SELECT '4900000000034', '日用品', 300, tax_category_id FROM tax_categories WHERE category_code='STANDARD';
INSERT INTO members (member_id, name) VALUES ('M0001', 'テスト会員');
-- password_hash は backend/scripts/hash_password.py で生成してください。
-- INSERT INTO cashiers (cashier_id, password_hash, display_name) VALUES ('staff01', '<bcrypt hash>', '山田');
