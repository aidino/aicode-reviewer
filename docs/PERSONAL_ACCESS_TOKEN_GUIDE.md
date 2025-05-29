# Personal Access Token (PAT) Guide

## Tổng quan

AI Code Reviewer hỗ trợ clone private repositories thông qua **Personal Access Token (PAT)** của GitHub, GitLab, và Bitbucket. Token chỉ được sử dụng trong quá trình clone và **không được lưu trữ** trong hệ thống.

## 🔐 Bảo mật

- ✅ Token chỉ dùng để clone repository một lần
- ✅ Token không được lưu vào database
- ✅ Token không được log ra console/file
- ✅ Token được xóa khỏi memory sau khi sử dụng
- ⚠️ **Không bao giờ commit token vào code**

## 📋 Hướng dẫn tạo GitHub Personal Access Token

### Bước 1: Truy cập GitHub Settings
1. Đăng nhập GitHub → Click avatar → **Settings**
2. Sidebar trái → **Developer settings**
3. **Personal access tokens** → **Tokens (classic)**

### Bước 2: Tạo Token mới
1. Click **Generate new token** → **Generate new token (classic)**
2. **Note**: Đặt tên mô tả (ví dụ: "AI Code Reviewer")
3. **Expiration**: Chọn thời hạn phù hợp (30 days, 90 days, custom)

### Bước 3: Chọn quyền (Scopes)
Chỉ cần quyền tối thiểu:
- ✅ **repo** (Full control of private repositories)
  - Bao gồm: `repo:status`, `repo_deployment`, `public_repo`, `repo:invite`

### Bước 4: Generate và Copy
1. Click **Generate token**
2. **Copy token ngay lập tức** (chỉ hiển thị 1 lần)
3. Lưu token an toàn (password manager, environment variable)

## 🔧 Sử dụng trong AI Code Reviewer

### Frontend (Add Repository Modal)
```typescript
// User nhập token vào form
const formData = {
  repo_url: "https://github.com/user/private-repo",
  access_token: "ghp_xxxxxxxxxxxxxxxxxxxx" // Optional
}

// Gửi lên backend
fetch('/api/repositories/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${userToken}`
  },
  body: JSON.stringify(formData)
})
```

### Backend API
```python
# Repository service sử dụng token để clone
def clone_repository(repo_url: str, access_token: str = None) -> str:
    if access_token:
        # Inject token vào URL cho HTTPS clone
        clone_url = repo_url.replace(
            "https://", 
            f"https://{access_token}:x-oauth-basic@"
        )
    else:
        clone_url = repo_url
    
    # Clone repository
    Repo.clone_from(clone_url, tmp_dir)
```

## 🌐 Hỗ trợ các Platform

### GitHub
- **URL format**: `https://github.com/user/repo`
- **Token format**: `ghp_xxxxxxxxxxxxxxxxxxxx`
- **Scope cần thiết**: `repo`

### GitLab (Coming Soon)
- **URL format**: `https://gitlab.com/user/repo`
- **Token format**: `glpat-xxxxxxxxxxxxxxxxxxxx`
- **Scope cần thiết**: `read_repository`

### Bitbucket (Coming Soon)
- **URL format**: `https://bitbucket.org/user/repo`
- **Token format**: App passwords
- **Scope cần thiết**: `Repositories: Read`

## ⚠️ Lưu ý quan trọng

### Cho Developers
1. **Không hardcode token** trong code
2. Sử dụng environment variables cho testing
3. Token có thời hạn → cần renew định kỳ
4. Revoke token ngay khi không cần

### Cho Users
1. Chỉ cấp quyền tối thiểu cần thiết
2. Không chia sẻ token với ai
3. Sử dụng token có thời hạn ngắn
4. Monitor token usage trong GitHub Settings

## 🧪 Testing

### Unit Tests
```python
def test_clone_private_repository_with_token():
    result = clone_repository(
        "https://github.com/user/private-repo",
        access_token="ghp_test_token"
    )
    
    # Verify URL transformation
    expected_url = "https://ghp_test_token:x-oauth-basic@github.com/user/private-repo"
    mock_clone.assert_called_with(expected_url, temp_dir)
```

### Manual Testing
```bash
# Test với public repo (không cần token)
curl -X POST "http://localhost:8000/api/repositories/" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -d '{"repo_url": "https://github.com/octocat/Hello-World"}'

# Test với private repo (cần token)
curl -X POST "http://localhost:8000/api/repositories/" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -d '{
    "repo_url": "https://github.com/user/private-repo",
    "access_token": "ghp_your_token_here"
  }'
```

## 🔍 Troubleshooting

### Lỗi thường gặp

#### 1. "Authentication failed"
```
fatal: could not read Username for 'https://github.com': No such device or address
```
**Nguyên nhân**: Private repo không có token hoặc token sai
**Giải pháp**: Kiểm tra token và quyền

#### 2. "Bad credentials"
```
remote: Invalid username or password
```
**Nguyên nhân**: Token hết hạn hoặc bị revoke
**Giải pháp**: Tạo token mới

#### 3. "Repository not found"
```
fatal: repository 'https://github.com/user/repo.git/' not found
```
**Nguyên nhân**: Repo không tồn tại hoặc không có quyền truy cập
**Giải pháp**: Kiểm tra URL và quyền

### Debug Steps
1. Verify token trong GitHub Settings → Personal access tokens
2. Test token với GitHub API:
   ```bash
   curl -H "Authorization: token YOUR_TOKEN" \
        https://api.github.com/user
   ```
3. Kiểm tra repository permissions
4. Check token expiration date

## 📚 Tài liệu tham khảo

- [GitHub Personal Access Tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [GitLab Personal Access Tokens](https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html)
- [Bitbucket App Passwords](https://support.atlassian.com/bitbucket-cloud/docs/app-passwords/)

---

**Lưu ý**: Tài liệu này được cập nhật cho phiên bản AI Code Reviewer v1.0. Kiểm tra phiên bản mới nhất trong repository. 