"""Product service — isolated CRUD for catalog products."""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.app.models.product import Product
from backend.app.schemas.product import ProductCreate


def create_product(payload: ProductCreate, db: Session) -> Product:
    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def list_products(db: Session, active_only: bool = True) -> list[Product]:
    q = db.query(Product)
    if active_only:
        q = q.filter(Product.is_active == True)  # noqa: E712
    return q.all()


def get_product(product_id: int, db: Session) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found.")
    return product


def update_product(product_id: int, payload: ProductCreate, db: Session) -> Product:
    product = get_product(product_id, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product
