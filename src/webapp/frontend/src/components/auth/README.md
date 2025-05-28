# Authentication System - AI Code Reviewer Frontend

Hệ thống authentication toàn diện cho AI Code Reviewer với modern UI/UX design theo PLANNING.md.

## 📋 Tổng quan

Hệ thống authentication bao gồm:
- **JWT-based authentication** với automatic token refresh
- **Modern Soft UI design** với responsive layout
- **Comprehensive validation** và error handling
- **Protected routing** với loading states
- **Session management** với multi-device support
- **Profile management** với password changes

## 🏗️ Kiến trúc

```
src/components/auth/
├── __tests__/               # Unit tests
│   ├── LoginForm.test.tsx
│   ├── RegisterForm.test.tsx
│   └── ProtectedRoute.test.tsx
├── AuthModal.tsx           # Modal kết hợp login/register
├── LoginForm.tsx           # Form đăng nhập
├── RegisterForm.tsx        # Form đăng ký
├── ProtectedRoute.tsx      # Route protection component
├── UserProfile.tsx         # Profile management UI
└── index.ts               # Component exports

src/contexts/
└── AuthContext.tsx        # Global authentication state

src/hooks/
└── useAuth.ts             # Authentication hooks

src/services/
└── api.ts                 # API service với auth endpoints
```

## 🔧 Components

### AuthModal
Modal component kết hợp LoginForm và RegisterForm với tab switching.

```tsx
import { AuthModal } from './components/auth';

<AuthModal
  isOpen={showModal}
  onClose={() => setShowModal(false)}
  initialMode="login"
  onSuccess={() => console.log('Success!')}
/>
```

**Props:**
- `isOpen: boolean` - Modal visibility
- `onClose: () => void` - Close callback
- `initialMode?: 'login' | 'register'` - Initial form mode
- `onSuccess?: () => void` - Success callback

### LoginForm
Modern login form với validation và remember me functionality.

```tsx
import { LoginForm } from './components/auth';

<LoginForm
  onSuccess={() => navigate('/dashboard')}
  onSwitchToRegister={() => setMode('register')}
/>
```

**Features:**
- Username/password validation
- Show/hide password toggle
- Remember me checkbox
- Social login placeholders (Google, GitHub)
- Error handling với real-time feedback

### RegisterForm
Comprehensive registration form với password confirmation.

```tsx
import { RegisterForm } from './components/auth';

<RegisterForm
  onSuccess={() => navigate('/dashboard')}
  onSwitchToLogin={() => setMode('login')}
/>
```

**Features:**
- Full name, username, email, password fields
- Password confirmation validation
- Terms & conditions acceptance
- Social registration placeholders
- Real-time validation feedback

### ProtectedRoute
Route protection component với authentication checks.

```tsx
import { ProtectedRoute } from './components/auth';

<ProtectedRoute>
  <Dashboard />
</ProtectedRoute>

// Với custom fallback
<ProtectedRoute fallback={<CustomUnauthorized />}>
  <PrivateContent />
</ProtectedRoute>

// HOC version
const ProtectedDashboard = withAuth(Dashboard);
```

**Features:**
- Automatic authentication checking
- Loading states
- Custom fallback content
- Modal-based authentication
- HOC wrapper support

### UserProfile
Complete profile management với tabs cho personal info, password, và sessions.

```tsx
import { UserProfile } from './components/auth';

<UserProfile className="custom-styles" />
```

**Features:**
- Personal information editing
- Password change functionality
- Session management và revocation
- Timezone selection
- Real-time updates

## 🎣 Hooks

### useAuth (Context Hook)
Main authentication hook từ AuthContext.

```tsx
import { useAuth } from './contexts/AuthContext';

const {
  user,              // Current user data
  loading,           // Loading state
  isAuthenticated,   // Authentication status
  login,             // Login function
  register,          // Register function
  logout,            // Logout function
  updateProfile,     // Update profile function
  changePassword,    // Change password function
  refreshToken       // Manual token refresh
} = useAuth();
```

### useUserSessions
Hook for session management operations.

```tsx
import { useUserSessions } from './hooks/useAuth';

const {
  data,              // Sessions array
  loading,           // Loading state
  error,             // Error state
  fetchSessions,     // Fetch sessions function
  revokeSession,     // Revoke specific session
  revokeAllSessions  // Revoke all sessions
} = useUserSessions();
```

### useAuthOperations
Standalone authentication operations (không cập nhật global state).

```tsx
import { useAuthOperations } from './hooks/useAuth';

const {
  loading,
  error,
  login,
  register,
  changePassword,
  updateProfile,
  clearError
} = useAuthOperations();
```

### useAuthValidation
Form validation utilities.

```tsx
import { useAuthValidation } from './hooks/useAuth';

const {
  validateEmail,
  validateUsername,
  validatePassword,
  validatePasswordConfirm,
  validateFullName,
  validateLoginForm,
  validateRegisterForm
} = useAuthValidation();

// Example usage
const validation = validateLoginForm({
  username: 'testuser',
  password: 'password123'
});

if (!validation.isValid) {
  console.log(validation.errors);
}
```

## 🔐 AuthContext

Global authentication state management với useReducer.

### Provider Setup
```tsx
import { AuthProvider } from './contexts/AuthContext';

<AuthProvider>
  <App />
</AuthProvider>
```

### State Management
- **User state**: Current user information
- **Loading state**: Authentication operations
- **Error handling**: API errors và network issues
- **Token management**: Automatic refresh và storage
- **Session tracking**: Multi-device session management

### Features
- **Automatic token refresh**: 14-minute intervals
- **Persistent sessions**: localStorage token storage
- **Error recovery**: Token refresh on API failures
- **Loading states**: UI feedback cho auth operations

## 🎨 Styling

Components sử dụng Soft UI design system với:

### Color Palette
- **Primary**: Deep blue (#1A237E), Electric blue (#2979FF)
- **Accent**: Emerald green (#00C853), Orange (#FF9100)
- **Background**: Light gray (#F5F7FA), White (#FFFFFF)
- **Text**: High contrast, adaptive cho light/dark mode

### CSS Classes
```css
/* Soft UI effects */
.shadow-soft-xl        /* Soft shadow */
.rounded-3xl           /* Rounded corners */
.bg-gradient-to-r      /* Gradient backgrounds */

/* Form styling */
.form-input            /* Input fields */
.btn-soft              /* Soft buttons */
.card-soft             /* Card containers */

/* Loading states */
.animate-spin          /* Loading spinners */
.transition-all        /* Smooth transitions */
```

## 🧪 Testing

Comprehensive test suite với 90%+ coverage.

### Running Tests
```bash
# All authentication tests
npm test src/components/auth src/hooks/useAuth.test.ts

# Individual component tests
npm test src/components/auth/__tests__/LoginForm.test.tsx
npm test src/components/auth/__tests__/RegisterForm.test.tsx
npm test src/components/auth/__tests__/ProtectedRoute.test.tsx

# Hooks tests
npm test src/hooks/__tests__/useAuth.test.ts

# Coverage report
npm run test:coverage
```

### Test Features
- **Component rendering**: All UI elements và states
- **User interactions**: Form submissions, clicks, typing
- **Validation logic**: Form validation và error handling
- **Authentication flows**: Login, register, logout scenarios
- **Loading states**: UI feedback during operations
- **Error handling**: API errors và network failures
- **Mock services**: Complete API mocking

## 🔒 Security Features

### Token Management
- **JWT tokens** với short expiration (15 minutes)
- **Refresh tokens** với longer expiration
- **Automatic refresh** before token expiry
- **Token blacklisting** khi logout

### Session Security
- **Multi-device tracking** với user agent và IP
- **Session revocation** từ UI
- **Automatic cleanup** expired sessions
- **Secure storage** với httpOnly cookies (backend)

### Validation Security
- **Input sanitization** trong form validation
- **Password strength** requirements
- **Rate limiting** (backend implementation)
- **CSRF protection** (backend implementation)

## 📝 API Integration

Authentication system tích hợp với FastAPI backend.

### Endpoints
```typescript
POST /auth/register     // User registration
POST /auth/login        // User login
POST /auth/logout       // User logout
GET  /auth/me          // Get current user
PUT  /auth/me          // Update profile
POST /auth/refresh     // Refresh token
POST /auth/change-password  // Change password
GET  /auth/sessions    // Get user sessions
DELETE /auth/sessions/{id}  // Revoke session
DELETE /auth/sessions  // Revoke all sessions
```

### Error Handling
```typescript
interface ApiError {
  detail: string;
  status_code: number;
}

// Usage
const response = await apiService.login(credentials);
if (response.error) {
  console.error(response.error.detail);
}
```

## 🚀 Usage Examples

### Basic Setup
```tsx
import { 
  AuthProvider, 
  ProtectedRoute, 
  AuthModal 
} from './components/auth';

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<AuthModal />} />
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } />
        </Routes>
      </Router>
    </AuthProvider>
  );
}
```

### Custom Authentication Flow
```tsx
import { useAuth } from './contexts/AuthContext';

function CustomLogin() {
  const { login, loading, user } = useAuth();
  
  const handleLogin = async (credentials) => {
    try {
      await login(credentials);
      navigate('/dashboard');
    } catch (error) {
      console.error('Login failed:', error);
    }
  };
  
  if (user) {
    return <Navigate to="/dashboard" />;
  }
  
  return (
    <form onSubmit={handleLogin}>
      {/* Custom form implementation */}
    </form>
  );
}
```

### Profile Management
```tsx
import { useAuth } from './contexts/AuthContext';

function ProfilePage() {
  const { user, updateProfile, changePassword } = useAuth();
  
  const handleProfileUpdate = async (updates) => {
    await updateProfile(updates);
  };
  
  const handlePasswordChange = async (passwords) => {
    await changePassword(passwords);
  };
  
  return (
    <UserProfile 
      user={user}
      onUpdateProfile={handleProfileUpdate}
      onChangePassword={handlePasswordChange}
    />
  );
}
```

## 🐛 Troubleshooting

### Common Issues

**1. Token Refresh Failures**
```typescript
// Check token storage
const token = localStorage.getItem('access_token');
const refreshToken = localStorage.getItem('refresh_token');

// Manual refresh
const { refreshToken } = useAuth();
await refreshToken();
```

**2. Form Validation Errors**
```typescript
// Use validation hooks
const { validateLoginForm } = useAuthValidation();
const validation = validateLoginForm(formData);

if (!validation.isValid) {
  setErrors(validation.errors);
}
```

**3. Protected Route Issues**
```typescript
// Check authentication status
const { isAuthenticated, loading } = useAuth();

if (loading) return <LoadingSpinner />;
if (!isAuthenticated) return <LoginRequired />;
return <ProtectedContent />;
```

### Debug Mode
```typescript
// Enable debug logging
localStorage.setItem('auth_debug', 'true');

// Check AuthContext state
const authState = useAuth();
console.log('Auth State:', authState);
```

## 📚 References

- [PLANNING.md](../../../../../../PLANNING.md) - Project architecture
- [TASK.md](../../../../../../TASK.md) - Implementation tasks
- [FastAPI Authentication](https://fastapi.tiangolo.com/tutorial/security/) - Backend reference
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/) - Testing approach 