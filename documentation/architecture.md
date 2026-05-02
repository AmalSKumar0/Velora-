# Velora Architecture & Order Flow

## Overview
Velora is a digital art marketplace platform connecting Clients with Artists. The platform handles everything from initial request creation to proposals, secure payments (escrow), artwork delivery, revisions, and final approval.

## Order Life Cycle

```mermaid
flowchart TD
    A[REQUEST OPEN] -->|Artist submits proposal| B[PROPOSAL PENDING]
    B -->|Client accepts| C[ORDER CREATED]
    C -->|Client pays to Escrow| D[IN PROGRESS]
    D -->|Artist uploads preview| E[SUBMITTED]
    
    E --> F{Client Review}
    F -->|Request Changes| G[REVISION]
    F -->|Approve| H[APPROVED]
    F -->|Dispute| I[DISPUTED]
    
    G --> D
    H -->|System releases funds| J[COMPLETED]
    I --> K[RESOLUTION]
```

## Detailed Interaction Flow

```mermaid
sequenceDiagram
    actor Client
    participant System
    actor Artist

    Client->>System: Create Request
    System-->>Artist: View Request
    Artist->>System: Submit Proposal
    Client->>System: Accept Proposal
    System->>Artist: Create Order
    Client->>System: Pay (Escrow)
    System-->>Artist: Start Work
    Artist->>System: Upload Preview
    System-->>Client: Review Submission
    
    alt Approve
        Client->>System: Approve
        System->>Artist: Release Payment
        System-->>Client: Download Final File
    else Request Revision
        Client->>System: Request Revision
        System-->>Artist: Continue Work
    else Dispute
        Client->>System: Dispute
        System-->>System: Admin Resolution
    end
```


