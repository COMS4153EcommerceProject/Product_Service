DROP TABLE IF EXISTS inventories;

CREATE TABLE inventories (
  inventory_id CHAR(36) PRIMARY KEY,
  product_id CHAR(36) NOT NULL,
  stock_quantity INT NOT NULL,
  warehouse_location VARCHAR(100),
  update_time DATETIME NOT NULL,
  created_at DATETIME NOT NULL,

  CONSTRAINT fk_inventory_product
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

INSERT INTO inventories
(inventory_id, product_id, stock_quantity, warehouse_location, update_time, created_at)
VALUES
(
  'cccccccc-cccc-cccc-cccc-cccccccccccc',
  'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
  100,
  'Warehouse A',
  NOW(),
  NOW()
);
