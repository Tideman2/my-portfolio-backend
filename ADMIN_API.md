# Admin API Specification — Portfolio Backend

**Audience:** the agent/developer building the admin dashboard.
**Status:** matches the backend on `feat/portfolio-redesign`.
**Base URL:** use the deployed API URL; for local development it is `http://localhost:5000` (the app reads `PORT`, default `5000`).

This document describes only what the backend actually implements. Do not assume extra endpoints, pagination, refresh tokens, or user management.

---

## 1. Conventions

### Authentication

All admin writes require a JWT access token:

```http
Authorization: Bearer <access_token>
```

Get the token from `POST /api/auth/login`. There is **no registration endpoint** and no refresh endpoint. When the token expires, log in again.

Public reads (profile, socials, skills, project groups, projects) do not require a token. This lets the public portfolio and the admin dashboard read the same data.

### Content types

| Situation | Content-Type |
|---|---|
| Normal JSON endpoints | `application/json` |
| `POST /api/projects/` | `multipart/form-data` |
| `PATCH /api/projects/<id>` with an image | `multipart/form-data` |
| `PATCH /api/projects/<id>` without an image | `application/json` (or form data) |

Do not manually set `Content-Type` when sending a `FormData` body; let the browser set the multipart boundary.

### Dates and numbers

- `date_of_birth` is an ISO date string: `YYYY-MM-DD`.
- `age` is computed by the backend on every read.
- `proficiency` is an integer from `1` to `5`.
- IDs are integers.

### Trailing slashes (important)

The collection endpoints are inconsistent, so use these exact paths:

| Path | Works? |
|---|---|
| `GET/POST /api/projects/` | Yes — use the trailing slash |
| `/api/projects` | Returns `308` redirect to `/api/projects/` |
| `GET/POST /api/project-groups` | Yes |
| `GET/POST /api/project-groups/` | Yes |
| `/me` and `/me/` | Both work |
| `/me/socials`, `/me/professional-skills`, `/me/technical-skills` | No trailing slash |
| `/me/socials/`, `/me/technical-skills/` | `404` |

### Error format

Validation errors:

```json
{
  "errors": {
    "field_name": ["Message about what is wrong."]
  }
}
```

Other errors:

```json
{ "error": "Human-readable message" }
```

Common status codes:

| Status | Meaning |
|---|---|
| `200` | Success |
| `201` | Created |
| `400` | Validation error, missing field, invalid group reference, or empty update |
| `401` | Missing/expired token, or bad login credentials |
| `403` | Malformed/invalid token |
| `404` | Resource not found |
| `409` | Conflicting group name/slug, or group still contains projects |

### List ordering

All list endpoints return records ordered by `id` ascending. There is no pagination; the dashboard receives the full list.

---

## 2. Endpoint quick reference

| Method | Path | Auth | Purpose |
|---|---|---|---|
| POST | `/api/auth/login` | No | Log in and get a token |
| POST | `/api/auth/verify` | Yes | Check whether a token is valid |
| GET | `/me` | No | Read the owner profile |
| PATCH | `/me` | Yes | Edit the owner profile |
| GET | `/me/socials` | No | List social links |
| POST | `/me/socials` | Yes | Add a social link |
| PATCH | `/me/socials/<id>` | Yes | Edit a social link |
| DELETE | `/me/socials/<id>` | Yes | Delete a social link |
| GET | `/me/professional-skills` | No | List professional skills |
| POST | `/me/professional-skills` | Yes | Add a professional skill |
| PATCH | `/me/professional-skills/<id>` | Yes | Edit a professional skill |
| DELETE | `/me/professional-skills/<id>` | Yes | Delete a professional skill |
| GET | `/me/technical-skills` | No | List technical skills |
| POST | `/me/technical-skills` | Yes | Add a technical skill |
| PATCH | `/me/technical-skills/<id>` | Yes | Edit a technical skill |
| DELETE | `/me/technical-skills/<id>` | Yes | Delete a technical skill |
| GET | `/api/project-groups` | No | List project groups |
| POST | `/api/project-groups` | Yes | Create a project group |
| PATCH | `/api/project-groups/<id>` | Yes | Rename a project group |
| DELETE | `/api/project-groups/<id>` | Yes | Delete a project group |
| GET | `/api/projects/` | No | List/filter projects |
| POST | `/api/projects/` | Yes | Create a project |
| PATCH | `/api/projects/<id>` | Yes | Edit a project |
| DELETE | `/api/projects/<id>` | Yes | Delete a project |

---

## 3. Authentication

### POST `/api/auth/login`

Request:

```json
{
  "username": "Admin",
  "password": "your-admin-password"
}
```

Validation: `username` is required; `password` is required and must be at least 6 characters.

Success `200`:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 1,
    "username": "Admin"
  }
}
```

Errors:

- `400` `{"errors": {...}}` — invalid/missing login payload.
- `400` `{"error": "Missing credentials"}` — empty username/password.
- `401` `{"error": "Invalid credentials"}` — wrong username or password.

The only account is the seeded `Admin` account. Do not build a registration screen.

### POST `/api/auth/verify`

Requires `Authorization: Bearer <token>`. No body.

Success `200`:

```json
{ "verified": true }
```

Errors:

- `401` missing header or expired token.
- `403` invalid token.

Use this on app startup to decide whether to show the dashboard or the login screen.

---

## 4. Profile (`/me`)

### GET `/me` (public)

Success `200`:

```json
{
  "name": "Roland",
  "date_of_birth": "2000-01-01",
  "age": 26,
  "country": "Ghana",
  "bio": "Backend developer..."
}
```

Any field can be `null` if it has not been filled in. `date_of_birth` is returned because the admin editor needs it; age is derived.

If the singleton profile row is missing, the backend returns:

```json
{ "error": "Profile not found" }
```

with status `404`. In a migrated database the row is seeded automatically.

### PATCH `/me`

Auth required. JSON body. Send only the fields being changed:

```json
{
  "name": "Roland",
  "date_of_birth": "2000-01-01",
  "country": "Ghana",
  "bio": "Backend developer..."
}
```

- All fields are optional.
- `date_of_birth` must match `YYYY-MM-DD` or the API returns `400`.
- `null` is not accepted for these fields. Omit a field to leave it unchanged.
- An empty `{}` body returns `200` with the unchanged profile.

Success `200`: the full profile object, same shape as `GET /me`.

Errors:

- `400` `{"errors": {...}}` — invalid date.
- `404` `{"error": "Profile not found"}`.
- `401`/`403` — auth failure.

There is no profile-picture, email, or phone field. Social links live in `/me/socials`.

---

## 5. Social links (`/me/socials`)

### Shape

```json
{
  "id": 1,
  "platform_name": "LinkedIn",
  "url": "https://www.linkedin.com/in/roland"
}
```

### GET `/me/socials` (public)

Returns an array, ordered by `id`. Empty array when there are none.

### POST `/me/socials`

Auth required. JSON:

```json
{
  "platform_name": "GitHub",
  "url": "https://github.com/roland"
}
```

Both fields are required non-empty strings. The backend does not validate that `url` is a well-formed URL, but the dashboard should.

Success `201`: the created social object.

### PATCH `/me/socials/<id>`

Auth required. JSON. Send any subset of `platform_name` and `url`.

Success `200`: the updated social object.
Errors: `400` validation, `404` unknown id, `401`/`403` auth.

### DELETE `/me/socials/<id>`

Auth required.

Success `200`:

```json
{ "message": "Social deleted" }
```

Errors: `404`, `401`/`403`.

---

## 6. Professional skills (`/me/professional-skills`)

### Shape

```json
{
  "id": 1,
  "name": "Communication",
  "description": "Explaining technical work to non-technical teammates.",
  "proficiency": 5
}
```

### GET `/me/professional-skills` (public)

Returns an array ordered by `id`.

### POST `/me/professional-skills`

Auth required. JSON:

```json
{
  "name": "Communication",
  "description": "Explaining technical work to non-technical teammates.",
  "proficiency": 5
}
```

All three fields are required. `proficiency` must be an integer `1`–`5`.

Success `201`: the created skill.
Errors: `400` validation, `401`/`403`.

### PATCH `/me/professional-skills/<id>`

Auth required. JSON. Send any subset of `name`, `description`, `proficiency`.
Success `200`: the updated skill.
Errors: `400`, `404`, `401`/`403`.

### DELETE `/me/professional-skills/<id>`

Auth required.
Success `200`: `{"message": "Skill deleted"}`
Errors: `404`, `401`/`403`.

---

## 7. Technical skills (`/me/technical-skills`)

Identical contract to professional skills, using the same fields and rules.

### GET `/me/technical-skills` (public)

Returns an array ordered by `id`.

### POST `/me/technical-skills`

Auth required. JSON:

```json
{
  "name": "HTML/CSS",
  "description": "Built responsive portfolio pages from scratch.",
  "proficiency": 4
}
```

Success `201`: the created skill.

### PATCH `/me/technical-skills/<id>`

Auth required. JSON. Send any subset of `name`, `description`, `proficiency`.

### DELETE `/me/technical-skills/<id>`

Auth required.
Success `200`: `{"message": "Skill deleted"}`

---

## 8. Project groups (`/api/project-groups`)

Groups classify projects, e.g. `Solo`, `Collab`, and anything the admin adds later. The migration seeds one group named `Uncategorized`.

### Shape

```json
{
  "id": 1,
  "name": "Solo",
  "slug": "solo"
}
```

- `slug` is generated from `name` on creation and then **never changes**, even when the group is renamed.
- `name` is unique.
- Deleting a group that still has projects is blocked.

### GET `/api/project-groups` (public)

Returns an array ordered by `id`.

### POST `/api/project-groups`

Auth required. JSON:

```json
{ "name": "Open Source Collaborations" }
```

`name` is required, 1–100 characters. Slug is generated, e.g. `open-source-collaborations`.

Success `201`: the created group.
Errors:
- `400` validation.
- `409` `{"error": "Group name already exists"}`.
- `409` `{"error": "Group slug already exists"}`.

### PATCH `/api/project-groups/<id>`

Auth required. JSON. Renaming requires `name`:

```json
{ "name": "Collaboration" }
```

`slug` is not accepted and does not change.

Success `200`: the updated group.
Errors: `400`, `404`, `409` duplicate name, `401`/`403`.

### DELETE `/api/project-groups/<id>`

Auth required.

Success `200`:

```json
{ "message": "Project group deleted" }
```

Errors:
- `404` unknown group.
- `409` `{"error": "Project group still has projects"}` — move the projects to another group first.

---

## 9. Projects (`/api/projects/`)

### Project response shape

```json
{
  "id": 1,
  "title": "Portfolio API",
  "image": "https://res.cloudinary.com/.../image.png",
  "stack": "Python, Flask, MySQL",
  "goal": "Serve portfolio data to the public site.",
  "github_url": "https://github.com/roland/portfolio-backend",
  "demo_url": "https://example.com"
}
```

- `image` may be `null`.
- The response **does not include `group_id` or any group object**. This is intentional and must not be expected by the dashboard. See the grouped-view strategy below.

### GET `/api/projects/` (public)

Optional query parameters:

| Parameter | Meaning |
|---|---|
| `group_id=<int>` | Return projects in that group |
| `group=<slug>` | Return projects in the group with that slug |

Examples:

```http
GET /api/projects/
GET /api/projects/?group_id=2
GET /api/projects/?group=solo
```

- If both are supplied, `group_id` wins.
- A non-numeric `group_id` returns `400` `{"error": "Invalid group_id"}`.
- An unknown `group_id` or slug returns `404` `{"error": "Project group not found"}`.
- Otherwise returns an array ordered by `id`.

### POST `/api/projects/`

Auth required. **`multipart/form-data`**, not JSON.

Fields:

| Field | Type | Required | Notes |
|---|---|---|---|
| `title` | string | Yes | 150 characters max at the database level |
| `stack` | string | Yes | e.g. `Python, Flask, MySQL` |
| `goal` | string | Yes | |
| `github_url` | string | Yes | |
| `demo_url` | string | Yes | |
| `group_id` | integer | Yes | Must reference an existing group |
| `image` | file | No | Uploaded to Cloudinary |

Example with `fetch`:

```js
const form = new FormData();
form.append("title", "Portfolio API");
form.append("stack", "Python, Flask, MySQL");
form.append("goal", "Serve portfolio data to the public site.");
form.append("github_url", "https://github.com/roland/portfolio-backend");
form.append("demo_url", "https://example.com");
form.append("group_id", String(groupId));
form.append("image", file); // optional File

await fetch(`${API_BASE}/api/projects/`, {
  method: "POST",
  headers: { Authorization: `Bearer ${token}` },
  body: form,
});
```

Success `201`:

```json
{ "message": "Project created" }
```

The created project is **not** returned. Re-fetch the project list after creating.

Errors:
- `400` `{"errors": {...}}` — missing/invalid fields, including a missing `group_id`.
- `400` `{"error": "Project group not found"}`.
- `401`/`403` — auth failure.

### PATCH `/api/projects/<id>`

Auth required. All fields are optional.

- Send `application/json` for text-only edits:
  ```json
  { "title": "New title", "group_id": 2 }
  ```
- Or send `multipart/form-data` when including a new `image` file.
- An empty payload returns `400` `{"error": "No fields to update"}`.
- `null` values are not accepted; omit a field to leave it unchanged.
- When `image` is supplied, the backend uploads the new image and deletes the old Cloudinary asset after a successful save.

Success `200`:

```json
{ "message": "Project updated" }
```

Errors:
- `400` validation or `{"error": "Project group not found"}`.
- `400` empty payload.
- `404` unknown project.
- `401`/`403`.

### DELETE `/api/projects/<id>`

Auth required. Deletes the project and its Cloudinary image, if any.

Success `200`:

```json
{ "message": "Project deleted" }
```

Errors: `404`, `401`/`403`.

---

## 10. Building grouped project views (important)

Because project responses intentionally omit group information, the dashboard should use one of these strategies:

### Recommended: fetch each group’s projects

1. `GET /api/project-groups`
2. For each group, `GET /api/projects/?group_id=<group.id>`
3. Render sections by group.

This gives you the group assignment without changing the public project response shape.

### Editing a project’s group

Since a project response has no `group_id`, keep the group context when the user opened the project from a group-filtered list. If you load all projects with `GET /api/projects/`, build a map of `project.id -> group.id` by collecting the per-group requests first, then merge that map into the UI.

The edit form can always send a new `group_id` to move the project.

### Creating a project

The create form must require a group selection and send `group_id`. Projects cannot be created without a group.

---

## 11. Suggested dashboard screens

- **Login** — `/api/auth/login`; store the token; verify with `/api/auth/verify`.
- **Profile editor** — `GET /me`, `PATCH /me`.
- **Social links** — `GET/POST/PATCH/DELETE /me/socials`.
- **Professional skills** — `GET/POST/PATCH/DELETE /me/professional-skills`.
- **Technical skills** — `GET/POST/PATCH/DELETE /me/technical-skills`.
- **Project groups** — `GET/POST/PATCH/DELETE /api/project-groups`; disable delete when the group has projects, or show the `409` message.
- **Projects** — `GET /api/projects/?group_id=<id>`, create with `multipart/form-data`, edit with JSON or multipart, delete.

---

## 12. TypeScript-friendly types

Response types (legacy data can be null, so string fields are typed defensively):

```ts
export interface Profile {
  name: string | null;
  date_of_birth: string | null; // YYYY-MM-DD
  age: number | null;
  country: string | null;
  bio: string | null;
}

export interface Social {
  id: number;
  platform_name: string;
  url: string;
}

export interface Skill {
  id: number;
  name: string;
  description: string;
  proficiency: number; // 1-5
}

export interface ProjectGroup {
  id: number;
  name: string;
  slug: string;
}

export interface Project {
  id: number;
  title: string;
  image: string | null;
  stack: string | null;
  goal: string | null;
  github_url: string | null;
  demo_url: string | null;
}

export interface LoginResponse {
  access_token: string;
  user: { id: number; username: string };
}

export type ApiError =
  | { error: string }
  | { errors: Record<string, string[]> };
```

Input types:

```ts
export type ProfileUpdate = Partial<{
  name: string;
  date_of_birth: string; // YYYY-MM-DD
  country: string;
  bio: string;
}>;

export interface SocialInput {
  platform_name: string;
  url: string;
}

export interface SkillInput {
  name: string;
  description: string;
  proficiency: number; // 1-5
}

export interface ProjectGroupInput {
  name: string;
}

export interface ProjectInput {
  title: string;
  stack: string;
  goal: string;
  github_url: string;
  demo_url: string;
  group_id: number;
  image?: File;
}

export type ProjectUpdate = Partial<Omit<ProjectInput, "image">> & {
  image?: File;
};
```

---

## 13. Explicitly not available

Do not build these; the backend does not support them:

- User registration or user management.
- Multiple admin accounts.
- Token refresh.
- Pagination, search, or sorting parameters on lists.
- A profile photo, email, phone, or CV field on `/me`.
- Project fields in the project response for its group.
- Listing contact-form messages (the mail endpoint only sends email).
- Deleting a project group that still contains projects.
- Changing a group’s slug after creation.
