
# 📄 Technical Design Document — Scalable Image Upload & Metadata Service

## 1. Overview
We are designing a **service layer similar to Instagram’s image service**. This module supports:
- Uploading images with metadata.
- Listing images with filters.
- Viewing/downloading images.
- Deleting images.

---

## 2. Assumptions
- **Image size**: Maximum allowed = **100 MB** for standard uploads. Larger images (e.g., 500 MB) will use **multipart S3 upload**.
- **File types**: JPEG, PNG, WebP only.
- **User scale**: Millions of active users, 1000+ concurrent uploads/sec.
- **Latency requirement**: < 300 ms for metadata operations, < 1s for presigned URL generation.
- **Storage scale**: Petabyte-level image storage.
- **Consistency**: Eventual consistency acceptable for search, but strong consistency needed for metadata CRUD.
- **Authentication**: Handled via API Gateway + IAM/JWT.

---

## 3. Architecture Diagram

```
          ┌────────────┐
          │   Client   │
          └─────┬──────┘
                │
       ┌────────▼────────┐
       │   API Gateway   │
       └──────┬──────────┘
              │
      ┌───────▼───────────────────┐
      │         Lambda            │
      │  (Lightweight Control)    │
      └─────────┬─────────────────┘
                │
   ┌────────────┴────────────┐
   │                         │
   ▼                         ▼
Presigned URL          Metadata Ops
(S3 Direct Upload)     (DynamoDB CRUD)
   │                         │
   ▼                         ▼
 ┌───────┐             ┌────────────┐
 │   S3  │             │  DynamoDB  │
 │ Bucket│             │   Table    │
 └───────┘             └────────────┘
   │                         │
   │   ┌─────────────────┐   │
   └──►│  Event Triggers │◄──┘
       └───────┬─────────┘
               │
      ┌────────▼───────────┐
      │  SQS / EventBridge │
      └────────┬───────────┘
               │
       ┌───────▼───────────┐
       │  Worker Lambdas   │
       │ (Thumbnail/Scan)  │
       └───────┬───────────┘
               │
       ┌───────▼───────────┐
       │   Processed S3    │
       │   Bucket          │
       └────────┬──────────┘
                │
       ┌────────▼────────┐
       │   CloudFront    │
       │   (CDN)         │
       └─────────────────┘
```

---

## 4. Workflows

### 4.1 Upload Image
1. Client requests upload → API Gateway → Lambda.
2. Lambda generates **S3 presigned URL** with constraints:
   - Max size (100 MB)
   - Allowed MIME types
   - Expiry (5 min)
3. Client uploads image directly to S3.
4. Lambda/DynamoDB stores metadata:
   ```json
   {
     "PK": "userId#123",
     "SK": "imageId#uuid",
     "tags": ["beach", "sunset"],
     "uploadTime": "2025-09-19T12:00:00Z",
     "s3Key": "user123/uuid.jpg",
     "size": 4500000
   }
   ```
5. S3 triggers an event → SQS → Worker Lambda for async processing.

### 4.2 List Images
- Lambda queries DynamoDB.
- Supported filters:
  - By userId (partition key)
  - By tag/date (via GSI)

### 4.3 View/Download Image
- API Gateway → Lambda → returns **CloudFront-signed URL** (cached globally).

### 4.4 Delete Image
- API Gateway → Lambda deletes S3 object + DynamoDB entry.
- If one fails → scheduled cleanup job ensures consistency.

---

## 5. DynamoDB Schema

### Table: `Images`
- **PK**: `userId#<id>`
- **SK**: `imageId#<uuid>`
- **Attributes**: `tags`, `uploadTime`, `s3Key`, `size`

### Global Secondary Indexes (GSIs)
- **GSI1**: `tag` → Query by tag
- **GSI2**: `uploadDate` → Query by date range

---

## 6. Constraints & Enforcement

### File Size
- Lambda generates presigned URLs with `content-length-range` condition.
- Example (Python boto3):
  ```python
  s3.generate_presigned_post(
      Bucket="images-bucket",
      Key="user123/uuid.jpg",
      Fields={"Content-Type": "image/jpeg"},
      Conditions=[
          ["content-length-range", 0, 100 * 1024 * 1024],
          {"Content-Type": "image/jpeg"}
      ],
      ExpiresIn=300
  )
  ```

### Lambda Memory
- Images never pass through Lambda.
- Lambda only handles metadata + presigned URL generation.

### API Rate Limiting
- API Gateway quotas (e.g., 100 req/sec/user).
- WAF for IP-based throttling.

### Cost Controls
- S3 lifecycle rules → move old images to Glacier.
- DynamoDB TTL for expired metadata.

---

## 7. Bottlenecks & Mitigations

| Bottleneck                | Mitigation                                                                 |
|----------------------------|----------------------------------------------------------------------------|
| Lambda OOM on big files    | Presigned S3 upload (bypass Lambda).                                       |
| Hot partitions in DynamoDB | Partition key design = userId#date.                                        |
| Limited DynamoDB queries   | GSIs for tags, dates; OpenSearch for advanced search if needed.            |
| Traffic spikes             | Use SQS to buffer events; provisioned Lambda concurrency.                  |
| Latency in downloads       | CloudFront CDN.                                                           |
| Orphan metadata/files      | Event-driven cleanup + scheduled reconciliation jobs.                      |

---

## 8. Monitoring & Observability
- **CloudWatch**: Lambda execution time, errors.
- **X-Ray**: Traces across API Gateway → Lambda → DynamoDB.
- **S3 Access Logs**: Monitor direct uploads/downloads.
- **DynamoDB Streams**: Track metadata changes.

---

## 9. Development with LocalStack
- Run LocalStack in Docker Compose with S3, DynamoDB, SQS.
- Flask app simulating API Gateway + Lambda.
- Unit tests with Pytest + Moto/LocalStack.
- Swagger/OpenAPI documentation.

---

## 10. Future Enhancements
- Integrate OpenSearch for flexible search.
- Add ElastiCache/Redis for hot metadata cache.
- Introduce GraphQL layer for richer client queries.
- Add image recognition tags (ML integration).

---

## 11. Conclusion
This design ensures:
- **Scalability**: serverless + auto-scaling services.
- **Fault tolerance**: decoupling with SQS/EventBridge.
- **Security**: presigned URLs, IAM, WAF.
- **Cost efficiency**: pay-per-use, lifecycle policies.

By separating metadata (DynamoDB) and storage (S3), and using presigned URLs, the system avoids Lambda bottlenecks and scales horizontally to millions of requests.

