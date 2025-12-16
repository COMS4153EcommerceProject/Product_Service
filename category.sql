CREATE TABLE IF NOT EXISTS categories (
  category_id CHAR(36) PRIMARY KEY,
  name        VARCHAR(100) NOT NULL,
  description TEXT,
  created_at  DATETIME NOT NULL,
  updated_at  DATETIME NOT NULL
);

INSERT INTO categories
(category_id, name, description, created_at, updated_at)
VALUES
(
  'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
  'Electronics',
  'Electronic devices and accessories',
  NOW(),
  NOW()
);
