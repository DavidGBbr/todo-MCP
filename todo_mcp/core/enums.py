from enum import Enum


class Status(str, Enum):
    to_do = "to_do"
    in_progress = "in_progress"
    blocked = "blocked"
    done = "done"


class Priority(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


class SortField(str, Enum):
    created_at = "created_at"
    updated_at = "updated_at"
    due_date = "due_date"
    priority = "priority"
    title = "title"


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"
