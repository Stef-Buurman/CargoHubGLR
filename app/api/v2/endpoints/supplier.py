from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from services.v2.pagination_service import Pagination
from services.v2 import data_provider_v2, auth_provider_v2
from models.v2.supplier import Supplier

supplier_router_v2 = APIRouter()


@supplier_router_v2.get("/{supplier_id}")
def read_supplier(
    supplier_id: int, api_key: str = Depends(auth_provider_v2.get_api_key)
):
    data_provider_v2.init()
    supplier = data_provider_v2.fetch_supplier_pool().get_supplier(supplier_id)
    if supplier is None:
        raise HTTPException(
            status_code=404, detail=f"Supplier with id {supplier_id} not found"
        )
    return supplier


@supplier_router_v2.get("/")
def read_suppliers(
    pagination: Pagination = Depends(),
    api_key: str = Depends(auth_provider_v2.get_api_key),
):
    data_provider_v2.init()
    suppliers = data_provider_v2.fetch_supplier_pool().get_suppliers()
    if suppliers is None:
        raise HTTPException(status_code=404, detail="Suppliers not found")
    return pagination.apply(suppliers)


@supplier_router_v2.get("/{supplier_id}/items")
def read_items_of_supplier(
    supplier_id: int,
    pagination: Pagination = Depends(),
    api_key: str = Depends(auth_provider_v2.get_api_key),
):
    data_provider_v2.init()

    supplier = data_provider_v2.fetch_supplier_pool().get_supplier(supplier_id)
    if supplier is None:
        raise HTTPException(
            status_code=404, detail=f"Supplier with id {supplier_id} not found"
        )

    items_for_supplier = data_provider_v2.fetch_item_pool().get_items_for_supplier(
        supplier_id
    )
    return pagination.apply(items_for_supplier)


@supplier_router_v2.post("/")
def create_supplier(
    supplier: Supplier, api_key: str = Depends(auth_provider_v2.get_api_key)
):
    data_provider_v2.init()
    created_supplier = data_provider_v2.fetch_supplier_pool().add_supplier(supplier)
    return JSONResponse(
        status_code=status.HTTP_201_CREATED, content=created_supplier.model_dump()
    )


@supplier_router_v2.put("/{supplier_id}")
def update_supplier(
    supplier_id: int,
    supplier: Supplier,
    api_key: str = Depends(auth_provider_v2.get_api_key),
):
    data_provider_v2.init()
    existingSupplier = data_provider_v2.fetch_supplier_pool().get_supplier(supplier_id)
    if existingSupplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    updated_supplier = data_provider_v2.fetch_supplier_pool().update_supplier(
        supplier_id, supplier
    )
    return updated_supplier


@supplier_router_v2.patch("/{supplier_id}")
def partial_update_supplier(
    supplier_id: int,
    supplier: dict,
    api_key: str = Depends(auth_provider_v2.get_api_key),
):
    data_provider_v2.init()
    existing_supplier = data_provider_v2.fetch_supplier_pool().get_supplier(supplier_id)
    if existing_supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")

    valid_keys = Supplier.model_fields.keys()
    update_data = {key: value for key, value in supplier.items() if key in valid_keys}

    for key, value in update_data.items():
        setattr(existing_supplier, key, value)

    partial_updated_supplier = data_provider_v2.fetch_supplier_pool().update_supplier(
        supplier_id, existing_supplier
    )
    return partial_updated_supplier


@supplier_router_v2.delete("/{supplier_id}")
def delete_supplier(
    supplier_id: int, api_key: str = Depends(auth_provider_v2.get_api_key)
):
    data_provider_v2.init()
    supplier_pool = data_provider_v2.fetch_supplier_pool()

    supplier = supplier_pool.get_supplier(supplier_id)
    if supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")

    supplier_pool.remove_supplier(supplier_id)
    return {"message": "Supplier deleted successfully"}
