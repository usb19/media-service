# Assumptions, Constraints, and Edge Cases

## 🔑 General Assumptions
- All requests include a valid JWT `Authorization` header (`Bearer <token>`).
- JWT contains a `user_id` claim used as the partition key in DynamoDB.
- A dedicated S3 bucket (e.g., `media-bucket`) exists with proper permissions.
- DynamoDB and S3 metadata are always kept in sync.
- Multiple users can upload/download simultaneously.
- Presigned URLs expire within 5 minutes (300 seconds).

---

## 📤 Upload Lambda
**Purpose:** Generate presigned upload URL, validate metadata, and persist entry in DynamoDB.

### Constraints
- Max file size: **100 MB**
- Allowed MIME types: `image/jpeg`, `image/png`, `image/gif`, `image/webp`
- Filenames sanitized to remove unsafe characters

### Edge Cases
- ❌ Missing/invalid JWT → `400 BadRequestError`
- ❌ Missing `contentType` or `fileSize` → `400`
- ❌ Unsupported content type → `400`
- ❌ Invalid file size (≤0 or >100MB) → `400`
- ✅ Sanitizes filename for S3
- ✅ Optional metadata (`caption`, `tags`, `location`, `visibility`)
- ✅ Unique `mediaId` (UUID)
- ❌ DynamoDB insert failure → `500 InternalServiceError`

---

## 📋 List Lambda
**Purpose:** Fetch all user images with optional filters.

### Constraints
- Query by PK (`user#<id>`)
- GSI supports filtering by `createdAt` range

### Edge Cases
- ✅ No media found → empty array
- ✅ Filters: `createdAfter`, `createdBefore`, `status`, `mediaId`
- ❌ Invalid date filters → empty result/validation error
- ✅ DynamoDB pagination future-ready

---

## 👁️ View Lambda
**Purpose:** Generate presigned download URL for a mediaId.

### Constraints
- Requires `mediaId` in path params
- Only owner (`user_id`) can view
- Validates record exists before generating URL
- URL cached in DynamoDB (`cachedUrl`, `urlExpiry`)

### Edge Cases
- ❌ Missing `mediaId` → `400`
- ❌ Media not found → `404`
- ❌ Expired cached URL → regenerate
- ❌ S3 failure → `500`
- ✅ Visibility allows PUBLIC/PRIVATE support

---

## 🗑️ Delete Lambda
**Purpose:** Delete an image from both S3 and DynamoDB.

### Constraints
- Requires `mediaId`
- Only owner can delete
- Must remove from both S3 + DynamoDB

### Edge Cases
- ❌ Missing `mediaId` → `400`
- ❌ Media not found → `404`
- ✅ Idempotent: deletes DynamoDB even if S3 missing
- ❌ S3 delete failure → `500`
- ✅ Return success with deleted key

---

## 🔄 Status Update Lambda
**Purpose:** Process S3 `ObjectCreated` event and mark media status `COMPLETED`.

### Constraints
- Triggered only on successful PUT
- Key format: `<userId>/<mediaId>`

### Edge Cases
- ❌ No `Records` → return `200` with `"No records to process"`
- ❌ Invalid key format → error + `400`
- ❌ DynamoDB update failure → `500`
- ✅ Multiple records handled iteratively
- ✅ Idempotent (marking already COMPLETED is safe)

---

# ✅ Summary
- **Upload** → Validates metadata, creates DB entry, presigned upload URL.
- **List** → Retrieves media metadata with filters.
- **View** → Validates record, returns presigned download URL.
- **Delete** → Removes from both S3 and DynamoDB.
- **Status Update** → Marks media as COMPLETED after S3 event.
