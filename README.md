

# KAAIZEN-API

KAAIZEN-API is a RESTful backend service built using Python, Django, and Django REST Framework. It is designed for fitness and lifestyle applications, providing APIs for managing users, workouts, nutrition, trainers, payments, and administrative operations.

---

## Features

The project includes a modular and scalable backend with the following capabilities:

* User authentication and registration
* JWT-based authentication using cookies
* Role-based access (admin, trainer, client)
* Workout management (create, update, delete, list)
* Nutrition planning and tracking
* Trainer and client management
* Personal training plans and subscriptions
* Wallet and payment integration
* Stripe payment integration with webhook handling
* Admin APIs for monitoring and control
* Background task handling using Celery
* Notification system
* Integration with third-party services such as Google OAuth and ZegoCloud

---

## Tech Stack

* Python
* Django
* Django REST Framework
* PostgreSQL (production) / SQLite (development)
* Redis (for caching and Celery)
* Celery (for background jobs)
* Stripe (payment processing)
* Cloudinary (media storage)
* Docker (containerization)
* Nginx (reverse proxy)
* AWS EC2 (deployment)
* GitHub Actions (CI/CD)

---

## Project Structure

```
KAAIZEN-API/
├── admin_api/              # Admin-specific endpoints
├── auth_api/               # Authentication logic
├── clients/                # Client-related features
├── core/                   # Shared utilities and configurations
├── kaaizen/                # Main project settings
├── nutrition/              # Nutrition module
├── trainers/               # Trainer-related logic
├── users/                  # Custom user model and user management
├── workouts/               # Workout-related features
├── personal_training/      # Training plans and subscriptions
├── wallet/                 # Wallet and transactions
├── notification/           # Notification system
├── manage.py
├── .env
```

---

## Installation

### Prerequisites

* Python 3.10 or higher
* PostgreSQL
* Redis
* Virtual environment tool (venv or virtualenv)

---

### Clone the repository

```
git clone <your-repo-url>
cd KAAIZEN-API
```

---

### Create virtual environment

```
python -m venv env
source env/bin/activate     # Linux / Mac
env\Scripts\activate        # Windows
```

---

### Install dependencies

```
pip install -r requirements.txt
```

---

### Configure environment variables

Create a `.env` file in the root directory:

```
SECRET_KEY=your_secret_key
DEBUG=True

DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_PORT=5432
DB_HOST=localhost

FRONTEND_URL=http://localhost:5173

STRIPE_SECRET_KEY=your_stripe_secret
STRIPE_WEBHOOK_SECRET=your_webhook_secret

REDIS_HOST=localhost
REDIS_PORT=6379
```

---

### Run migrations

```
python manage.py makemigrations
python manage.py migrate
```

---

### Create superuser

```
python manage.py createsuperuser
```

---

### Run development server

```
python manage.py runserver
```

---

## API Usage

All API endpoints are prefixed under:

```
/api/
```

Example endpoints:

* Authentication: `/api/auth/`
* Workouts: `/api/workouts/`
* Nutrition: `/api/nutrition/`
* Training Plans: `/api/personaltraining/`
* Admin: `/api/admin/`

---

## Stripe Integration

The project integrates Stripe for handling payments.

* Checkout sessions are created from the backend
* Webhooks are used to confirm successful payments
* Metadata is used to link payments with users and plans

Important:

* Always use production URLs in `FRONTEND_URL`
* Webhook endpoint must be publicly accessible

---

## Deployment

The application is containerized using Docker and deployed on AWS EC2.

### Docker

```
docker-compose up --build -d
```

### Services

* Backend runs on port 8000
* Frontend runs on port 3000
* Nginx handles routing and SSL

---

### Nginx Routing

* `/` → Frontend
* `/api/` → Django backend

---

## CI/CD

GitHub Actions is used for automated deployment:

* Builds Docker images
* Pushes to AWS ECR
* Deploys to EC2

---

## Logging

* Logs are configured using Django logging
* Accessible via Docker logs:

```
docker logs -f kaaizen-backend
```

---

## Security Considerations

* Use environment variables for sensitive data
* Disable DEBUG in production
* Configure ALLOWED_HOSTS properly
* Use HTTPS for all requests
* Secure cookies for authentication

---

## Future Improvements

* Add API documentation using Swagger or Redoc
* Implement rate limiting
* Improve test coverage
* Add monitoring and alerting

---
