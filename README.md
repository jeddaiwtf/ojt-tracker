# 🎓 OJT Performance Tracker

A production-ready Django web application to replace Excel-based OJT tracking.
Built with Django 5, Bootstrap 5, Chart.js, and deployable 100% free on Render.com.

---

## 📁 Project Structure

```
ojt_tracker/
├── manage.py
├── requirements.txt
├── Procfile                    ← Render/Heroku deployment
├── render.yaml                 ← Render.com blueprint
├── .env.example                ← Environment variable template
├── .gitignore
│
├── ojt_tracker/                ← Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── tracker/                    ← Main application
│   ├── models.py               ← UserProfile, DailyLog, WeeklySummary
│   ├── views.py                ← Class-based views
│   ├── forms.py                ← Crispy forms
│   ├── urls.py                 ← App URL routing
│   ├── admin.py                ← Admin panel config
│   ├── migrations/
│   ├── templatetags/
│   │   └── ojt_filters.py      ← Custom template filters
│   └── templates/tracker/
│       ├── dashboard.html
│       ├── log_list.html
│       ├── log_form.html
│       ├── weekly_list.html
│       ├── weekly_form.html
│       ├── completion_report.html
│       ├── register.html
│       └── profile_form.html
│
├── templates/
│   ├── base.html               ← Sidebar layout
│   └── registration/
│       └── login.html
│
└── static/
    ├── css/
    └── js/
```

---

## 🗃️ Database Schema

```
User (Django built-in)
  └──1:1──► UserProfile
              ├── department
              ├── supervisor
              ├── total_required_hours  (default 448)
              ├── ojt_start_date
              └──1:N──► DailyLog
                          ├── date (unique per profile)
                          ├── time_in
                          ├── time_out
                          ├── daily_hours  [AUTO: (out-in) - 1hr lunch]
                          ├── week_number  [AUTO: floor((date-start)/7)+1]
                          └── remarks
              └──1:N──► WeeklySummary
                          ├── week_number (unique per profile)
                          ├── weekly_learnings
                          └── major_tasks
```

---

## ⚙️ Local Development Setup

### 1. Clone & Create Virtual Environment
```bash
git clone <your-repo-url>
cd ojt_tracker
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env — set your SECRET_KEY
```

### 4. Run Migrations & Create Superuser
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 5. Run Dev Server
```bash
python manage.py runserver
```
Open http://127.0.0.1:8000

---

## 🚀 Free Deployment — Render.com (Recommended)

### Prerequisites
- GitHub account (push your code to a repo)
- Render.com account (free tier)

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Initial OJT Tracker"
git remote add origin https://github.com/YOUR_USERNAME/ojt-tracker.git
git push -u origin main
```

### Step 2: Create PostgreSQL Database on Render
1. Go to https://render.com → Dashboard → New → **PostgreSQL**
2. Name: `ojt-tracker-db`
3. Plan: **Free**
4. Click **Create Database**
5. Copy the **Internal Database URL**

### Step 3: Deploy Web Service
1. Dashboard → New → **Web Service**
2. Connect your GitHub repo
3. Configure:
   - **Name**: `ojt-tracker`
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - **Start Command**: `gunicorn ojt_tracker.wsgi:application --bind 0.0.0.0:$PORT`
   - **Plan**: Free

### Step 4: Set Environment Variables
In Render Web Service → Environment tab:
```
SECRET_KEY    = (click "Generate" or use a 50-char random string)
DEBUG         = False
ALLOWED_HOSTS = .onrender.com
DATABASE_URL  = (paste your PostgreSQL Internal URL from Step 2)
```

### Step 5: Create Superuser on Render
In Render → your service → **Shell** tab:
```bash
python manage.py createsuperuser
```

✅ Your app is now live at `https://ojt-tracker.onrender.com`

---

## 🔐 Security Checklist

- [x] `SECRET_KEY` stored in environment variable
- [x] `DEBUG=False` in production
- [x] `ALLOWED_HOSTS` explicitly set
- [x] HTTPS enforced via `SECURE_SSL_REDIRECT`
- [x] `CSRF_COOKIE_SECURE = True`
- [x] `SESSION_COOKIE_SECURE = True`
- [x] `HSTS` headers enabled
- [x] `X_FRAME_OPTIONS = 'DENY'`
- [x] Users can only see their own data (filtered by `profile__user=request.user`)
- [x] Admin panel protected by `is_staff` check
- [x] Input validation on all forms (client + server side)
- [x] No secrets in version control (`.env` in `.gitignore`)

---

## 📊 Business Logic Summary

### Hour Calculation
```
Daily Hours = (time_out - time_in) - 1 hour lunch
            = max(0, calculated_hours)
```

### Custom Week Number (NOT calendar week)
```
Week Number = floor((log_date - ojt_start_date).days / 7) + 1
Week 1 = Days 0-6 from start
Week 2 = Days 7-13
...
```

### Completion
```
Rendered = SUM(daily_hours) for all logs
Remaining = max(0, required - rendered)
Percentage = min(100, (rendered / required) * 100)
```

---

## 🔌 API Endpoint

GET `/api/logs/` — Returns JSON of all your logs + profile summary.

Example response:
```json
{
  "profile": {
    "name": "Juan Dela Cruz",
    "department": "IT Department",
    "total_required": "448.00",
    "total_rendered": "120.50",
    "completion_pct": 26.9
  },
  "logs": [
    {
      "id": 1,
      "date": "2024-06-03",
      "time_in": "08:00:00",
      "time_out": "17:00:00",
      "daily_hours": "8.00",
      "week_number": 1,
      "remarks": "Orientation day"
    }
  ]
}
```

---

## 📈 Future Improvements Roadmap

| Priority | Feature |
|----------|---------|
| High | Email notification when OJT is 75%, 90%, 100% complete |
| High | PDF export using WeasyPrint (server-side) |
| Medium | Multi-student supervisor view (see all students' progress) |
| Medium | Bulk log import from CSV |
| Medium | OJT schedule / calendar view |
| Low | REST API with JWT authentication (Django REST Framework) |
| Low | Mobile app (PWA or React Native) |
| Low | Dark mode toggle |
| Low | Overtime hour tracking |

---

## 📝 URL Reference

| URL | View | Description |
|-----|------|-------------|
| `/` | Redirect | → Dashboard |
| `/accounts/login/` | LoginView | Sign in |
| `/register/` | RegisterView | Create account |
| `/dashboard/` | DashboardView | Main dashboard |
| `/logs/` | DailyLogListView | All daily logs |
| `/logs/add/` | DailyLogCreateView | Add new log |
| `/logs/<pk>/edit/` | DailyLogUpdateView | Edit log |
| `/logs/<pk>/delete/` | DailyLogDeleteView | Delete log |
| `/weekly/` | WeeklySummaryListView | Weekly summaries |
| `/weekly/<n>/edit/` | WeeklySummaryEditView | Edit week notes |
| `/report/` | CompletionReportView | Printable report |
| `/export/csv/` | export_logs_csv | Download CSV |
| `/api/logs/` | api_logs | JSON API |
| `/admin/` | AdminSite | Django admin |
