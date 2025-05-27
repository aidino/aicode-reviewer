# Authentication System Implementation Plan

## Overview
Kế hoạch implement tính năng đăng ký/đăng nhập cho AI Code Reviewer System sử dụng JWT authentication và PostgreSQL database.

## 1. Architecture Overview

### Authentication Flow
```
1. User Registration -> Hash Password -> Store in DB -> Return JWT Token
2. User Login -> Verify Credentials -> Generate JWT Token -> Return Token
3. Protected Routes -> Verify JWT Token -> Extract User Info -> Allow Access
4. Token Refresh -> Verify Refresh Token -> Generate New Access Token
5. Logout -> Blacklist Token -> Invalidate Session
```

### Tech Stack
- **Backend**: FastAPI + SQLAlchemy + PostgreSQL
- **Authentication**: JWT (JSON Web Tokens) với PyJWT
- **Password Security**: bcrypt hashing với passlib
- **Database Migration**: Alembic
- **Frontend**: React + Context API
- **Rate Limiting**: slowapi (FastAPI rate limiting)

## 2. Database Schema Design

### 2.1. Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    role VARCHAR(20) DEFAULT 'user', -- user, admin, premium
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_active ON users(is_active);
```

### 2.2. User Profiles Table
```sql
CREATE TABLE user_profiles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    full_name VARCHAR(255),
    avatar_url VARCHAR(500),
    bio TEXT,
    timezone VARCHAR(50) DEFAULT 'UTC',
    preferences JSONB DEFAULT '{}', -- UI preferences, notifications, etc.
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);
```

### 2.3. User Sessions Table (Token Blacklisting)
```sql
CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    token_jti VARCHAR(255) UNIQUE NOT NULL, -- JWT ID for blacklisting
    token_type VARCHAR(20) DEFAULT 'access', -- access, refresh
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    revoked_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    user_agent TEXT,
    ip_address INET,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_token_jti ON user_sessions(token_jti);
CREATE INDEX idx_user_sessions_expires_at ON user_sessions(expires_at);
```

### 2.4. User Permissions & Roles (Future Extension)
```sql
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    permissions JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE user_roles (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    granted_by INTEGER REFERENCES users(id),
    UNIQUE(user_id, role_id)
);
```

## 3. Backend Implementation

### 3.1. Dependencies
```python
# Add to requirements.txt
PyJWT>=2.8.0
passlib[bcrypt]>=1.7.4
python-multipart>=0.0.6
alembic>=1.13.0
slowapi>=0.1.9
python-decouple>=3.8
```

### 3.2. Models Structure
```
src/webapp/backend/models/
├── __init__.py
├── auth_models.py          # User, UserProfile, UserSession models
├── scan_models.py          # Existing scan models
└── base.py                 # Base model với common fields
```

### 3.3. Services Structure
```
src/webapp/backend/services/
├── __init__.py
├── auth_service.py         # Authentication business logic
├── user_service.py         # User management logic
├── token_service.py        # JWT token handling
└── scan_service.py         # Existing scan service
```

### 3.4. API Routes Structure
```
src/webapp/backend/api/
├── __init__.py
├── auth_routes.py          # Authentication endpoints
├── user_routes.py          # User profile endpoints
├── scan_routes.py          # Existing scan routes (update với auth)
└── main.py                 # Updated với auth middleware
```

### 3.5. Core Utilities
```
src/webapp/backend/core/
├── __init__.py
├── auth.py                 # JWT utilities, password hashing
├── security.py            # Security middleware, rate limiting
├── config.py              # Configuration management
└── exceptions.py          # Custom exceptions
```

## 4. API Endpoints Design

### 4.1. Authentication Endpoints
```
POST /api/auth/register
Request: {
  "username": "string",
  "email": "string", 
  "password": "string",
  "full_name": "string" (optional)
}
Response: {
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": 1,
    "username": "string",
    "email": "string",
    "full_name": "string",
    "role": "user"
  }
}

POST /api/auth/login
Request: {
  "username_or_email": "string",
  "password": "string"
}
Response: {
  "access_token": "string",
  "refresh_token": "string", 
  "token_type": "bearer",
  "expires_in": 3600,
  "user": { ... }
}

POST /api/auth/logout
Headers: Authorization: Bearer <token>
Response: {
  "message": "Successfully logged out"
}

POST /api/auth/refresh
Request: {
  "refresh_token": "string"
}
Response: {
  "access_token": "string",
  "token_type": "bearer",
  "expires_in": 3600
}

GET /api/auth/me
Headers: Authorization: Bearer <token>
Response: {
  "user": { ... },
  "profile": { ... }
}
```

### 4.2. User Management Endpoints
```
PUT /api/users/profile
PATCH /api/users/password
GET /api/users/sessions
DELETE /api/users/sessions/{session_id}
```

## 5. Security Considerations

### 5.1. Password Security
- Minimum 8 characters, include uppercase, lowercase, numbers
- bcrypt hashing với salt rounds >= 12
- Password history để prevent reuse
- Account lockout after failed attempts

### 5.2. JWT Security
- Short access token expiry (15-30 minutes)
- Longer refresh token expiry (7-30 days)
- Include JTI (JWT ID) for token blacklisting
- Rotate refresh tokens on use
- Store sensitive claims in database, not JWT

### 5.3. Rate Limiting
- Login attempts: 5 per minute per IP
- Registration: 3 per hour per IP
- Password reset: 3 per hour per email
- API calls: 100 per minute per authenticated user

### 5.4. Additional Security
- HTTPS only in production
- Secure HTTP headers (HSTS, CSP, etc.)
- Input validation và sanitization
- SQL injection protection (SQLAlchemy ORM)
- XSS protection
- CSRF protection for state-changing operations

## 6. Frontend Implementation

### 6.1. Authentication Context
```typescript
interface AuthContextType {
  user: User | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
  isLoading: boolean;
  updateProfile: (profile: Partial<UserProfile>) => Promise<void>;
}
```

### 6.2. Component Structure
```
src/webapp/frontend/src/
├── components/auth/
│   ├── LoginForm.tsx
│   ├── RegisterForm.tsx
│   ├── ProtectedRoute.tsx
│   └── UserProfile.tsx
├── hooks/
│   ├── useAuth.ts
│   ├── useTokenRefresh.ts
│   └── useProfile.ts
├── services/
│   ├── authService.ts
│   └── tokenService.ts
└── types/
    └── auth.ts
```

### 6.3. Token Management
- Store tokens in httpOnly cookies (preferred) or localStorage
- Automatic token refresh before expiry
- Redirect to login on authentication failure
- Clear tokens on logout

## 7. Database Migration Plan

### 7.1. Migration Files
```
migrations/
├── env.py
├── script.py.mako
└── versions/
    ├── 001_create_users_table.py
    ├── 002_create_user_profiles_table.py
    ├── 003_create_user_sessions_table.py
    └── 004_add_auth_indexes.py
```

### 7.2. Existing Data Considerations
- Scan ownership: Add user_id foreign key to scans table
- Anonymous scans: Allow scans without user (guest mode)
- Data migration: Assign existing scans to default admin user

## 8. Testing Strategy

### 8.1. Backend Testing
- Unit tests: Models, services, utilities
- Integration tests: API endpoints, database operations
- Security tests: Authentication, authorization, rate limiting
- Performance tests: Database queries, token operations

### 8.2. Frontend Testing
- Component tests: Forms, authentication flow
- Integration tests: API communication
- E2E tests: Complete authentication workflow
- Security tests: Token handling, protected routes

## 9. Deployment Considerations

### 9.1. Environment Variables
```env
# JWT Configuration
JWT_SECRET_KEY=<strong-secret-key>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
DATABASE_URL=postgresql://user:pass@host:port/db

# Security
BCRYPT_ROUNDS=12
RATE_LIMIT_ENABLED=true
```

### 9.2. Production Setup
- Use strong JWT secret keys
- Enable HTTPS
- Configure rate limiting
- Set up monitoring cho failed login attempts
- Regular security audits

## 10. Future Enhancements

### 10.1. Phase 2 Features
- Social login (Google, GitHub)
- Two-factor authentication (2FA)
- Email verification workflow
- Password reset via email
- Admin panel for user management

### 10.2. Advanced Features  
- OAuth2 provider capabilities
- API key management for external integrations
- Audit logging for security events
- Role-based access control (RBAC)
- Multi-tenant support

## 11. Implementation Timeline

### Week 1: Database & Backend Core
- [ ] Setup database models và migrations
- [ ] Implement authentication utilities
- [ ] Create basic auth services
- [ ] Write unit tests

### Week 2: API Endpoints
- [ ] Implement auth API endpoints
- [ ] Add security middleware
- [ ] Integration testing
- [ ] API documentation

### Week 3: Frontend Integration
- [ ] Create authentication components
- [ ] Implement protected routes
- [ ] Token management
- [ ] User profile UI

### Week 4: Security & Testing
- [ ] Security hardening
- [ ] Comprehensive testing
- [ ] Performance optimization
- [ ] Documentation completion

---

*Document created: 2025-01-28*
*Last updated: 2025-01-28* 