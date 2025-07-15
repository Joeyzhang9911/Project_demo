# SDG Form System & Google Docs API Quick Integration Guide

## Quick Start

**Before first use:**
- In the `frontend` directory, run:
  ```bash
  npm install date-fns
  ```

## 1. Google Cloud Setup
- Create/select a project at [Google Cloud Console](https://console.cloud.google.com/)
- Enable Google Docs API and Google Drive API
- Create credentials:
  - For dev/testing: OAuth 2.0 Client ID (Web/Desktop), set redirect URI (e.g. `http://localhost:8000/auth/google/callback`)
  - For production: Service Account (Editor role), download JSON key
- Place `credentials.json` in `backend/app/`
- (Optional) Share target Drive folder with service account email

## 2. Environment Variables
Add to `.env`:
```env
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
```

## 3. Backend Setup
- Install dependencies:
  ```bash
  pip install google-api-python-client channels channels-redis
  ```
- In `settings.py`:
  ```python
  INSTALLED_APPS += ['channels']
  ASGI_APPLICATION = '_config.asgi.application'
  CHANNEL_LAYERS = {
      'default': {
          'BACKEND': 'channels_redis.core.RedisChannelLayer',
          'CONFIG': {"hosts": [os.environ.get('REDIS_URL', 'redis://localhost:6379/0')]},
      },
  }
  GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
  GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')
  GOOGLE_REDIRECT_URI = os.environ.get('GOOGLE_REDIRECT_URI')
  ```
- Run migrations:
  ```bash
  python manage.py makemigrations sdg_action_plan
  python manage.py migrate
  ```

## 4. API Endpoints
- `POST /api/sdg-action-plan/{id}/google-docs/` — Sync/Create Google Doc
- `GET /api/sdg-action-plan/{id}/google-docs/status/` — Get Doc status

## 5. Frontend Integration
- On receiving `auth_required` and `auth_url`, prompt user to authorize, then retry
- WebSocket supported for real-time collaboration

## 6. Security
- Do NOT commit `credentials.json` to version control
- Service account must have Docs/Drive edit permissions

## 7. Example Structure
```
backend/app/
├── credentials.json
├── token.pickle
├── manage.py
└── ...
```

---
For more details, see:
- [Google Docs API Docs](https://developers.google.com/docs/api)
- [Google Drive API Docs](https://developers.google.com/drive)
- [Django Channels Docs](https://channels.readthedocs.io/)