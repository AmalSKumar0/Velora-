# Velora Features

Velora is a robust digital art marketplace platform with role-based dashboards and an integrated commission workflow.

## Role-Based Architecture
The platform is divided into three main roles:
- **Clients**: Users who can post artwork requests, review artist proposals, fund orders, and review delivered artwork.
- **Artists**: Users who have dedicated profiles, can showcase their portfolios, discover client requests, submit proposals, and upload deliverables.
- **Administrators**: Users with full oversight of the platform, including user management, financial reports, and dispute resolution.

## Core Workflows

### Commissions & Requests
- Clients can create detailed requests for custom artwork including budget limits, required tags, and reference images.
- Artists can browse open requests that match their skill tags and submit pricing proposals and delivery timelines.
- Clients can accept proposals, which automatically generates a formalized Order.

### Escrow Payment System
- Integrated with Razorpay to hold funds securely in escrow.
- When an order is created, the client pays the agreed-upon amount. The status changes to `held`.
- Funds are only `released` to the artist after the client reviews and explicitly approves the final artwork submission.

### Deliverable Tracking & Revisions
- Artists can upload preview files (with watermarks applied by the system).
- Clients can either approve the submission or request specific changes.
- The platform tracks revision counts and maintains the historical state of the order.
- Once approved, the original un-watermarked high-resolution file is unlocked for the client to download.

### Portfolios & Profiles
- Artists can configure their public display name, bio, and external portfolio links.
- Artists can upload and manage portfolio items with specific tags to attract relevant clients.
- Clients can browse through artists' past work and profiles before committing to a request.

### Admin Tools & Reporting
- Admins have access to high-level dashboards tracking user growth, revenue, and active orders.
- Admins can generate and download PDF global reports (using WeasyPrint).
- Admins can manage users, oversee global requests/orders, and handle payment disputes.
