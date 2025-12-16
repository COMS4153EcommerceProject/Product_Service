DROP TABLE IF EXISTS products;

CREATE TABLE products (
  product_id CHAR(36) PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
  rating DECIMAL(3,2) CHECK (rating >= 0 AND rating <= 5),
  category_id CHAR(36),
  inventory_id CHAR(36),
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    ON UPDATE CURRENT_TIMESTAMP
);

INSERT INTO products
(product_id, name, description, price, rating, category_id, created_at, updated_at)
VALUES
(
  'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
  'Wireless Mouse',
  'Ergonomic wireless mouse',
  29.99,
  4.5,
  'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
  NOW(),
  NOW()
);
