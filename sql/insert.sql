-- Passwords are all 'Admin123'
-- Hash: $2b$12$NW9qH.DSfqvSMseb82Sci.arjJuL0AWkgk6.GuoVGw8BkvkK3w/Nm

INSERT INTO users (id, full_name, email, password_hash, role, is_active) VALUES
(1, 'Fichow Admin', 'admin@fichow.test', '$2b$12$NW9qH.DSfqvSMseb82Sci.arjJuL0AWkgk6.GuoVGw8BkvkK3w/Nm', 'ADMIN', TRUE),
(2, 'Ana Customer', 'ana@fichow.test', '$2b$12$NW9qH.DSfqvSMseb82Sci.arjJuL0AWkgk6.GuoVGw8BkvkK3w/Nm', 'CUSTOMER', TRUE),
(3, 'Luis Customer', 'luis@fichow.test', '$2b$12$NW9qH.DSfqvSMseb82Sci.arjJuL0AWkgk6.GuoVGw8BkvkK3w/Nm', 'CUSTOMER', TRUE),
(4, 'Maria Customer', 'maria@fichow.test', '$2b$12$NW9qH.DSfqvSMseb82Sci.arjJuL0AWkgk6.GuoVGw8BkvkK3w/Nm', 'CUSTOMER', TRUE);

INSERT INTO wallets (id, user_id, balance, currency) VALUES
(1, 1, 1000.00, 'PEN'),
(2, 2, 100.00, 'PEN'),
(3, 3, 100.00, 'PEN'),
(4, 4, 100.00, 'PEN');

INSERT INTO carts (id, user_id) VALUES
(1, 1),
(2, 2),
(3, 3),
(4, 4);

INSERT INTO products (id, name, description, price, stock, category, image_url, is_active) VALUES
(1, 'Fichow clásico', 'El clásico chaufa con pollo y huevo.', 15.00, 100, 'Platos Fuertes', 'https://via.placeholder.com/400x300.png?text=Fichow+Clasico', TRUE),
(2, 'Fichow especial', 'Chaufa con pollo, carne, chancho y langostinos.', 22.00, 50, 'Platos Fuertes', 'https://via.placeholder.com/400x300.png?text=Fichow+Especial', TRUE),
(3, 'Fichow aeropuerto', 'Chaufa mezclado con tallarín saltado.', 20.00, 80, 'Platos Fuertes', 'https://via.placeholder.com/400x300.png?text=Fichow+Aeropuerto', TRUE),
(4, 'Fichow familiar', 'Porción gigante de Fichow clásico para toda la familia.', 45.00, 30, 'Para Compartir', 'https://via.placeholder.com/400x300.png?text=Fichow+Familiar', TRUE),
(5, 'Wantán frito', 'Porción de 6 unidades de wantán frito con salsa de tamarindo.', 8.00, 200, 'Entradas', 'https://via.placeholder.com/400x300.png?text=Wantan+Frito', TRUE),
(6, 'Inka Kola personal', 'Gaseosa Inka Kola 500ml.', 4.00, 300, 'Bebidas', 'https://via.placeholder.com/400x300.png?text=Inka+Kola', TRUE),
(7, 'Combo Fichow + bebida', 'Un Fichow clásico más una Inka Kola personal.', 18.00, 150, 'Combos', 'https://via.placeholder.com/400x300.png?text=Combo+Fichow', TRUE),
(8, 'Combo familiar Fichow', 'Un Fichow familiar, 12 wantanes y 1 Gaseosa 1.5L.', 55.00, 40, 'Combos', 'https://via.placeholder.com/400x300.png?text=Combo+Familiar', TRUE);

INSERT INTO coupons (id, code, discount_type, discount_value, max_uses, used_count, min_purchase_amount, is_active) VALUES
(1, 'FICHOW10', 'PERCENTAGE', 10.00, 100, 1, 20.00, TRUE),
(2, 'BIENVENIDO5', 'FIXED', 5.00, 500, 1, 15.00, TRUE),
(3, 'FAMILIAR15', 'PERCENTAGE', 15.00, 50, 1, 40.00, TRUE);

INSERT INTO orders (id, user_id, coupon_id, subtotal, discount_amount, total_amount, status) VALUES
(1, 2, 1, 45.00, 4.50, 40.50, 'DELIVERED'),
(2, 3, 2, 22.00, 5.00, 17.00, 'PAID'),
(3, 4, 3, 55.00, 8.25, 46.75, 'CREATED');

INSERT INTO order_items (id, order_id, product_id, product_name, quantity, unit_price, subtotal) VALUES
(1, 1, 4, 'Fichow familiar', 1, 45.00, 45.00),
(2, 2, 2, 'Fichow especial', 1, 22.00, 22.00),
(3, 3, 8, 'Combo familiar Fichow', 1, 55.00, 55.00);

-- Initial Top Ups and Purchases
INSERT INTO transactions (id, user_id, wallet_id, order_id, type, amount, balance_before, balance_after, description) VALUES
(1, 2, 2, NULL, 'TOP_UP', 140.50, 0.00, 140.50, 'Initial Top Up'),
(2, 2, 2, 1, 'PURCHASE', 40.50, 140.50, 100.00, 'Order #1 Payment'),

(3, 3, 3, NULL, 'TOP_UP', 117.00, 0.00, 117.00, 'Initial Top Up'),
(4, 3, 3, 2, 'PURCHASE', 17.00, 117.00, 100.00, 'Order #2 Payment'),

(5, 4, 4, NULL, 'TOP_UP', 146.75, 0.00, 146.75, 'Initial Top Up'),
(6, 4, 4, 3, 'PURCHASE', 46.75, 146.75, 100.00, 'Order #3 Payment');

INSERT INTO coupon_usages (id, coupon_id, user_id, order_id) VALUES
(1, 1, 2, 1),
(2, 2, 3, 2),
(3, 3, 4, 3);

SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));
SELECT setval('wallets_id_seq', (SELECT MAX(id) FROM wallets));
SELECT setval('carts_id_seq', (SELECT MAX(id) FROM carts));
SELECT setval('products_id_seq', (SELECT MAX(id) FROM products));
SELECT setval('coupons_id_seq', (SELECT MAX(id) FROM coupons));
SELECT setval('orders_id_seq', (SELECT MAX(id) FROM orders));
SELECT setval('order_items_id_seq', (SELECT MAX(id) FROM order_items));
SELECT setval('transactions_id_seq', (SELECT MAX(id) FROM transactions));
SELECT setval('coupon_usages_id_seq', (SELECT MAX(id) FROM coupon_usages));
