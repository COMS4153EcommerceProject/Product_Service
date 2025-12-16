CREATE TABLE IF NOT EXISTS inventory (
  inventory_id CHAR(36) PRIMARY KEY,
  product_id   CHAR(36) NOT NULL,
  quantity     INT NOT NULL,
  location     VARCHAR(100),
  updated_at   DATETIME NOT NULL,
  FOREIGN KEY (product_id) REFERENCES products(product_id)
);

INSERT INTO inventory
(inventory_id, product_id, quantity, location, updated_at)
VALUES
(
  'cccccccc-cccc-cccc-cccc-cccccccccccc',
  'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
  100,
  'Warehouse A',
  NOW()
);
