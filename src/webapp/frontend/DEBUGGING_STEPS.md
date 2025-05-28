# 🔧 Hướng dẫn Debug Màn Hình Login Trắng

## ✅ Các bước đã thực hiện:
1. ✅ Cleared Vite cache (`rm -rf node_modules/.vite dist .vite`)
2. ✅ Killed all Vite processes và restart dev server
3. ✅ Đơn giản hóa App.tsx (loại bỏ AuthProvider, ThemeProvider, etc.)
4. ✅ Tạo LoginPageSimple component cực đơn giản
5. ✅ Kiểm tra HTML được serve đúng (`<div id="root">` có trong response)
6. ✅ Kiểm tra JavaScript files được compile đúng bởi Vite

## 🔍 Bước tiếp theo - Manual Testing:

### **Bước 1: Mở Browser Developer Tools**
1. Mở trình duyệt (Chrome/Firefox/Edge)
2. Đi tới: http://localhost:5173
3. Nhấn **F12** để mở Developer Tools
4. Chuyển tới tab **Console**

### **Bước 2: Kiểm tra trang Home**
- URL: http://localhost:5173
- **Kết quả mong đợi:** Thấy "🏠 Home Page Working!" và link "Go to Login"
- **Nếu thấy trang trắng:** Xem Console có error gì

### **Bước 3: Kiểm tra trang Login**
- URL: http://localhost:5173/login
- **Kết quả mong đợi:** Thấy "🔐 Simple Login Page" với form đơn giản
- **Nếu thấy trang trắng:** Xem Console có error gì

### **Bước 4: Sử dụng Standalone Test Page**
- URL: http://localhost:5173/standalone-test.html
- Trang này sẽ tự động kiểm tra và hiển thị lỗi nếu có

### **Bước 5: Clear Browser Cache**
Nếu vẫn thấy trang trắng:
1. **Chrome:** Ctrl+Shift+R (hard refresh)
2. **Firefox:** Ctrl+F5
3. **Hoặc:** Developer Tools > Network tab > click "Disable cache" checkbox

## 🚨 Lỗi thường gặp:

### **Lỗi 1: JavaScript Runtime Error**
```
Uncaught Error: Minified React error
```
**Giải pháp:** Xem error message chi tiết, thường do import sai

### **Lỗi 2: Module Not Found**
```
Failed to resolve module specifier
```
**Giải pháp:** Kiểm tra file path và import statements

### **Lỗi 3: React Router Error**
```
Error: useRoutes() may be used only in the context of a <Router> component
```
**Giải pháp:** Đảm bảo Router wrapper đúng cách

### **Lỗi 4: CSS Loading Error**
```
Failed to load resource: net::ERR_FILE_NOT_FOUND
```
**Giải pháp:** Kiểm tra CSS import paths

## 🔧 Debug Commands:

### **Kiểm tra Dev Server**
```bash
curl -I http://localhost:5173
# Kết quả: HTTP/1.1 200 OK
```

### **Kiểm tra Login Page HTML**
```bash
curl -s http://localhost:5173/login | grep "root"
# Kết quả: <div id="root"></div>
```

### **Kiểm tra Console Logs**
Trong Browser Console, gõ:
```javascript
// Kiểm tra React
console.log('React:', typeof React);

// Kiểm tra Root element
console.log('Root:', document.getElementById('root'));

// Kiểm tra nội dung đã render
console.log('Root content:', document.getElementById('root').innerHTML);
```

## 📞 Báo cáo kết quả:

Sau khi thực hiện các bước trên, hãy báo cáo:

1. **Console có error gì không?** (copy paste error message)
2. **Trang Home (/) có hiển thị được không?**
3. **Trang Test (/test) có hiển thị được không?**
4. **Standalone test page có hoạt động không?**
5. **Hard refresh (Ctrl+Shift+R) có giúp được không?**

## 🎯 Tạm thời sử dụng LoginPageTest:

Nếu vẫn không được, có thể sử dụng LoginPageTest (đã hoạt động trước đó):
- Uncomment `import { LoginPageTest }` trong App.tsx
- Thay `<LoginPageSimple />` bằng `<LoginPageTest />` 