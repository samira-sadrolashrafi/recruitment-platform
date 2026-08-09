# JobPortal — Django Job Recruitment Platform

JobPortal is a Django-based recruitment platform connecting **employers** and **job seekers**.

Employers can create and manage job posts, review applicants, download submitted resumes, accept or reject applications, and schedule interviews. Job seekers can browse jobs, manage resumes, apply for positions, track application status, and receive notifications.

## Features

### Job Seekers

- Register and log in with OTP-based account verification
- Browse active jobs and view job details
- Filter jobs by title, benefits, and salary range
- Upload and manage resumes
- Apply with an optional resume and cover letter
- Select only resumes belonging to their own account
- Track submitted applications and their status
- Receive application-related notifications
- View job recommendations based on previous applications

### Employers

- Register and log in as an employer
- Create, edit, and delete their own job posts
- Define salary range, benefits, requirements, and job details
- Review applicants for their jobs
- Download submitted resumes
- Accept or reject applications
- Set interview dates for accepted applicants

## Authentication & User Roles

The project uses a custom Django user model with separate **employer** and **job-seeker** roles.

It includes:

- Employer and job-seeker profile models
- Email and phone OTP models
- Session-based verification
- Custom authentication backend for verified users
- Role-based dashboard behavior

OTP delivery is currently simulated through logging for local development.

## Job Search & Recommendations

Jobs can be filtered by title, benefits, and salary range.

Custom Django managers and querysets are used for job searching, filtering, application queries, resume ownership, and recommendations.

Recommendations are keyword-based and use previously applied-to jobs. Already-applied jobs are excluded, with recent active jobs used as a fallback.

## Resume & Application Management

Supported resume formats:

```text
.pdf, .doc, .docx, .txt
```

Maximum file size: **5 MB**

Resume access is restricted so users can only select their own resumes when applying, while employers can download resumes submitted to their own job posts.

Application statuses are:

```text
Pending
Accepted
Rejected
```

A job seeker cannot apply to the same job more than once. Employers are prevented from applying for jobs.

Application updates generate in-app notifications, and Django's email backend can also be used for application-result emails.

## Tech Stack

- **Backend:** Python, Django 5.2.8
- **Database:** PostgreSQL, psycopg2-binary
- **Frontend:** HTML, CSS, Django Templates, Bootstrap 5.3, Bootstrap Icons

## Project Structure

```text
accounts/       Users, authentication, OTPs, profiles, notifications
applications/   Resumes and job applications
jobs/           Job posts, filtering, search, recommendations
config/         Django settings and configuration
templates/      Templates and reusable partials
static/         CSS and static assets
media/          Resume files
```

## Local Setup

Clone the repository and create a virtual environment:

```bash
git clone <repository-url>
cd <repository-folder>

python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file using `.env.example` as a reference:

```env
SECRET_KEY=your-secret-key
DEBUG=True

DB_NAME=your-database-name
DB_USER=your-database-user
DB_PASSWORD=your-database-password
DB_HOST=127.0.0.1
DB_PORT=5432
```

Create the PostgreSQL database, then run:

```bash
python manage.py migrate
```

Optional demo data:

```bash
python manage.py create_test_data
```

Start the development server:

```bash
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/
```

## Notes

- PostgreSQL is the primary database.
- Sensitive configuration is stored in a local `.env` file and excluded from Git.
- OTP delivery currently uses a development logging implementation.
- Job recommendations are keyword-based, not machine-learning based.
- The project is configured for local development.

## Author

samira sadrolashrafi