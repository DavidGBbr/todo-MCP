from uuid import UUID


class TodoNotFoundError(Exception):
    def __init__(self, todo_id: UUID) -> None:
        self.todo_id = todo_id
        super().__init__(f"TODO_NOT_FOUND: {todo_id}")


class TodoAlreadyDeletedError(Exception):
    def __init__(self, todo_id: UUID) -> None:
        self.todo_id = todo_id
        super().__init__(f"TODO_ALREADY_DELETED: {todo_id}")


class TodoNotDeletedError(Exception):
    def __init__(self, todo_id: UUID) -> None:
        self.todo_id = todo_id
        super().__init__(f"TODO_NOT_DELETED: {todo_id}")


class PageOutOfRangeError(Exception):
    def __init__(self, page: int, page_size: int, total_pages: int) -> None:
        self.page = page
        self.page_size = page_size
        self.total_pages = total_pages
        super().__init__(
            "PAGE_OUT_OF_RANGE: "
            f"page={page}, page_size={page_size}, total_pages={total_pages}"
        )
