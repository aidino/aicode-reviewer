ISSUE: Authentication logout sau khi refresh (F5) trình duyệt
User đăng nhập thành công vào dashboard, nhưng khi refresh trang (F5) hoặc reload trình duyệt, màn hình tự động redirect về login page.

NGUYÊN NHÂN:
1. Inconsistent token storage keys: ApiService sử dụng 'access_token' nhưng AuthContext kiểm tra qua apiService.getAuthToken()
2. AuthContext.checkAuth() quá strict: logout user khi gặp network error hoặc timeout, thay vì giữ user logged in với existing token
3. Race condition: Nếu auth check thất bại do network, user bị logout ngay cả khi token còn hợp lệ
4. Missing user state restoration: Không restore user data từ localStorage khi có valid token

RESOLVE:
1. Đảm bảo token được restore đúng trong ApiService constructor
2. Sửa AuthContext.checkAuth() để ít strict hơn với network errors
3. Restore user data từ localStorage khi có valid token nhưng auth check timeout
4. Thêm fallback mechanism khi network request thất bại
5. Implement proper loading state để tránh premature logout

==========
