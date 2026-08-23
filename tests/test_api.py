import os
from pathlib import Path

os.environ["DATABASE_URL"] = "sqlite:///./test_warehouse.db"

from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


client = TestClient(app)


def setup_module() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def teardown_module() -> None:
    Base.metadata.drop_all(bind=engine)
    Path("test_warehouse.db").unlink(missing_ok=True)


def test_health() -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_and_read_product() -> None:
    category = client.post(
        "/api/v1/categories",
        json={"name": "数码设备", "slug": "digital-devices"},
    )
    assert category.status_code == 201

    product = client.post(
        "/api/v1/products",
        json={
            "category_id": category.json()["id"],
            "name": "iPhone 15",
            "slug": "iphone-15",
            "brand": "Apple",
        },
    )
    assert product.status_code == 201

    detail = client.get("/api/v1/products/iphone-15")
    assert detail.status_code == 200
    assert detail.json()["category"]["slug"] == "digital-devices"
    assert detail.json()["parts"] == []
