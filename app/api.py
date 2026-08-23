from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models import AssemblyConnection, Category, Part, Product
from app.schemas import (
    CategoryCreate,
    CategoryRead,
    ConnectionCreate,
    ConnectionRead,
    PartCreate,
    PartRead,
    ProductCreate,
    ProductDetail,
    ProductRead,
)

router = APIRouter()


def commit_or_conflict(db: Session, detail: str) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=detail) from exc


@router.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/categories", response_model=list[CategoryRead], tags=["categories"])
def list_categories(db: Session = Depends(get_db)) -> list[Category]:
    return list(db.scalars(select(Category).order_by(Category.id)))


@router.post(
    "/categories", response_model=CategoryRead, status_code=status.HTTP_201_CREATED, tags=["categories"]
)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)) -> Category:
    category = Category(**payload.model_dump())
    db.add(category)
    commit_or_conflict(db, "分类名称或 slug 已存在")
    db.refresh(category)
    return category


@router.get("/products", response_model=list[ProductRead], tags=["products"])
def list_products(
    category_slug: str | None = Query(default=None),
    published_only: bool = Query(default=False),
    db: Session = Depends(get_db),
) -> list[Product]:
    statement = select(Product).order_by(Product.id)
    if category_slug:
        statement = statement.join(Product.category).where(Category.slug == category_slug)
    if published_only:
        statement = statement.where(Product.is_published.is_(True))
    return list(db.scalars(statement))


@router.post(
    "/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED, tags=["products"]
)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)) -> Product:
    if db.get(Category, payload.category_id) is None:
        raise HTTPException(status_code=404, detail="分类不存在")
    product = Product(**payload.model_dump())
    db.add(product)
    commit_or_conflict(db, "产品 slug 已存在")
    db.refresh(product)
    return product


@router.get("/products/{slug}", response_model=ProductDetail, tags=["products"])
def get_product(slug: str, db: Session = Depends(get_db)) -> Product:
    statement = (
        select(Product)
        .where(Product.slug == slug)
        .options(
            selectinload(Product.category),
            selectinload(Product.parts),
            selectinload(Product.connections),
        )
    )
    product = db.scalar(statement)
    if product is None:
        raise HTTPException(status_code=404, detail="产品不存在")
    return product


@router.post(
    "/products/{product_id}/parts",
    response_model=PartRead,
    status_code=status.HTTP_201_CREATED,
    tags=["parts"],
)
def create_part(product_id: int, payload: PartCreate, db: Session = Depends(get_db)) -> Part:
    if db.get(Product, product_id) is None:
        raise HTTPException(status_code=404, detail="产品不存在")
    part = Part(product_id=product_id, **payload.model_dump())
    db.add(part)
    commit_or_conflict(db, "该产品中零件 slug 已存在")
    db.refresh(part)
    return part


@router.post(
    "/products/{product_id}/connections",
    response_model=ConnectionRead,
    status_code=status.HTTP_201_CREATED,
    tags=["assembly"],
)
def create_connection(
    product_id: int, payload: ConnectionCreate, db: Session = Depends(get_db)
) -> AssemblyConnection:
    if payload.source_part_id == payload.target_part_id:
        raise HTTPException(status_code=422, detail="零件不能连接到自身")
    part_ids = set(
        db.scalars(
            select(Part.id).where(
                Part.product_id == product_id,
                Part.id.in_([payload.source_part_id, payload.target_part_id]),
            )
        )
    )
    if part_ids != {payload.source_part_id, payload.target_part_id}:
        raise HTTPException(status_code=422, detail="两个零件必须都属于当前产品")
    connection = AssemblyConnection(product_id=product_id, **payload.model_dump())
    db.add(connection)
    commit_or_conflict(db, "该装配关系已存在")
    db.refresh(connection)
    return connection
