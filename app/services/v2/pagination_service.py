from fastapi import Query


class Pagination:
    def __init__(self, page: int = Query(1, ge=1), items_per_page: int = 50):
        self.page = page
        self.items_per_page = items_per_page

    def apply(self, data: list):
        total = len(data)
        start_index = (self.page - 1) * self.items_per_page
        end_index = start_index + self.items_per_page

        paginated_data = data[start_index:end_index]
        return {
            "data": paginated_data,
            "pagination": {
                "total": total,
                "page": self.page,
                "items_per_page": self.items_per_page,
                "pages": (total + self.items_per_page - 1) // self.items_per_page,
            },
        }
