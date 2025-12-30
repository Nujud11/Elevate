# Elevate — Internship Management Platform

Elevate is a web-based internship management platform built using **Django and Wagtail CMS**.  
It is designed to streamline the process of posting internships, managing applications, and connecting students with companies through a structured and scalable system.

The project focuses on solving common challenges in internship ecosystems by centralizing workflows for students, companies, and administrators.

---

## 🧠 Project Overview

Internship management is often fragmented across emails, spreadsheets, and external forms.  
Elevate addresses this problem by providing a unified platform where:

- **Companies** can post internship opportunities, review student applications (CVs and cover letters), and accept or reject applicants.
- **Students** can browse available internships, apply directly through the platform, and manage their profiles.
- **Administrators** can oversee content, users, and approvals through the Wagtail CMS admin panel.

The platform is built with a modular architecture to support scalability and future feature expansion.

---

## ✨ Key Features

- Internship posting and management
- Student profile creation and internship applications
- Company onboarding and profile management
- Application review and decision workflow (accept / reject)
- Admin dashboard powered by Wagtail CMS
- Modular Django app structure for maintainability

---

## 🛠 Tech Stack

- **Python**
- **Django**
- **Wagtail CMS**
- **SQLite** (development database)
- **HTML / CSS**
- **Pytest** (testing)

---

## ▶️ Run Locally

```bash
git clone https://github.com/Nujud11/Elevate.git
cd Elevate

python -m venv venv
source venv/bin/activate  # macOS / Linux
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
