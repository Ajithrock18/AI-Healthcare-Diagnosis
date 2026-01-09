# Nginx Setup & Configuration Guide

## Project Architecture with Nginx

```
┌─────────────────────────────────────────────┐
│         Nginx Reverse Proxy (Port 80)       │
├─────────────────────────────────────────────┤
│ Routes:                                     │
│ • / → Frontend (Streamlit, Port 8501)       │
│ • /login → Backend (FastAPI, Port 8000)     │
│ • /predict → Backend (FastAPI, Port 8000)   │
│ • /history → Backend (FastAPI, Port 8000)   │
│ • /docs → FastAPI Swagger UI                │
│ • /openapi.json → API Schema                │
└─────────────────────────────────────────────┘
         ↓                    ↓
    ┌─────────────┐   ┌──────────────┐
    │  Frontend   │   │   Backend    │
    │  Streamlit  │   │   FastAPI    │
    │ (8501)      │   │  (8000)      │
    └─────────────┘   └──────────────┘
```

## Prerequisites

- **Docker**: Install from [docker.com](https://docker.com)
- **Docker Compose**: Included with Docker Desktop
- **Git**: For version control
- **Curl** or **Postman**: For API testing (optional)

## Quick Start with Docker

### 1. Build and Start All Services

```powershell
cd "c:\Users\Ajith Kumar T\OneDrive\Desktop\AI Healthcare Project"

# Build images
docker-compose build

# Start all services (backend, frontend, nginx)
docker-compose up -d

# Check status
docker-compose ps
```

**Expected output:**
```
CONTAINER ID   IMAGE                          STATUS
...            aihealthcareproject-backend    Up (healthy)
...            aihealthcareproject-frontend   Up (healthy)
...            aihealthcareproject-nginx      Up
```

### 2. Access the Application

| Component | URL | Purpose |
|-----------|-----|---------|
| **Frontend UI** | http://localhost:8080 | Streamlit dashboard |
| **Backend API Docs** | http://localhost:8080/docs | Swagger UI (interactive) |
| **Backend API** | http://localhost:8080/login, /predict | API endpoints |
| **Direct Backend** | http://localhost:8000 | Backend without Nginx |
| **Direct Frontend** | http://localhost:8501 | Frontend without Nginx |

### 3. Login Credentials

```
Username: admin
Password: admin123
```

## Docker Compose Services

### Backend Service
- **Image**: Custom (builds from `./backend/Dockerfile`)
- **Port**: 8000 (internal), exposed via Nginx
- **Healthcheck**: API `/docs` endpoint
- **Network**: healthcare-network

### Frontend Service
- **Image**: Custom (builds from `./frontend/Dockerfile`)
- **Port**: 8501 (internal), exposed via Nginx
- **Healthcheck**: Streamlit health endpoint
- **Dependencies**: Waits for backend to be healthy
- **Network**: healthcare-network

### Nginx Service
- **Image**: nginx:alpine (lightweight)
- **Ports**: 80 (HTTP), 443 (HTTPS - optional)
- **Configuration**: `./nginx/nginx.conf`
- **SSL Certs**: `./nginx/ssl/` (if using HTTPS)
- **Network**: healthcare-network

## Nginx Configuration Details

**File**: `./nginx/nginx.conf`

### Upstream Definitions
```nginx
upstream backend {
    server backend:8000;  # Uses Docker DNS for container discovery
}

upstream frontend {
    server frontend:8501;
}
```

### Location Blocks

#### Root Path `/`
- Forwards to **Frontend (Streamlit)**
- WebSocket support enabled (for Streamlit interactivity)
- Max upload size: 50MB

#### API Endpoints
- `/login` → Backend login endpoint
- `/predict` → Model inference endpoint
- `/history` → User prediction history
- `/docs` → FastAPI Swagger documentation
- `/api/` → General API route prefix

### Key Headers
- `X-Real-IP`: Preserves client IP
- `X-Forwarded-For`: Tracks proxy chain
- `X-Forwarded-Proto`: Preserves original protocol (HTTP/HTTPS)
- `Host`: Maintains original host header
- `Upgrade`/`Connection`: WebSocket support for Streamlit

## Common Commands

### Start Services
```powershell
docker-compose up -d
```

### Stop Services
```powershell
docker-compose down
```

### View Logs
```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f nginx
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Restart Service
```powershell
docker-compose restart nginx
```

### Rebuild Images (after code changes)
```powershell
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Check Service Health
```powershell
docker-compose ps

# Detailed health status
docker-compose exec backend curl -s http://localhost:8000/docs | head -20
```

## Testing Nginx Connectivity

### Test Frontend Access
```powershell
curl http://localhost
# Should return HTML from Streamlit
```

### Test Backend API
```powershell
# Login
curl -X POST http://localhost/login `
  -H "Content-Type: application/x-www-form-urlencoded" `
  -d "username=admin&password=admin123"

# Response should include access_token
```

### Test Swagger Docs
```powershell
curl http://localhost/docs
# Should return API documentation
```

## Troubleshooting

### Nginx Won't Start
**Error**: `docker: Error response from daemon`

**Solution**:
```powershell
# Check if ports are in use
netstat -ano | findstr :80
netstat -ano | findstr :443

# Kill process using port 80
taskkill /PID <PID> /F

# Restart
docker-compose restart nginx
```

### Container Health Checks Failing
**Error**: `(unhealthy)` status in `docker-compose ps`

**Solution**:
```powershell
# Check logs
docker-compose logs backend

# Ensure backend is fully started
docker-compose exec backend curl -s http://localhost:8000/docs

# Wait 40+ seconds for startup period, then restart
docker-compose restart frontend
```

### Frontend Can't Reach Backend
**Error**: Login fails with connection error in Streamlit

**Verify**:
```powershell
# Inside frontend container, test backend connectivity
docker-compose exec frontend curl http://backend:8000/docs

# If fails, check network
docker network inspect aihealthcareproject-nginx
```

### SSL/HTTPS Not Working
**Setup Instructions**:
1. Create `./nginx/ssl/` directory
2. Add `certificate.crt` and `private.key` files
3. Update `nginx.conf` with SSL configuration:
```nginx
listen 443 ssl http2;
ssl_certificate /etc/nginx/ssl/certificate.crt;
ssl_certificate_key /etc/nginx/ssl/private.key;
```
4. Restart Nginx: `docker-compose restart nginx`

## Production Deployment

### For AWS/Cloud Deployment
1. Use managed container service (ECS, AKS, GKE)
2. Replace `localhost` with domain name
3. Use managed SSL certificates (ACM, Let's Encrypt)
4. Configure load balancer to forward to Nginx
5. Use secrets manager for API keys and passwords
6. Set up logging/monitoring (CloudWatch, ELK Stack)

### Environment Variables
Create `.env` file for sensitive data:
```env
SECRET_KEY=your-secret-key
DB_URL=postgresql://user:password@db:5432/healthcare
ALLOWED_HOSTS=yourdomain.com
```

### Docker Registry
Push images to registry (Docker Hub, ECR, GCR):
```powershell
docker tag aihealthcareproject-backend:latest myregistry/backend:latest
docker push myregistry/backend:latest
```

## Monitoring & Logs

### View Real-time Logs
```powershell
docker-compose logs -f nginx --tail 50
```

### Check Resource Usage
```powershell
docker stats
```

### Save Logs to File
```powershell
docker-compose logs > deployment.log
```

## Security Best Practices

1. **Change default credentials** in `backend/main.py`
2. **Use strong SECRET_KEY** in `.env`
3. **Enable HTTPS** with valid SSL certificates
4. **Rate limiting** - Add to Nginx config for `/predict` endpoint
5. **CORS Policy** - Configure in FastAPI if needed
6. **Input validation** - Already implemented in backend models
7. **Database encryption** - Use PostgreSQL in production instead of SQLite

## References

- [Nginx Documentation](https://nginx.org/en/docs/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Streamlit Deployment](https://docs.streamlit.io/streamlit-cloud/deploy-your-app)

---

**Last Updated**: January 9, 2026
**Status**: Production-Ready
