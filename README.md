# DealerOS-FullStack-Assessment

# DealerOS – Full-Stack Reconciliation System

A Django-based full-stack application designed to reconcile transaction records between two independent systems, identify data disagreements, and provide organization-level data isolation.

## 🚀 Project Overview

DealerOS helps organizations compare transaction data from System A and System B. It identifies missing records, duplicate entries, mismatched values, and inconsistencies in transaction dates and locations.

The application focuses on reliable data processing, accurate financial calculations, and secure multi-tenant data handling.

## ✨ Features

- **Data Reconciliation:** Compare records between System A and System B.
- **Reference Normalization:** Standardize inconsistent transaction references.
- **Financial Validation:** Compare System B values against System A's `total_value`.
- **Disagreement Detection:** Identify missing, duplicate, orphan, and mismatched records.
- **Split Transactions:** Support multiple entries that correctly add up to a transaction total.
- **Multi-Tenant Isolation:** Restrict organization data access based on location ownership.
- **Interactive Dashboard:** View, filter, and sort reconciliation results.
- **REST API:** Retrieve disagreement records using API endpoints.
- **Data Accuracy:** Handle missing and invalid amounts without silently converting them to zero.


## 📌 Future Improvements

- Add authentication and role-based access control.
- Improve dashboard analytics and reporting.
- Add CSV export functionality.
- Add comprehensive automated tenant-isolation tests.
- Improve import validation and error reporting.
- Add PostgreSQL support for production deployment.

## 👨‍💻 Author

**Vemulapally Sharan**


