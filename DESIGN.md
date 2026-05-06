# Waste Management and Recycling System (WMRS) - Design Documentation

## 1. Problem Statement
Agruni Company Limited and similar waste management entities require a robust digital system to manage the complex flow of waste collection, staff assignments, and financial handovers in Rwanda. Manual tracking leads to inefficiencies and financial leaks.

## 2. Objectives
- **Operational Flow:** Represent the real chain of responsibility from Collector to Admin.
- **Financial Transparency:** Track every RWF from customer payment to company profit.
- **Sustainability:** Monitor recycling and disposal metrics.

## 3. User Roles (10 Roles Supported)
1. **Admin / Boss:** Full oversight, financial reports, system configuration.
2. **Secretary / Registrar:** Customer registration, service agreements, zone assignments.
3. **General Manager:** Operational strategy, cross-location monitoring, handover verification.
4. **Location Manager:** Zone-specific management, collector supervision, cash reception.
5. **Finance Officer:** Invoicing, payment verification, expense management.
6. **Supervisor:** Fleet management, driver assignments, route oversight.
7. **Collector:** Front-line collection, cash payment recording, manager handovers.
8. **Driver:** Waste transport, vehicle maintenance reporting.
9. **Customer:** Service requests, online payments, complaint submission.
10. **Sorting Staff:** Waste classification, recycling/disposal recording.

## 4. System Diagrams

### 4.1 Use Case Diagram
```mermaid
useCaseDiagram
    actor "Customer" as C
    actor "Collector" as CO
    actor "Location Manager" as LM
    actor "Secretary" as SEC
    actor "Admin" as AD
    actor "Driver" as DR
    actor "Supervisor" as SV

    package "WMRS System" {
        usecase "Register/Login" as UC1
        usecase "Request Collection" as UC2
        usecase "Record Payment" as UC3
        usecase "Handover Money" as UC4
        usecase "Verify Handover" as UC5
        usecase "Assign Collector/Zone" as UC6
        usecase "Dispatch Driver" as UC7
        usecase "View Profit/Loss" as UC8
    }

    C --> UC1
    C --> UC2
    SEC --> UC6
    CO --> UC3
    CO --> UC4
    LM --> UC5
    SV --> UC7
    AD --> UC8
```

### 4.2 Context Diagram (Level 0 DFD)
```mermaid
graph LR
    C[Customer] -- Payment/Request --> WMRS((WMRS System))
    WMRS -- Invoice/Status --> C
    CO[Collector] -- Cash Handover --> WMRS
    WMRS -- Commission Status --> CO
    AD[Admin] -- Strategy/Approval --> WMRS
    WMRS -- Profit/Loss Reports --> AD
```

### 4.3 Level 2 DFD: Payment & Money Handover Flow
```mermaid
graph TD
    C[Customer] -- Pays Cash --> CO[Collector]
    CO -- Records Payment --> P_DB[(Payments DB)]
    CO -- Money Handover --> LM[Location Manager]
    LM -- Verifies Cash --> MH_DB[(Handovers DB)]
    LM -- Forwards Funds --> GM[General Manager]
    GM -- Final Verification --> AD[Admin/Finance]
    AD -- Updates Ledger --> REVENUE[(Revenue Records)]
```

### 4.4 Sequence Diagram: Customer Payment to Boss
```mermaid
sequenceDiagram
    participant C as Customer
    participant CO as Collector
    participant LM as Location Manager
    participant GM as General Manager
    participant AD as Admin

    C->>CO: Pay Waste Fee (Cash)
    CO->>CO: Record Payment in Dashboard
    CO->>LM: Submit Money Handover Request
    LM->>LM: Verify Cash & Approve Handover
    LM->>GM: Submit Consolidated Handover
    GM->>GM: Verify Location Totals
    GM->>AD: Submit Daily/Weekly Revenue Report
    AD->>AD: Update Company Profit/Loss
```

### 4.5 Class Diagram (Major Models)
```mermaid
classDiagram
    class User {
        +String username
        +Role role
        +String phone
    }
    class Zone {
        +String name
        +User manager
    }
    class Subscription {
        +User customer
        +Zone zone
        +User collector
        +Decimal agreed_fee
    }
    class Invoice {
        +Subscription sub
        +Decimal amount
        +Status status
    }
    class Payment {
        +Invoice invoice
        +User collected_by
        +Decimal amount
    }
    class MoneyHandover {
        +User from_user
        +User to_user
        +Decimal amount
        +Status status
    }

    User "1" -- "0..*" Subscription
    Zone "1" -- "0..*" Subscription
    Subscription "1" -- "0..*" Invoice
    Invoice "1" -- "0..*" Payment
    Payment "0..*" -- "1" MoneyHandover
```

## 5. Operational Flow
1. **Registration:** Secretary registers Customer and assigns them to a **Zone** and **Collector**.
2. **Collection:** Collector visits Customer, marks waste collected, and records payment.
3. **Logistics:** Supervisor dispatches Driver to transport waste to recycling.
4. **Finance:** Collector hands over cash to Location Manager; Finance verifies invoices.
5. **Management:** Admin views real-time Profit/Loss and performance by location.
