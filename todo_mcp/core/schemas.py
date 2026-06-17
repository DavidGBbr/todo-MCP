from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from todo_mcp.core.enums import Priority, SortField, SortOrder, Status


class SubtaskInput(BaseModel):
    id: UUID | None = None
    title: str = Field(min_length=1, max_length=255)
    done: bool = False


class CreateTodoInput(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str
    status: Status
    priority: Priority
    due_date: date
    project: str | None = Field(default=None, max_length=255)
    tags: list[str] = Field(default_factory=list)
    assignee: str | None = Field(default=None, max_length=255)
    effort: str | None = Field(default=None, max_length=100)
    subtasks: list[SubtaskInput] = Field(default_factory=list)

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str]) -> list[str]:
        for tag in v:
            if len(tag) > 100:
                raise ValueError(f"Each tag must be at most 100 characters, got: {tag!r}")
        return v


class UpdateTodoInput(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: Status | None = None
    priority: Priority | None = None
    due_date: date | None = None
    project: str | None = Field(default=None, max_length=255)
    tags: list[str] | None = None
    assignee: str | None = Field(default=None, max_length=255)
    effort: str | None = Field(default=None, max_length=100)
    subtasks: list[SubtaskInput] | None = None

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return v
        for tag in v:
            if len(tag) > 100:
                raise ValueError(f"Each tag must be at most 100 characters, got: {tag!r}")
        return v


class ListTodosInput(BaseModel):
    status: Status | None = None
    priority: Priority | None = None
    project: str | None = None
    assignee: str | None = None
    tags: list[str] | None = None
    include_deleted: bool = False
    sort_by: SortField = SortField.created_at
    sort_order: SortOrder = SortOrder.asc
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class SubtaskOut(BaseModel):
    id: UUID
    todo_id: UUID
    title: str
    done: bool

    model_config = {"from_attributes": True}


class TodoOut(BaseModel):
    id: UUID
    title: str
    description: str
    status: Status
    priority: Priority
    due_date: date
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None
    project: str | None
    tags: list[str]
    assignee: str | None
    effort: str | None
    subtasks: list[SubtaskOut]

    model_config = {"from_attributes": True}


class ListTodosOut(BaseModel):
    items: list[TodoOut]
    total: int
    page: int
    page_size: int
    total_pages: int
