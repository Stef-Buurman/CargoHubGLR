from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from services.v1 import data_provider, auth_provider

supplier_router = APIRouter(tags=["v1.Suppliers"], prefix="/suppliers")


@supplier_router.get("/{supplier_id}")
def read_supplier(supplier_id: int, api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    supplier = data_provider.fetch_supplier_pool().get_supplier(supplier_id)
    if supplier is None:
        raise HTTPException(
            status_code=404, detail=f"Supplier with id {supplier_id} not found"
        )
    return supplier


@supplier_router.get("")
def read_suppliers(api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    suppliers = data_provider.fetch_supplier_pool().get_suppliers()
    if suppliers is None:
        raise HTTPException(status_code=404, detail="Suppliers not found")
    return suppliers


@supplier_router.get("/{supplier_id}/items")
def read_items_of_supplier(
    supplier_id: int, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider.init()

    supplier = data_provider.fetch_supplier_pool().get_supplier(supplier_id)
    if supplier is None:
        raise HTTPException(
            status_code=404, detail=f"Supplier with id {supplier_id} not found"
        )

    items_for_supplier = data_provider.fetch_item_pool().get_items_for_supplier(
        supplier_id
    )
    return items_for_supplier


@supplier_router.post("")
def create_supplier(supplier: dict, api_key: str = Depends(auth_provider.get_api_key)):
    data_provider.init()
    existingSupplier = data_provider.fetch_supplier_pool().get_supplier(
        supplier.get("id")
    )
    if existingSupplier is not None:
        raise HTTPException(status_code=409, detail="Supplier already exists")
    added_supplier = data_provider.fetch_supplier_pool().add_supplier(supplier)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=added_supplier)


@supplier_router.put("/{supplier_id}")
def update_supplier(
    supplier_id: int, supplier: dict, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider.init()
    existingSupplier = data_provider.fetch_supplier_pool().get_supplier(supplier_id)
    if existingSupplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    updated_supplier = data_provider.fetch_supplier_pool().update_supplier(
        supplier_id, supplier
    )
    return updated_supplier


@supplier_router.delete("/{supplier_id}")
def delete_supplier(
    supplier_id: int, api_key: str = Depends(auth_provider.get_api_key)
):
    data_provider.init()
    supplier_pool = data_provider.fetch_supplier_pool()

    supplier = supplier_pool.get_supplier(supplier_id)
    if supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")

    supplier_pool.remove_supplier(supplier_id)
    supplier_pool.save()
    return {"message": "Supplier deleted successfully"}
