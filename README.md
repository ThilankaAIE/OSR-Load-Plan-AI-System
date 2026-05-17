# OSR Load Plan AI System

AI-powered logistics load plan automation system using OCR, AI extraction, and Excel generation.

---

# Project Overview

This project aims to automate the creation of logistics load plans that are currently processed manually using handwritten notes, shipment labels, operational paperwork, and Excel sheets.

The system is being developed as a real-world applied AI engineering project focused on warehouse and logistics operations.

---

# Business Problem

Current load plan workflows are:

- handwritten
- manually transferred into Excel
- time-consuming
- difficult to standardize
- prone to human error

Operational teams often process:
- container numbers
- shipment reference numbers
- order references
- deck/location references
- warehouse location codes
- shipment paperwork
- item labels/stickers

Manually capturing this information creates delays and data quality issues.

---

# Proposed AI Solution

The goal is to build an AI-powered workflow that can:

1. Accept images/photos of:
   - handwritten load plans
   - item labels
   - shipment paperwork
   - container labels

2. Extract text using OCR

3. Use AI to:
   - clean noisy OCR text
   - identify operational fields
   - structure extracted data

4. Generate:
   - structured JSON
   - automated Excel load plans

---

# MVP Scope (Phase 1)

Initial MVP focuses on:

- single-image OCR extraction
- AI cleanup of OCR text
- structured JSON output
- Excel export generation

The first version intentionally avoids:
- complex web apps
- authentication systems
- heavy infrastructure
- over-engineering

---

# Current Progress

## Environment & Infrastructure

- [x] Python setup
- [x] VS Code setup
- [x] Virtual environment setup
- [x] Git & GitHub integration
- [x] Tesseract OCR installation
- [x] OpenRouter API integration
- [x] First successful AI API call

---

# Planned Workflow

```text
Image
→ OCR Extraction
→ AI Cleanup
→ Structured JSON
→ Excel Load Plan