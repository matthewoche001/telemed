# OHMS — Agent Reference Document
# Online Hospital Management System with CNN-based CT Scan Diagnostics
# Veritas University Abuja | Dept. of Software Engineering
# Student: Ameh Oche Matthew | Matric: VUG/SEN/22/8454
# Supervisor: Mr. Usoh Ikouwem | HOD: Dr. Abisoye Opeyemi

---

## AGENT INSTRUCTIONS

This document is the single source of truth for this project.
- Stack: Django (backend), plain HTML/CSS/JS (frontend), MySQL (database), TensorFlow or PyTorch (AI)
- Never use SQLite. Always use MySQL.
- Never use React unless explicitly instructed.
- The CNN diagnostic module lives in a dedicated Django app called `diagnostics`.
- All FR numbers below (FR-01 through FR-15) are the canonical requirement IDs. Reference them in code comments.
- Build in the order listed in Section 7 (Build Order). Do not skip ahead.

---

## 1. TECH STACK

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, JavaScript (no framework) |
| Backend | Python — Django (preferred over Flask for built-in auth, ORM, admin panel) |
| API | REST, JSON responses |
| Authentication | Django session-based auth + role-based access control middleware |
| AI/ML | TensorFlow or PyTorch — CNN binary classifier |
| Database | MySQL |
| File Storage | Local filesystem — /media/ct_scans/original/ and /media/ct_scans/preprocessed/ |

---

## 2. ARCHITECTURE

Three-tier architecture:

```
[Browser — HTML/CSS/JS]
        |
        | HTTP / REST
        |
[Django Backend — Views, URLs, Auth, RBAC, REST API]
        |
    [Diagnostics App — CNN Service]
        |
    [MySQL Database]    [File Storage — /media/]
```

The CNN model is NOT a separate microservice. It runs as a Python module (`diagnostics/cnn_service.py`) called synchronously (or as a background task) from within Django. The model is loaded once at startup and reused per request.

---

## 3. SYSTEM ACTORS

### 3.1 Doctor
| Responsibility | Detail |
|---|---|
| View patient records | Full medical history, past diagnostics, prescriptions, imaging |
| Manage appointments | Approve, reschedule, cancel. View daily schedule. |
| Conduct consultations | Remote video or chat. Full record access during session. |
| Review AI CT results | Access CNN output on diagnostic dashboard alongside patient history |
| Validate AI output | Approve, modify, or annotate CNN findings before report is finalized |
| Issue prescriptions | Generate digital prescriptions stored to patient record |
| Update medical records | Add clinical notes, update treatment plans, record diagnoses |

### 3.2 Nurse
| Responsibility | Detail |
|---|---|
| Update patient vitals | Record BP, temperature, pulse during ward rounds |
| Monitor ongoing treatment | Track progress, flag adverse reactions to doctor |
| Alert doctors | Send critical change alerts through the system |
| Assist CT scan upload | Help patients upload CT images, verify patient identity before submission |
| Schedule tests | Coordinate lab and imaging bookings with lab technicians |
| Patient communication | Send reminders, prep instructions, follow-up info |

### 3.3 Patient
| Responsibility | Detail |
|---|---|
| Register account | Create account with demographic and contact details |
| Book appointments | Select doctor, specialty, preferred time slot |
| Upload CT scans | Submit cardiac CT scan images for AI analysis |
| Remote consultation | Connect with doctors via video or chat |
| View diagnostic results | Access AI-generated CT analysis and doctor-validated reports |
| Track consultation | View status, follow-up dates, messages from staff |

### 3.4 Admin
| Responsibility | Detail |
|---|---|
| Manage user accounts | Create, update, suspend, delete all user types |
| Configure roles/permissions | Define what each role can access and modify |
| Monitor system performance | Track uptime, response times, error rates |
| View analytics and reports | Patient volume, diagnostic stats, AI accuracy, inventory |
| Oversee inventory | Track stock, approve reorders, manage suppliers |
| Review audit logs | Inspect all user activity and data access events |

### 3.5 Lab Technician
| Responsibility | Detail |
|---|---|
| Upload test results | Submit lab results into patient record |
| Manage sample tracking | Log sample receipt, processing status, result availability |
| Coordinate with doctors | Notify requesting doctors when results are ready |
| Assist CT scan submission | Support patients/nurses with CT uploads, verify patient linkage |

> GAP: Lab Technician is listed as an actor but is largely absent from Chapter 3 of the proposal. Their Django views, URLs, and permissions need to be explicitly defined during implementation.

---

## 4. FUNCTIONAL REQUIREMENTS

### 4.1 Core HMS

| ID | Requirement | Description |
|---|---|---|
| FR-01 | User Registration | Patients, doctors, nurses, radiologists, and admins create secure accounts. Role-based permissions assigned at signup. Patients self-register. Staff accounts created by Admin only. |
| FR-02 | Authentication | Secure login with unique credentials. Role-based access control restricts what each user can see and do. Session-based. |
| FR-03 | Appointment Booking | Patients book appointments online. Doctors and staff manage, approve, reschedule. Automated reminders sent. |
| FR-04 | Online Consultation | Patients consult doctors remotely via secure video or chat. Doctor has full patient record access during session. |
| FR-05 | Manage Consultation | Doctors issue digital prescriptions, stored in patient records, optionally shareable with pharmacies. |
| FR-06 | Update Patient Records | Authorized staff enter, update, and retrieve records: personal info, medical history, diagnostics, treatment plans. |

### 4.2 AI and Diagnostics

| ID | Requirement | Description |
|---|---|---|
| FR-07 | CT Scan Upload | Patients or staff securely upload CT scan images. System validates file format (DICOM, PNG, JPG) before processing. Reject all other formats with a clear error message. |
| FR-08 | AI CT Evaluation | CNN model automatically analyzes uploaded cardiac CT. Outputs probability score and binary class: Normal vs Abnormal. Target inference time: under 5 seconds. |
| FR-09 | AI Validation Dashboard | Doctors and radiologists review CNN results on a dedicated interface. Can approve, modify, or annotate before report is finalized. |

### 4.3 Operations and Administration

| ID | Requirement | Description |
|---|---|---|
| FR-10 | Staff Management | Admins create, update, deactivate staff accounts. Monitor performance and oversee workflows. |
| FR-11 | Inventory Tracking | Monitor stock of medical supplies, medications, equipment. Generate restock alerts to prevent shortages. |
| FR-12 | Reports and Analytics | Dashboards: appointments, diagnostics summary, patient demographics, AI accuracy metrics, resource utilization. |
| FR-13 | Notifications and Alerts | Real-time notifications: appointment reminders, critical diagnostic results, system events, AI result availability. |
| FR-14 | Data Backup and Recovery | Automatic scheduled backup of records and diagnostic results. Recovery procedures in case of data loss. |
| FR-15 | Record Storage | Centralized storage: demographics, medical history, diagnostic images, AI-generated reports, prescriptions. |

---

## 5. NON-FUNCTIONAL REQUIREMENTS

| Attribute | Requirement |
|---|---|
| Performance | CT scan AI result ≤ 5 seconds. Login, data retrieval, report generation ≤ 3 seconds under normal load. |
| Availability | 99% uptime. Auto-recovery from failures. |
| Security | Encrypted data transmission. RBAC enforced. HIPAA/GDPR compliance. Full audit logging of all events. |
| Scalability | Architecture supports growing users and data volume. Modular for future AI module additions. |
| Reliability | Data integrity at all times. No loss of patient records or diagnostic results under any failure. |
| Usability | Intuitive UI for all roles — doctors, nurses, admins, radiologists, patients — minimal training overhead. |
| Maintainability | Modular Django apps. Well-documented. Features can be updated without disrupting existing functionality. |
| Interoperability | Supports integration with external healthcare systems, lab information systems, imaging devices. |
| Auditability | All logins, data access, AI outputs logged. Admins can review for compliance. |

---

## 6. DATABASE SCHEMA

### Table: users
| Column | Type | Notes |
|---|---|---|
| id | INT PK AUTO_INCREMENT | |
| email | VARCHAR(255) UNIQUE | |
| password_hash | VARCHAR(255) | bcrypt |
| role | ENUM('doctor','nurse','patient','admin','lab_tech') | |
| full_name | VARCHAR(255) | |
| phone | VARCHAR(20) | |
| is_active | BOOLEAN | default true |
| created_at | DATETIME | |

### Table: patients
| Column | Type | Notes |
|---|---|---|
| id | INT PK | |
| user_id | INT FK → users.id | |
| date_of_birth | DATE | |
| gender | VARCHAR(10) | |
| blood_group | VARCHAR(5) | |
| address | TEXT | |
| emergency_contact | VARCHAR(255) | |
| medical_history | TEXT | |

### Table: appointments
| Column | Type | Notes |
|---|---|---|
| id | INT PK AUTO_INCREMENT | |
| patient_id | INT FK → users.id | |
| doctor_id | INT FK → users.id | |
| scheduled_at | DATETIME | |
| status | ENUM('pending','confirmed','cancelled','completed') | |
| notes | TEXT | |
| created_at | DATETIME | |

### Table: ct_scans
| Column | Type | Notes |
|---|---|---|
| id | INT PK AUTO_INCREMENT | |
| patient_id | INT FK → users.id | |
| uploaded_by | INT FK → users.id | nurse or patient |
| original_path | VARCHAR(500) | /media/ct_scans/original/ |
| preprocessed_path | VARCHAR(500) | /media/ct_scans/preprocessed/ |
| upload_timestamp | DATETIME | |
| status | ENUM('uploaded','preprocessing','analyzed','validated','failed') | |

### Table: ai_results
| Column | Type | Notes |
|---|---|---|
| id | INT PK AUTO_INCREMENT | |
| scan_id | INT FK → ct_scans.id | |
| predicted_class | ENUM('normal','abnormal') | |
| confidence_score | FLOAT | 0.0 to 1.0 |
| ai_timestamp | DATETIME | |
| validation_status | ENUM('pending','approved','corrected','rejected') | default pending |
| doctor_id | INT FK → users.id | NULL until reviewed |
| doctor_notes | TEXT | |
| validated_at | DATETIME | |

### Table: inventory
| Column | Type | Notes |
|---|---|---|
| id | INT PK AUTO_INCREMENT | |
| item_name | VARCHAR(255) | |
| category | VARCHAR(100) | |
| quantity | INT | |
| reorder_threshold | INT | |
| last_updated | DATETIME | |

### Table: audit_logs
| Column | Type | Notes |
|---|---|---|
| id | INT PK AUTO_INCREMENT | |
| user_id | INT FK → users.id | |
| action | VARCHAR(255) | e.g. 'login', 'upload_scan', 'validate_result' |
| target_table | VARCHAR(100) | |
| target_id | INT | |
| timestamp | DATETIME | |
| ip_address | VARCHAR(45) | |

---

## 7. CT SCAN PROCESSING PIPELINE

This is the most complex flow. Implement as a background task (Django's threading or Celery) — do NOT block the HTTP response while the CNN runs.

| Step | Action | Tier | Notes |
|---|---|---|---|
| 1 | Patient or nurse uploads CT image via form | Frontend | Client-side format check first |
| 2 | Backend receives, re-validates format | Django view | Reject non-DICOM/PNG/JPG with HTTP 400 |
| 3 | Save original to /media/ct_scans/original/ | Django | Create CTScan DB record, status = 'uploaded' |
| 4 | Preprocessing | diagnostics/cnn_service.py | Resize 224×224, normalize, median filter, contrast enhance. Save to /media/ct_scans/preprocessed/ |
| 5 | CNN inference | diagnostics/cnn_service.py | Load model, forward pass, get class + confidence. Target < 5s. |
| 6 | Store result | Django / MySQL | Write to ai_results table. Update ct_scans.status = 'analyzed' |
| 7 | Notify doctor | Django | In-app notification to assigned doctor. Use Django messages or a Notification model. |
| 8 | Doctor reviews | Frontend + Django | Doctor sees scan image + AI output + patient history. Approves/modifies/annotates. |
| 9 | Write final record | Django | Update ai_results.validation_status. Log to audit_logs. |
| 10 (optional) | Feedback loop | diagnostics/ | If doctor corrects prediction, queue (image, correct_label) for future retraining. |

---

## 8. CNN MODEL SPECIFICATION

### Input
- Cardiac CT scan image
- Preprocessed to 224 × 224 pixels
- Grayscale or RGB (normalize to [0,1])

### Preprocessing Steps (in order)
1. Resize to 224 × 224
2. Normalize pixel values to [0, 1]
3. Apply median filter (noise reduction)
4. Apply contrast enhancement (CLAHE or histogram equalization) if needed

### Architecture
```
Input (224×224×1 or 224×224×3)
→ Conv2D(32, 3×3, ReLU)
→ MaxPooling2D(2×2)
→ Conv2D(64, 3×3, ReLU)
→ MaxPooling2D(2×2)
→ Conv2D(128, 3×3, ReLU)
→ MaxPooling2D(2×2)
→ Flatten
→ Dense(128, ReLU)
→ Dropout(0.5)
→ Dense(64, ReLU)
→ Dense(1, Sigmoid)
```

### Output
- Single value 0.0–1.0
- >= 0.5 → Abnormal
- < 0.5 → Normal
- Confidence score = raw sigmoid output

### Training Config
- Loss: binary_crossentropy
- Optimizer: Adam
- Metrics: accuracy, precision, recall
- Regularization: Dropout(0.5), data augmentation (rotation, flip, shift)
- Early stopping: patience=10
- Save best: ModelCheckpoint('best_model.h5')

### Model File
- Saved as: `diagnostics/ml_models/cardiac_cnn.h5` (or `.pt` for PyTorch)
- Loaded once at Django startup in `diagnostics/apps.py` ready() method
- Never reload per request

---

## 9. DJANGO PROJECT STRUCTURE

```
ohms/                          ← Django project root
├── ohms/                      ← Project settings package
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/                  ← User auth, registration, RBAC
│   ├── models.py              ← Custom User model with role field
│   ├── views.py               ← login, logout, register, profile
│   ├── urls.py
│   └── templates/accounts/
├── patients/                  ← Patient records, medical history
│   ├── models.py
│   ├── views.py
│   └── templates/patients/
├── appointments/              ← Booking, scheduling, reminders
│   ├── models.py
│   ├── views.py
│   └── templates/appointments/
├── consultations/             ← Video/chat, prescriptions
│   ├── models.py
│   ├── views.py
│   └── templates/consultations/
├── diagnostics/               ← CT upload, CNN inference, AI results
│   ├── models.py              ← CTScan, AIResult
│   ├── views.py               ← upload_scan, view_result, validate_result
│   ├── cnn_service.py         ← preprocess() and predict() functions
│   ├── apps.py                ← Load model on startup
│   ├── ml_models/             ← cardiac_cnn.h5 lives here
│   └── templates/diagnostics/
├── admin_panel/               ← Staff mgmt, inventory, analytics, audit logs
│   ├── models.py
│   ├── views.py
│   └── templates/admin_panel/
├── notifications/             ← Notification model and triggers
│   ├── models.py
│   └── views.py
├── static/                    ← CSS, JS, images (shared)
├── media/                     ← Uploaded files (gitignored)
│   └── ct_scans/
│       ├── original/
│       └── preprocessed/
├── templates/                 ← Base templates, shared partials
│   └── base.html
├── manage.py
└── requirements.txt
```

---

## 10. API ENDPOINTS

| Method | URL | Auth | Description |
|---|---|---|---|
| POST | /api/auth/register | Public | Patient self-registration |
| POST | /api/auth/login | Public | Returns session cookie |
| POST | /api/auth/logout | Any | Clears session |
| GET | /api/patient/{id} | Doctor, Nurse, Admin | Get patient record |
| PUT | /api/patient/{id} | Doctor, Nurse | Update patient record |
| POST | /api/appointment/book | Patient | Book appointment |
| GET | /api/appointment/list | Doctor, Patient, Nurse | List appointments |
| PUT | /api/appointment/{id} | Doctor, Admin | Update appointment status |
| POST | /api/ct/upload | Patient, Nurse | Upload CT scan (FR-07) |
| GET | /api/ct/result/{id} | Doctor, Patient | Get AI result for scan |
| PUT | /api/ct/validate/{id} | Doctor | Doctor validates AI result (FR-09) |
| POST | /api/ai/analyze | Internal only | Trigger CNN inference (called internally, not from frontend) |
| GET | /api/admin/staff | Admin | List all staff |
| POST | /api/admin/staff | Admin | Create staff account |
| GET | /api/admin/inventory | Admin | List inventory |
| PUT | /api/admin/inventory/{id} | Admin | Update stock |
| GET | /api/admin/analytics | Admin | Analytics data |
| GET | /api/admin/audit-logs | Admin | Audit log entries |

---

## 11. ROLE-BASED ACCESS CONTROL

| Feature | Doctor | Nurse | Patient | Admin | Lab Tech |
|---|---|---|---|---|---|
| Register (self) | No | No | Yes | No | No |
| Create staff accounts | No | No | No | Yes | No |
| View own records | Yes | Yes | Yes | Yes | Yes |
| View any patient record | Yes | Yes | No | Yes | No |
| Update patient records | Yes | Yes | No | No | No |
| Book appointments | No | No | Yes | No | No |
| Manage appointments | Yes | Yes | No | Yes | No |
| Upload CT scans | No | Yes | Yes | No | Yes |
| View CT AI results | Yes | No | Own only | Yes | No |
| Validate AI results | Yes | No | No | No | No |
| Upload lab results | No | No | No | No | Yes |
| Manage inventory | No | No | No | Yes | No |
| View analytics | No | No | No | Yes | No |
| View audit logs | No | No | No | Yes | No |

---

## 12. KNOWN GAPS — MUST RESOLVE BEFORE BUILDING

| # | Gap | Impact | Action |
|---|---|---|---|
| 1 | Lab Technician has no defined Django views or URL routes | Cannot build their interface | Define views: upload_result, track_sample, view_assigned_patients |
| 2 | Inventory management in Ch.2 but missing from Ch.3 requirements | Scope confusion | Treat FR-11 as confirmed. Build it in admin_panel app. |
| 3 | CT scope inconsistency — proposal mentions lung nodules in scope section but cardiac CT in methodology | Model training dataset ambiguity | Use cardiac CT dataset. Ignore lung references — supervisor has been informed. |
| 4 | Abstract in proposal has copy-paste boilerplate mid-paragraph | Thesis document quality only, no implementation impact | Fix in thesis document, not in code. |
| 5 | Chapters 4 and 5 of thesis not written | Thesis only | Write after prototype is complete. |
| 6 | No real cardiac CT dataset specified | AI module training | Use publicly available datasets: NIH ChestX-ray14, or Kaggle cardiac CT datasets as proxy. |

---

## 13. BUILD ORDER (DO NOT SKIP STEPS)

Build and verify each step before moving to the next. Parallel agents only after Step 4 is stable.

```
Step 1:  Django project scaffold + MySQL connection configured
Step 2:  Custom User model with role field (accounts app)
Step 3:  Auth — login, logout, registration (patients only), role-based redirects
Step 4:  Patient records CRUD (patients app)
Step 5:  Appointment booking system (appointments app)
Step 6:  Consultation module + prescription issuance (consultations app)
Step 7:  CT scan upload with format validation (diagnostics app — FR-07)
Step 8:  CNN preprocessing pipeline (diagnostics/cnn_service.py — stub first)
Step 9:  CNN inference integration — replace stub with real model (FR-08)
Step 10: AI validation dashboard for doctors (FR-09)
Step 11: Notifications system
Step 12: Staff management (admin_panel app — FR-10)
Step 13: Inventory tracking (admin_panel app — FR-11)
Step 14: Reports and analytics dashboard (FR-12)
Step 15: Audit logging (FR-14, FR-15)
Step 16: Frontend polish — HTML/CSS templates for all role dashboards
Step 17: End-to-end testing
```

---

## 14. CNN STUB (USE THIS UNTIL REAL MODEL IS READY)

During Steps 7–9, use this stub in `diagnostics/cnn_service.py` so the full pipeline can be tested before the real model is trained:

```python
# diagnostics/cnn_service.py
# STUB — replace predict() with real CNN inference at Step 9

def preprocess(image_path):
    """Stub: returns the path unchanged."""
    # TODO: implement resize, normalize, median filter, contrast enhance
    return image_path

def predict(preprocessed_path):
    """Stub: returns hardcoded result for pipeline testing."""
    # TODO: replace with real TensorFlow/PyTorch model inference
    return {
        "class": "normal",
        "confidence": 0.91,
        "model_version": "stub-v0"
    }
```

Replace `predict()` at Step 9 with:

```python
import numpy as np
from tensorflow.keras.models import load_model
from PIL import Image

_model = None  # loaded once in apps.py

def load_cnn_model(model_path):
    global _model
    _model = load_model(model_path)

def predict(preprocessed_path):
    img = Image.open(preprocessed_path).convert('L')  # grayscale
    img = img.resize((224, 224))
    arr = np.array(img) / 255.0
    arr = arr.reshape(1, 224, 224, 1)
    score = float(_model.predict(arr)[0][0])
    return {
        "class": "abnormal" if score >= 0.5 else "normal",
        "confidence": score if score >= 0.5 else 1 - score,
        "model_version": "cardiac-cnn-v1"
    }
```

---

*End of OHMS Agent Reference — v1.0*
*All agents working on this project must treat this document as ground truth.*