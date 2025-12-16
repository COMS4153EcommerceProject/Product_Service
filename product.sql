CREATE TABLE IF NOT EXISTS products (
  product_id  CHAR(36) PRIMARY KEY,
  name        VARCHAR(255) NOT NULL,
  description TEXT,
  price       DECIMAL(10,2) NOT NULL,
  rating      DECIMAL(3,2),
  category_id CHAR(36),
  created_at  DATETIME NOT NULL,
  updated_at  DATETIME NOT NULL,
  FOREIGN KEY (category_id) REFERENCES categories(category_id)
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
