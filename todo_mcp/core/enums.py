from enum import StrEnum


class Status(StrEnum):
    to_do = "to_do"
    in_progress = "in_progress"
    blocked = "blocked"
    done = "done"


class Priority(StrEnum):
    high = "high"
    medium = "medium"
    low = "low"


class SortField(StrEnum):
    created_at = "created_at"
    updated_at = "updated_at"
    due_date = "due_date"
    priority = "priority"
    title_ = "title"


class SortOrder(StrEnum):
    asc = "asc"
    desc = "desc"
