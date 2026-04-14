11-04-2026

1. display all users,artist with profile and portfolio --- done
2. understand how the flow works --- done
3. send proposal to the client --- done
4. client accepts the proposal and sends money to escorw --- done

12-04-2026

1. Add payment integration
2. request view and management in artist side and client side

    1. view the request that the current artist have done annd taken
    2. update the status and upload the deliverables 
    3. pay to the artist when the payemnt is done 

        1. may add the messaging feature b/w the user and artist



# Flow of the order life cycle

                                    [REQUEST OPEN]
                                        ↓ (artist submits proposal)
                                    [PROPOSAL PENDING]
                                        ↓ (client accepts)
                                    [ORDER CREATED → PAYMENT_PENDING]
                                        ↓ (client pays)
                                    [IN_PROGRESS]
                                        ↓ (artist uploads preview)
                                    [SUBMITTED]
                                        ↓
                        ┌───────────────┬──────────────────┐
                        ↓               ↓                  ↓
                    [REVISION]      [APPROVED]         [DISPUTED]
                        ↓               ↓                  ↓
                    [IN_PROGRESS]   [COMPLETED]       [RESOLUTION]




                    CLIENT                SYSTEM                ARTIST
                    │                     │                     │
                    │ Create Request      │                     │
                    ├────────────────────>│                     │
                    │                     │                     │
                    │                     │  View Request       │
                    │                     │<────────────────────┤
                    │                     │                     │
                    │                     │  Submit Proposal    │
                    │                     │<────────────────────┤
                    │                     │                     │
                    │ Accept Proposal     │                     │
                    ├────────────────────>│ Create Order        │
                    │                     │-------------------->│
                    │                     │                     │
                    │ Pay                 │                     │
                    ├────────────────────>│                     │
                    │                     │  Start Work         │
                    │                     │<────────────────────┤
                    │                     │                     │
                    │                     │  Upload Preview     │
                    │                     │<────────────────────┤
                    │                     │                     │
                    │                     │  Submit Final       │
                    │                     │<────────────────────┤
                    │                     │                     │
                    │ Review              │                     │
                    ├───────────────┬─────┴──────────────┐      │
                    │               │                    │      │
                    Approve      Request Revision     Dispute   │
                    │               │                    │      │
                    ↓               ↓                    ↓      │
                    COMPLETED    IN_PROGRESS          DISPUTED  │