from fastapi import APIRouter, Request, HTTPException, status
from fastapi.responses import JSONResponse
from services.v2 import data_provider_v2
from models.v2.supplier import Supplier

supplier_router_v2 = APIRouter(tags=["v2.Suppliers"], prefix="/suppliers")


@supplier_router_v2.get("/{supplier_id}")
def read_supplier(supplier_id: int):
    supplier = data_provider_v2.fetch_supplier_pool().get_supplier(supplier_id)
    if supplier is None:
        raise HTTPException(
            status_code=404, detail=f"Supplier with id {supplier_id} not found"
        )
    return supplier


@supplier_router_v2.get("")
def read_suppliers(request: Request):
    suppliers = data_provider_v2.fetch_supplier_pool().get_suppliers()
    if suppliers is None:
        raise HTTPException(status_code=404, detail="Suppliers not found")
    return request.state.pagination.apply(suppliers)


@supplier_router_v2.get("/{supplier_id}/items")
def read_items_of_supplier(supplier_id: int, request: Request):
    supplier = data_provider_v2.fetch_supplier_pool().get_supplier(supplier_id)
    if supplier is None:
        raise HTTPException(
            status_code=404, detail=f"Supplier with id {supplier_id} not found"
        )

    items_for_supplier = data_provider_v2.fetch_item_pool().get_items_for_supplier(
        supplier_id
    )
    return request.state.pagination.apply(items_for_supplier)


@supplier_router_v2.post("")
def create_supplier(supplier: Supplier):
    created_supplier = data_provider_v2.fetch_supplier_pool().add_supplier(supplier)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=created_supplier.model_dump()
    )


@supplier_router_v2.put("/{supplier_id}")
def update_supplier(supplier_id: int, supplier: Supplier):
    existingSupplier = data_provider_v2.fetch_supplier_pool().is_supplier_archived(
        supplier_id
    )
    if existingSupplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    elif existingSupplier:
        raise HTTPException(status_code=400, detail="Supplier is archived")
    updated_supplier = data_provider_v2.fetch_supplier_pool().update_supplier(
        supplier_id, supplier
    )
    return updated_supplier


@supplier_router_v2.patch("/{supplier_id}")
def partial_update_supplier(supplier_id: int, supplier: dict):
    existing_supplier = data_provider_v2.fetch_supplier_pool().is_supplier_archived(
        supplier_id
    )
    if existing_supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    elif existing_supplier:
        raise HTTPException(status_code=400, detail="Supplier is archived")
    existing_supplier = data_provider_v2.fetch_supplier_pool().get_supplier(supplier_id)

    valid_keys = Supplier.model_fields.keys()
    update_data = {key: value for key, value in supplier.items() if key in valid_keys}

    for key, value in update_data.items():
        setattr(existing_supplier, key, value)

    partial_updated_supplier = data_provider_v2.fetch_supplier_pool().update_supplier(
        supplier_id, existing_supplier
    )
    return partial_updated_supplier


@supplier_router_v2.delete("/{supplier_id}")
def archive_supplier(supplier_id: int):
    existing_supplier = data_provider_v2.fetch_supplier_pool().is_supplier_archived(
        supplier_id
    )
    if existing_supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    elif existing_supplier:
        raise HTTPException(status_code=400, detail="Supplier is archived")

    updated_supplier = data_provider_v2.fetch_supplier_pool().archive_supplier(
        supplier_id
    )
    return updated_supplier


@supplier_router_v2.patch("/{supplier_id}/unarchive")
def unarchive_supplier(supplier_id: int):
    existing_supplier = data_provider_v2.fetch_supplier_pool().is_supplier_archived(
        supplier_id
    )
    if existing_supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    elif not existing_supplier:
        raise HTTPException(status_code=400, detail="Supplier is not archived")

    updated_supplier = data_provider_v2.fetch_supplier_pool().unarchive_supplier(
        supplier_id
    )
    return updated_supplier
