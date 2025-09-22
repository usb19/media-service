# Media Service – Enhancements & Future Improvements

This document outlines possible **enhancements** to the current architecture (Instagram-like service built with API Gateway, Lambda, S3, and DynamoDB). It covers **per-flow improvements**, **system-wide scalability**, **multi-region support**, and **CDN integration**.

---

## 1. Upload Flow

**Current:**  
- API Gateway → Upload Lambda validates JWT, metadata, and generates a presigned S3 URL.  
- Metadata is inserted into DynamoDB with status = `PENDING`.  
- User uploads image to S3.  

**Enhancements:**  
- **Virus scanning / content moderation:** Use an async Lambda triggered by S3 to scan images for malware, NSFW, or copyright issues.  
- **Duplicate detection:** Hash files (MD5/SHA256) before storing to detect duplicates.  
- **Chunked upload support:** For large files (>100MB), add multipart presigned upload.  
- **Retries & throttling:** Add retry policies via S3 TransferManager or API Gateway usage plans.  

---

## 2. Status Update Flow

**Current:**  
- S3 event → StatusUpdate Lambda updates DynamoDB record to `COMPLETED`.  

**Enhancements:**  
- **Dead Letter Queue (DLQ):** Attach DLQ (SQS) to capture failed events.  
- **Idempotency:** Ensure repeated S3 events don’t cause duplicate writes (check current status before updating).  
- **Notifications:** Trigger SNS/WebSocket to notify the user/app once upload is complete.  

---

## 3. List Flow

**Current:**  
- Query DynamoDB by PK (user) and optionally filter by status/mediaId.  
- Returns items to client.  

**Enhancements:**  
- **Global Secondary Indexes (GSIs):**  
  - `status` + `createdAt` → for filtering by recency.  
  - `tags` GSI → for search by hashtags.  
- **Pagination:** Support DynamoDB `LastEvaluatedKey` to return results in pages.  
- **Caching:** Cache recent results in Redis/DAX for faster feed rendering.  
- **Personalization:** Add ranking logic (sort by popularity, recency, engagement).  

---

## 4. View Flow

**Current:**  
- API Gateway → View Lambda validates JWT.  
- Generates presigned S3 `get_object` URL.  

**Enhancements:**  
- **Presigned URL caching:** Store and reuse short-lived presigned URLs in DynamoDB/Redis.  
- **CDN integration:** Replace presigned URLs with CloudFront signed cookies/URLs.  
- **Access policies:** Restrict visibility by `visibility = PUBLIC/PRIVATE/FRIENDS`.  
- **Audit logging:** Track how many times each media item was viewed.  

---

## 5. Delete Flow

**Current:**  
- API Gateway → Delete Lambda validates JWT.  
- Deletes object from S3 and metadata from DynamoDB.  

**Enhancements:**  
- **Soft delete:** Mark media as `DELETED` instead of physical delete for recovery.  
- **Background purge:** Schedule periodic cleanup of deleted objects.  
- **Audit logs:** Track who deleted and when (`deletedAt`, `deletedBy`).  
- **Retention policies:** Allow users to undo deletes within X days.  

---

## 6. Multi-Region Support

**Challenges solved:** High availability, disaster recovery, and global latency.  

**Enhancements:**  
- **S3 Cross-Region Replication (CRR):** Replicate images to multiple regions.  
- **DynamoDB Global Tables:** Multi-region write/read replication for metadata.  
- **API Gateway + Lambda regional deployment:** Deploy APIs in multiple regions.  
- **Global routing:** Use Route 53 latency-based routing or AWS Global Accelerator to direct users to nearest region.  

---

## 7. CDN Integration

**Why:** Reduce latency, cache frequently accessed images, secure delivery.  

**Enhancements:**  
- **CloudFront in front of S3:**  
  - Origin = S3 bucket.  
  - Signed URLs/cookies for private content.  
- **Presigned → CloudFront signed:** Replace direct presigned S3 URLs with CloudFront signed URLs.  
- **Caching strategy:**  
  - Static images cached in CDN for long TTL.  
  - Metadata served from API → no CDN needed.  
- **Edge Functions (Lambda@Edge/CloudFront Functions):** Modify requests, validate JWT at edge before serving media.  

---

## 8. System-Wide Enhancements

- **Monitoring & Logging:** Centralized logging in CloudWatch, metrics on S3/Lambda/DynamoDB.  
- **Tracing:** Use AWS X-Ray to trace request path.  
- **Security:**  
  - JWT expiration + refresh tokens.  
  - Fine-grained IAM policies for S3 access.  
- **Cost Optimization:** Lifecycle policies for old media → move to S3 Glacier.  
- **CI/CD:** Automate with SAM/CDK + GitHub Actions.  
- **Testing:** End-to-end Postman/Newman tests with mocked JWT tokens.  

---

✅ With these enhancements, the system will be:  
- **More reliable** (idempotency, retries, DLQs)  
- **Faster** (CDN, caching, GSIs, multi-region)  
- **More secure** (JWT, signed URLs, IAM)  
- **More scalable** (DynamoDB GSIs, S3 CRR, Route 53 routing)  
