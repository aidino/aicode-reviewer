# Authentication System - Tóm Tắt Kế Hoạch Implementation

## Mục Tiêu
Implement hệ thống đăng ký/đăng nhập cho AI Code Reviewer với JWT authentication và PostgreSQL database.

## Thiết Kế Database 

### Core Tables
1. **users** - Thông tin người dùng cơ bản
   - id, username, email, password_hash, is_active, role, timestamps
   - Roles: user, admin, premium
   - Constraints: unique email/username, valid email format, password length

2. **user_profiles** - Thông tin profile mở rộng  
   - user_id (FK), full_name, avatar_url, bio, timezone, preferences (JSONB)
   - Social links: github_username, linkedin_url, website_url

3. **user_sessions** - Quản lý JWT tokens và blacklisting
   - user_id (FK), token_jti, token_type (access/refresh), expires_at
   - Security: user_agent, ip_address, device_info (JSONB)

4. **scan_permissions** - Access control cho scans
   - scan_id (FK), user_id (FK), permission_type (view/edit/admin)

### Database Functions
- `cleanup_expired_sessions()` - Dọn dẹp sessions hết hạn
- `revoke_all_user_sessions()` - Thu hồi tất cả sessions của user
- `is_token_blacklisted()` - Kiểm tra token bị blacklist
- `user_can_access_scan()` - Kiểm tra quyền truy cập scan

## Tech Stack

### Backend
- **FastAPI** + **SQLAlchemy** + **PostgreSQL** 
- **PyJWT** cho JWT token handling
- **passlib[bcrypt]** cho password hashing
- **Alembic** cho database migrations
- **slowapi** cho rate limiting

### Frontend  
- **React** + **Context API** cho state management
- **TypeScript** cho type safety
- Token storage in httpOnly cookies (preferred) hoặc localStorage

## Security Features

### Password Security
- bcrypt hashing với salt rounds >= 12
- Password strength validation (8+ chars, mixed case, numbers)
- Account lockout sau failed attempts

### JWT Security  
- Short access token expiry (15-30 mins)
- Longer refresh token expiry (7-30 days) 
- Token blacklisting mechanism
- JTI (JWT ID) cho unique identification

### Rate Limiting
- Login: 5 attempts/minute/IP
- Registration: 3 attempts/hour/IP  
- API calls: 100 requests/minute/user

### Additional Protection
- HTTPS only in production
- Security headers (HSTS, CSP)
- Input validation & sanitization
- CSRF protection

## API Endpoints

### Authentication
- `POST /api/auth/register` - Đăng ký user mới
- `POST /api/auth/login` - Đăng nhập  
- `POST /api/auth/logout` - Đăng xuất (blacklist token)
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Lấy thông tin user hiện tại

### User Management
- `PUT /api/users/profile` - Cập nhật profile
- `PATCH /api/users/password` - Đổi password
- `GET /api/users/sessions` - Xem active sessions
- `DELETE /api/users/sessions/{id}` - Revoke session

## Implementation Plan

### Phase 1: Database & Core Backend (Week 1)
1. Setup database models và migrations
2. Implement authentication utilities (JWT, password hashing)
3. Create auth services (registration, login, token management)
4. Write unit tests

### Phase 2: API Development (Week 2)  
1. Implement auth API endpoints
2. Add security middleware và rate limiting
3. Integration testing
4. API documentation

### Phase 3: Frontend Integration (Week 3)
1. Create authentication components (Login/Register forms)
2. Implement protected routes
3. Token management và auto-refresh
4. User profile UI

### Phase 4: Security & Testing (Week 4)
1. Security hardening và penetration testing
2. Comprehensive test coverage
3. Performance optimization
4. Documentation completion

## Tích Hợp Với Hệ Thống Hiện Tại

### Scan Ownership
- Thêm `user_id` foreign key vào scans table
- Support anonymous scans (guest mode)
- Scan visibility: private, public, organization, unlisted

### Protected Routes
- All scan operations require authentication (trừ public scans)
- User chỉ có thể xem/edit scans của mình hoặc public scans
- Admin có thể truy cập tất cả scans

### Backward Compatibility
- Existing scans được assign cho admin user
- API endpoints vẫn hoạt động với optional authentication
- Gradual migration sang authenticated-only features

## Environment Configuration

```env
# JWT Settings
JWT_SECRET_KEY=<strong-random-key>
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Security
BCRYPT_ROUNDS=12
RATE_LIMIT_ENABLED=true

# Database  
DATABASE_URL=postgresql://user:pass@host:port/db
```

## Future Enhancements

### Phase 2 Features
- Social login (Google, GitHub)
- Two-factor authentication (2FA)
- Email verification workflow
- Password reset qua email
- Admin panel cho user management

### Advanced Features
- OAuth2 provider capabilities
- API key management
- Audit logging
- Role-based access control (RBAC)
- Multi-tenant support

---

**Ưu tiên cao**: Security, User experience, Backward compatibility  
**Timeline**: 4 weeks for complete implementation  
**Dependencies**: PostgreSQL database, existing FastAPI backend

*Created: 2025-01-28* 