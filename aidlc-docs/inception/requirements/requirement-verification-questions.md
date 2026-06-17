# Requirements Verification Questions — todo-mcp

Please answer each question by filling in the letter choice after the `[Answer]:` tag.  
If none of the options match, choose the last option (Other) and describe your preference.  
Let me know when you're done.

---

## Question 1
What storage backend should the MCP server use to persist todo items?

A) In-memory only (data lost on restart — simplest, good for prototyping)
B) JSON file on disk (lightweight, no external dependencies)
C) SQLite database (structured queries, no server needed, good for production)
D) PostgreSQL / external relational DB (full-featured, requires separate container)
X) Other (please describe after [Answer]: tag below)

[Answer]: option D

---

## Question 2
Should the MCP server support multi-user / shared lists with real authentication, or is it single-user (no auth)?

A) Single-user — no authentication needed
B) Multi-user with simple API key / token authentication
C) Multi-user with full OAuth2 / identity provider integration
X) Other (please describe after [Answer]: tag below)

[Answer]: option A

---

## Question 3
Which MCP transport should the server expose?

A) stdio only (used when Claude Desktop or an MCP client runs the server as a subprocess)
B) HTTP/SSE only (used when the server runs as a standalone service)
C) Both stdio and HTTP/SSE
X) Other (please describe after [Answer]: tag below)

[Answer]: option A

---

## Question 4
For subtasks: should they support arbitrary nesting depth (subtasks of subtasks), or just one level of nesting?

A) One level only (a task can have subtasks, but subtasks cannot have their own subtasks)
B) Arbitrary depth (full recursive nesting)
X) Other (please describe after [Answer]: tag below)

[Answer]: option A

---

## Question 5
Should the MCP expose search / filter / query capabilities as a tool (e.g. filter by status, priority, assignee, tag), or just basic CRUD operations?

A) Basic CRUD only (create, read, update, delete, list all)
B) CRUD plus filtering/search (filter by status, priority, project, tags, assignee, due date range)
C) CRUD plus filtering plus sorting and pagination
X) Other (please describe after [Answer]: tag below)

[Answer]: option C

---

## Question 6
Should completed or deleted tasks be permanently removed, or should there be a soft-delete / archive mechanism?

A) Hard delete — tasks are permanently removed
B) Soft delete / archive — tasks are hidden but recoverable
X) Other (please describe after [Answer]: tag below)

[Answer]: option B

---

## Question 7
What level of input validation and error handling is expected?

A) Minimal — basic type checks, fail loudly on bad input
B) Standard — validate required fields, return structured error messages via MCP
C) Strict — full validation with detailed error codes and user-friendly messages
X) Other (please describe after [Answer]: tag below)

[Answer]: option B

---

## Question 8
Should the Docker image support hot-reload / development mode, or just a production-ready image?

A) Production image only
B) Production image + separate dev compose with hot-reload
X) Other (please describe after [Answer]: tag below)

[Answer]: option B

---

## Question: Security Extensions
Should security extension rules be enforced for this project?

A) Yes — enforce all SECURITY rules as blocking constraints (recommended for production-grade applications)
B) No — skip all SECURITY rules (suitable for PoCs, prototypes, and experimental projects)
X) Other (please describe after [Answer]: tag below)

[Answer]: option A

---

## Question: Property-Based Testing Extension
Should property-based testing (PBT) rules be enforced for this project?

A) Yes — enforce all PBT rules as blocking constraints (recommended for projects with business logic, data transformations, serialization, or stateful components)
B) Partial — enforce PBT rules only for pure functions and serialization round-trips
C) No — skip all PBT rules (suitable for simple CRUD applications or thin integration layers)
X) Other (please describe after [Answer]: tag below)

[Answer]: option B
