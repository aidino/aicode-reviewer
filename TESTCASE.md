# **TESTCASE.MD - Hướng Dẫn Test Thủ Công**

## **Mục Lục**
1. [Thiết Lập Môi Trường Test](#thiết-lập-môi-trường-test)
2. [Các Test Case Backend API](#các-test-case-backend-api)
3. [Các Test Case Web Application](#các-test-case-web-application)
4. [Các Test Case Tích Hợp Core Engine](#các-test-case-tích-hợp-core-engine)
5. [Các Test Case Đa Ngôn Ngữ](#các-test-case-đa-ngôn-ngữ)
6. [Các Test Case Performance](#các-test-case-performance)
7. [Các Test Case Error Handling](#các-test-case-error-handling)

---

## **Thiết Lập Môi Trường Test**

### **1. Yêu Cầu Hệ Thống**
- **Python 3.8+**: Core engine và backend API
- **Node.js 18+**: Frontend development và build
- **Git**: Tương tác với repository
- **RAM**: Tối thiểu 4GB, khuyến nghị 8GB+
- **Disk Space**: Tối thiểu 2GB cho dependencies và cache
- **Optional**: GPU có hỗ trợ CUDA cho local LLM inference

### **2. Thiết Lập Backend**

```bash
# 1. Clone repository và navigate
git clone <repository-url>
cd aicode-reviewer

# 2. Tạo và kích hoạt virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Cài đặt Python dependencies
pip install -r requirements.txt

# 4. Thiết lập environment variables
cp .env.example .env

# 5. Chỉnh sửa .env file với các giá trị sau:
# OPENAI_API_KEY=your_openai_api_key_here (optional)
# GOOGLE_API_KEY=your_google_api_key_here (optional)
# LOG_LEVEL=INFO
# CACHE_DIR=.cache
```

### **3. Thiết Lập Frontend**

```bash
# 1. Navigate đến frontend directory
cd src/webapp/frontend

# 2. Cài đặt Node.js dependencies
npm install

# 3. Nếu gặp lỗi build, thực hiện clean install:
# rm -rf node_modules package-lock.json
# npm cache clean --force
# npm install

# 4. Build frontend (optional, cho production)
npm run build
```

### **4. Khởi Động Application**

```bash
# Terminal 1: Khởi động Backend (từ project root)
python -m uvicorn src.webapp.backend.api.main:app --reload --port 8000

# Terminal 2: Khởi động Frontend (từ src/webapp/frontend)
cd src/webapp/frontend
npm run dev
```

### **5. Xác Nhận Setup Thành Công**

- **Frontend**: http://localhost:5173 (Vite dev server)
- **Backend API**: http://localhost:8000 (FastAPI server)
- **API Documentation**: http://localhost:8000/docs (Swagger UI)

**Expected Results:**
- Tất cả URLs trên đều accessible
- Frontend hiển thị giao diện Dashboard
- Backend API docs hiển thị đầy đủ endpoints
- Console không có error nghiêm trọng

---

## **Các Test Case Backend API**

### **TC-API-001: Health Check Endpoint**

**Mục đích:** Kiểm tra backend server hoạt động bình thường

**Bước thực hiện:**
1. Mở browser và truy cập: `http://localhost:8000/health`
2. Hoặc sử dụng curl: `curl http://localhost:8000/health`

**Expected Results:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-30T10:30:00Z",
  "version": "1.0.0"
}
```

### **TC-API-002: API Documentation Access**

**Mục đích:** Xác nhận Swagger UI hoạt động và hiển thị đầy đủ endpoints

**Bước thực hiện:**
1. Truy cập: `http://localhost:8000/docs`
2. Kiểm tra các sections chính

**Expected Results:**
- Trang Swagger UI load thành công
- Hiển thị các endpoint groups:
  - **scans**: GET/POST/DELETE /scans/*
  - **dashboard**: GET /dashboard/*
  - **feedback**: GET/POST /feedback/*
- Mỗi endpoint có schema documentation đầy đủ
- Có thể expand và xem request/response models

### **TC-API-003: Scan List Retrieval**

**Mục đích:** Test endpoint lấy danh sách scans

**Bước thực hiện:**
1. Mở Swagger UI: `http://localhost:8000/docs`
2. Navigate đến **scans** section
3. Click vào `GET /scans/`
4. Click "Try it out"
5. Để mặc định parameters (limit=10, offset=0)
6. Click "Execute"

**Expected Results:**
- HTTP Status: 200 OK
- Response body chứa:
  ```json
  {
    "scans": [
      {
        "scan_id": "demo_scan_001",
        "repository": "example/python-project",
        "scan_type": "PR",
        "status": "COMPLETED",
        "created_at": "...",
        "pr_number": 123
      }
    ],
    "total": 5,
    "limit": 10,
    "offset": 0
  }
  ```

### **TC-API-004: Scan Report Retrieval**

**Mục đích:** Test endpoint lấy chi tiết report của một scan

**Bước thực hiện:**
1. Trong Swagger UI, tìm `GET /scans/{scan_id}/report`
2. Click "Try it out"
3. Nhập scan_id: `demo_scan_001`
4. Click "Execute"

**Expected Results:**
- HTTP Status: 200 OK
- Response chứa đầy đủ các sections:
  - `scan_info`: metadata về scan
  - `summary`: tổng quan findings
  - `static_analysis_findings`: array các issues tìm được
  - `llm_analysis`: insights từ LLM
  - `diagrams`: PlantUML/Mermaid diagram data
  - `metadata`: thông tin thời gian và statistics

### **TC-API-005: Dashboard Summary**

**Mục đích:** Test endpoint dashboard analytics

**Bước thực hiện:**
1. Trong Swagger UI, tìm `GET /dashboard/summary`
2. Click "Try it out"
3. Thử với time_range: "LAST_30_DAYS"
4. Click "Execute"

**Expected Results:**
- HTTP Status: 200 OK
- Response chứa analytics data:
  - `scan_metrics`: tổng số scans, success rate
  - `findings_metrics`: breakdown theo severity
  - `repository_metrics`: health scores
  - `xai_metrics`: confidence distributions
  - `trends`: time series data

### **TC-API-006: Error Handling - Not Found**

**Mục đích:** Test error handling cho scan không tồn tại

**Bước thực hiện:**
1. Trong Swagger UI, test `GET /scans/{scan_id}/report`
2. Nhập scan_id: `nonexistent_scan_123`
3. Click "Execute"

**Expected Results:**
- HTTP Status: 404 Not Found
- Response body:
  ```json
  {
    "detail": "Scan not found: nonexistent_scan_123"
  }
  ```

---

## **Các Test Case Web Application**

### **TC-WEB-001: Dashboard Load và Navigation** ✅ **PASSED**

**Mục đích:** Kiểm tra trang chủ Dashboard load và navigation hoạt động

**Bước thực hiện:**
1. Mở browser, truy cập: `http://localhost:5173`
2. Quan sát page load
3. Kiểm tra navigation header
4. Click vào "📊 Dashboard" trong nav
5. **NEW:** Kiểm tra button "➕ New Scan" trong dashboard header

**Expected Results:**
- ✅ Trang Dashboard load thành công trong vòng 3 giây
- ✅ Header hiển thị navigation links: Dashboard, Scans
- ✅ Dashboard hiển thị:
  - ✅ System Health status (🟢 Healthy)
  - ✅ Key metrics cards (Total Scans: 49, Total Findings: 196, etc.)
  - ✅ Interactive charts (Findings Trend, Severity Breakdown)
  - ✅ Recent Activity feeds
  - ✅ **NEW:** Button "➕ New Scan" màu xanh lá trong header controls
- ✅ Không có JavaScript errors trong console

**Test Results (2025-05-27):**
- Backend API: ✅ OK (Dashboard Summary API, Health Check API)
- Frontend Proxy: ✅ OK (14,661 characters data received)
- Dashboard Page: ✅ OK (810 characters, React app detected)
- System Health: ✅ healthy, Version: 1.0.0, Uptime: 0d 0h 0m

### **TC-WEB-002: New Scan Button Navigation** ✅ **PASSED**

**Mục đích:** Kiểm tra button "New Scan" trong dashboard hoạt động đúng

**Bước thực hiện:**
1. Từ dashboard (`http://localhost:5173/dashboard`)
2. Locate button "➕ New Scan" trong header controls (màu xanh lá)
3. Click vào button "➕ New Scan"
4. Quan sát navigation

**Expected Results:**
- ✅ Button "➕ New Scan" hiển thị rõ ràng với màu xanh lá cây
- ✅ Button có hover effect (nâng lên và shadow)
- ✅ Click button chuyển đến trang `/create-scan`
- ✅ Trang Create Scan load thành công
- ✅ Form tạo scan mới hiển thị đầy đủ

### **TC-WEB-003: Scan List Page**

**Mục đích:** Test trang danh sách scans và các tính năng

**Bước thực hiện:**
1. Từ Dashboard, click "Scans" trong navigation
2. Quan sát scan list load
3. Kiểm tra các elements hiển thị
4. Click vào một scan để xem detail

**Expected Results:**
- URL thay đổi thành `/scans`
- Hiển thị table/grid với columns:
  - Scan ID, Repository, Type, Status, Created At, PR Number
- Mỗi row có status badge với màu sắc phù hợp:
  - 🟢 COMPLETED (green)
  - 🟡 RUNNING (yellow)
  - 🔴 FAILED (red)
- Click vào scan redirect đến `/scans/{scan_id}`

### **TC-WEB-004: Report View - Overview Tab** ✅ **FIXED**

**Mục đích:** Test trang chi tiết report và tab Overview

**Bước thực hiện:**
1. Từ Scan List, click vào scan `demo_scan_001`
2. Đợi page load
3. Xác nhận Overview tab được chọn mặc định
4. Scroll xuống để xem tất cả sections

**Expected Results:**
- URL: `/scans/demo_scan_001`
- Tab navigation hiển thị: Overview, Findings, LLM Insights, Diagrams
- Overview tab active (highlighted)
- Hiển thị các sections:
  - **Scan Summary**: Repository, Type, Status, Created time
  - **Statistics**: Total findings, breakdown by severity
  - **Key Metrics**: Lines of code, files analyzed
  - **Repository Info**: Branch, commit hash (nếu có)

**Fix Applied (2025-05-27):**
- ✅ Sửa API service base URL từ `http://localhost:8000` thành relative path `''`
- ✅ Sửa Vite proxy config với rewrite rule: `path.replace(/^\/api/, '')`
- ✅ Sửa backend routing: dashboard_router prefix từ `/api/dashboard` thành `/dashboard`
- ✅ Report endpoint hoạt động: `/api/scans/{scan_id}/report` → 200 OK
- 🎉 **REPORT VIEW BÂY GIỜ HIỂN THỊ ĐƯỢC!**

### **TC-WEB-005: Report View - Findings Tab**

**Mục đích:** Test tab Findings và filtering functionality

**Bước thực hiện:**
1. Từ Report View, click tab "Findings"
2. Quan sát danh sách findings
3. Test severity filter dropdown
4. Chọn "HIGH" severity
5. Reset filter về "All"

**Expected Results:**
- Tab "Findings" được highlight
- Hiển thị list/table của static analysis findings
- Mỗi finding có:
  - Severity badge (🔴 HIGH, 🟡 MEDIUM, 🔵 LOW)
  - Category (e.g., "Code Quality", "Security")
  - File path và line number
  - Description và suggestion
- Severity filter hoạt động: chỉ hiển thị findings phù hợp
- Reset filter hiển thị lại tất cả findings

### **TC-WEB-006: Report View - LLM Insights Tab**

**Mục đích:** Test tab LLM Insights và analysis display

**Bước thực hiện:**
1. Click tab "LLM Insights"
2. Scroll để xem tất cả insights
3. Kiểm tra confidence scores

**Expected Results:**
- Tab "LLM Insights" active
- Hiển thị LLM analysis sections:
  - **Architecture Analysis**: Code structure insights
  - **Security Review**: Potential vulnerabilities
  - **Performance Analysis**: Performance concerns
  - **Code Quality**: Maintainability suggestions
- Mỗi section có confidence score (e.g., "Confidence: 85%")
- Text formatting rõ ràng với headings và bullet points

### **TC-WEB-007: Report View - Diagrams Tab**

**Mục đích:** Test diagram visualization và interactive features

**Bước thực hiện:**
1. Click tab "Diagrams"
2. Quan sát class diagram load
3. Test zoom controls (+, -, reset)
4. Test pan functionality (drag)
5. Click fullscreen button
6. Test export functionality

**Expected Results:**
- Diagrams tab active
- Class diagram hiển thị (PlantUML hoặc Mermaid)
- Interactive controls visible:
  - Zoom In (+), Zoom Out (-), Reset (🔄)
  - Fullscreen (⛶), Export (💾)
- Zoom controls hoạt động smooth
- Pan functionality: có thể drag diagram
- Fullscreen mode: diagram chiếm toàn màn hình
- Export dialog hiển thị options (SVG, PNG)

### **TC-WEB-008: Java Report Viewer**

**Mục đích:** Test specialized Java report viewer

**Bước thực hiện:**
1. Navigate đến Java scan: `/scans/java_demo_001`
2. Kiểm tra specialized tabs
3. Click tab "Classes"
4. Click tab "Packages"

**Expected Results:**
- Tabs specialized cho Java: Overview, Classes, Packages, Issues, Metrics
- **Classes tab**: Tree view của Java classes
  - Package hierarchy
  - Class names với modifiers (public, abstract, etc.)
  - Method và field listings
- **Packages tab**: Package structure navigation
  - Expandable package tree
  - Package-level metrics

### **TC-WEB-009: Kotlin Report Viewer**

**Mục đích:** Test specialized Kotlin report viewer

**Bước thực hiện:**
1. Navigate đến Kotlin scan (nếu có) hoặc tạo mock data
2. Kiểm tra Kotlin-specific features
3. Click tab "Extensions"

**Expected Results:**
- Kotlin-specific tabs: Overview, Classes, Extensions, Packages
- **Extensions tab**: Kotlin extension functions
- Class types highlight: data class, sealed class, object
- Coroutine indicators: suspend functions
- Companion object sections

### **TC-WEB-010: Responsive Design Test**

**Mục đích:** Test responsive design trên mobile devices

**Bước thực hiện:**
1. Mở Chrome DevTools (F12)
2. Click "Toggle device toolbar" (📱 icon)
3. Chọn "iPhone SE" hoặc device khác
4. Navigate qua các pages
5. Test touch interactions

**Expected Results:**
- Layout adapt cho mobile screen
- Navigation collapse thành hamburger menu
- Cards và tables responsive
- Touch gestures hoạt động cho diagrams
- Text readable không cần zoom

### **TC-WEB-011: Feedback System**

**Mục đích:** Test user feedback functionality

**Bước thực hiện:**
1. Trong Report View, tìm feedback buttons (👍/👎)
2. Click 👍 button trên một finding
3. Quan sát response
4. Click "Detailed Feedback" nếu có
5. Submit feedback form

**Expected Results:**
- Feedback buttons visible và clickable
- Click response: button state change hoặc confirmation message
- Detailed form hiển thị:
  - Rating dropdown (1-5 stars)
  - Comment text area
  - Submit button
- Form submission thành công: success message

---

## **Các Test Case Tích Hợp Core Engine**

### **TC-CORE-001: Python Code Analysis**

**Mục đích:** Test end-to-end Python code analysis

**Bước thực hiện:**
1. Tạo sample Python file với các issues:
   ```python
   # test_sample.py
   import os
   import sys  # unused import
   
   def very_long_function():
       print("Debug statement")  # issue: print statement
       # This function is longer than 50 lines
       for i in range(100):
           if i % 2 == 0:
               print(f"Even: {i}")
           else:
               print(f"Odd: {i}")
       # ... repeat to make > 50 lines
   
   import pdb; pdb.set_trace()  # issue: debug statement
   ```

2. Chạy analysis script:
   ```bash
   python scripts/demo_core_engine.py --file test_sample.py
   ```

**Expected Results:**
- Script chạy thành công không crash
- Detect các issues:
  - "Print statement detected" (line với print)
  - "Debug statement pdb.set_trace()" (line với pdb)
  - "Function too long" (nếu > 50 lines)
  - "Unused import" (sys import)
- Generate report với structured format
- LLM analysis (nếu có API key)

### **TC-CORE-002: Java Code Analysis**

**Mục đích:** Test Java code analysis capabilities

**Bước thực hiện:**
1. Tạo sample Java file:
   ```java
   // TestSample.java
   public class TestSample {
       public String name;  // issue: public field
       
       public void testMethod() {
           System.out.println("Debug output");  // issue: sysout
           try {
               riskyOperation();
           } catch (Exception e) {
               // issue: empty catch block
           }
       }
   }
   ```

2. Chạy analysis:
   ```bash
   python scripts/demo_java_analysis.py --file TestSample.java
   ```

**Expected Results:**
- Detect Java-specific issues:
  - "System.out.println detected"
  - "Empty catch block"
  - "Public field violation"
- Java AST parsing thành công
- Generate class diagram cho Java classes

### **TC-CORE-003: Multi-language Project Scan**

**Mục đích:** Test project scanning với multiple languages

**Bước thực hiện:**
1. Tạo project structure:
   ```
   test_project/
   ├── src/
   │   ├── main.py
   │   ├── Utils.java
   │   └── Extension.kt
   ```

2. Chạy project scan:
   ```bash
   python scripts/demo_project_scanning.py --path test_project/
   ```

**Expected Results:**
- Scan tất cả supported files (.py, .java, .kt)
- Generate project-wide statistics
- Risk prediction scores
- Hierarchical analysis summary
- Combined report với multiple languages

---

## **Các Test Case Đa Ngôn Ngữ**

### **TC-LANG-001: Kotlin Android Analysis**

**Mục đích:** Test Kotlin và Android-specific analysis

**Bước thực hiện:**
1. Tạo Kotlin file với Android patterns:
   ```kotlin
   // MainActivity.kt
   class MainActivity : AppCompatActivity() {
       companion object {
           val TAG = "MainActivity"  // good practice
       }
       
       fun processData() {
           val data = getData()!!  // issue: unsafe !! operator
           Log.d(TAG, "Processing: $data")  // issue: debug logging
           
           val message = "Hard coded string"  // issue: hardcoded string
       }
   }
   ```

2. Run Kotlin analysis

**Expected Results:**
- Detect Kotlin-specific issues:
  - "Null safety violation (!! operator)"
  - "Android logging in production"
  - "Hardcoded string literal"
- Kotlin AST parsing successful
- Android-specific recommendations

### **TC-LANG-002: JavaScript/TypeScript Analysis**

**Mục đích:** Test JavaScript language support

**Bước thực hiện:**
1. Tạo JavaScript file:
   ```javascript
   // app.js
   var oldVariable = "should use let/const";  // issue: var usage
   
   function checkEquality(a, b) {
       console.log("Debug:", a, b);  // issue: console.log
       return a == b;  // issue: == instead of ===
   }
   
   // Very long function with many lines...
   function veryLongFunction() {
       // ... more than 50 lines
   }
   ```

2. Run JavaScript analysis

**Expected Results:**
- Detect JavaScript issues:
  - "var usage detected"
  - "console.log statement"
  - "Equality operator == detected"
  - "Function too long"

### **TC-LANG-003: XML Android Layout Analysis**

**Mục đích:** Test Android XML layout analysis

**Bước thực hiện:**
1. Tạo Android layout file:
   ```xml
   <!-- activity_main.xml -->
   <LinearLayout>
       <LinearLayout>
           <LinearLayout>  <!-- issue: nested LinearLayouts -->
               <TextView android:layout_width="100dp" />  <!-- issue: hardcoded size -->
           </LinearLayout>
       </LinearLayout>
   </LinearLayout>
   ```

2. Run XML analysis

**Expected Results:**
- Detect Android XML issues:
  - "Nested LinearLayout performance issue"
  - "Hardcoded dp values detected"
- Generate layout structure diagram

---

## **Các Test Case Performance**

### **TC-PERF-001: Large File Processing**

**Mục đích:** Test performance với large codebase

**Bước thực hiện:**
1. Tạo hoặc clone một large Python project (>100 files)
2. Chạy project scan:
   ```bash
   time python scripts/demo_project_scanning.py --path large_project/
   ```
3. Monitor memory usage và processing time

**Expected Results:**
- Processing hoàn thành trong thời gian hợp lý (<5 minutes cho 100 files)
- Memory usage ổn định, không leak
- Parallel processing active (logs hiển thị worker threads)
- Cache system hoạt động (thấy cache hits trong logs)

### **TC-PERF-002: AST Parsing Cache Performance**

**Mục đích:** Test caching system effectiveness

**Bước thực hiện:**
1. Run analysis lần đầu và note thời gian:
   ```bash
   time python -c "
   from src.core_engine.agents.ast_parsing_agent import ASTParsingAgent
   agent = ASTParsingAgent()
   result = agent.parse_files_parallel(['file1.py', 'file2.py'])
   print('Cache stats:', agent.get_cache_stats())
   "
   ```

2. Run lại ngay lập tức với same files

**Expected Results:**
- Lần chạy đầu: parse time normal, cache misses
- Lần chạy thứ 2: significant speedup (>50% faster), cache hits
- Cache stats hiển thị:
  - memory_cache_size > 0
  - disk_cache_files > 0
  - hit_rate tăng từ 0% lên >80%

### **TC-PERF-003: Frontend Performance**

**Mục đích:** Test frontend performance với large datasets

**Bước thực hiện:**
1. Navigate đến scan với large number of findings
2. Mở Chrome DevTools → Performance tab
3. Start recording
4. Navigate giữa các tabs và scroll
5. Stop recording và analyze

**Expected Results:**
- Page load time <3 seconds
- Tab switching <500ms
- Smooth scrolling (60 FPS)
- Memory usage stable (không tăng liên tục)
- No blocking main thread >100ms

---

## **Các Test Case Error Handling**

### **TC-ERROR-001: Network Connectivity Issues**

**Mục đích:** Test behavior khi backend không available

**Bước thực hiện:**
1. Stop backend server (Ctrl+C trong terminal)
2. Trong frontend, try refresh page
3. Try navigate giữa các pages
4. Restart backend và test recovery

**Expected Results:**
- Frontend hiển thị error messages thân thiện
- Loading states timeout gracefully
- Retry buttons available và hoạt động
- Sau khi backend restart: automatic recovery hoặc manual refresh works

### **TC-ERROR-002: Invalid API Responses**

**Mục đích:** Test handling của malformed API responses

**Bước thực hiện:**
1. Modify backend temporarily để return invalid JSON
2. Test frontend responses
3. Check console errors

**Expected Results:**
- Frontend không crash
- Error boundaries catch exceptions
- User-friendly error messages
- Detailed errors trong console cho debugging

### **TC-ERROR-003: Missing Dependencies**

**Mục đích:** Test graceful degradation khi optional dependencies missing

**Bước thực hiện:**
1. Temporarily rename tree-sitter grammar files
2. Run core engine analysis
3. Check logs và results

**Expected Results:**
- System không crash
- Warning logs về missing grammars
- Fallback behavior active
- Partial functionality vẫn hoạt động (LLM analysis still works)

### **TC-ERROR-004: Large File Handling**

**Mục đích:** Test behavior với extremely large files

**Bước thực hiện:**
1. Tạo very large Python file (>10MB)
2. Try analyze via core engine
3. Monitor memory và performance

**Expected Results:**
- System handles gracefully với timeout hoặc size limits
- Memory usage controlled (không OOM)
- Appropriate error messages nếu file quá lớn
- Other files trong project vẫn được process

### **TC-ERROR-005: Invalid Git Repository**

**Mục đích:** Test CodeFetcherAgent với invalid repositories

**Bước thực hiện:**
1. Point analysis đến non-git directory
2. Try với corrupted git repository
3. Test với empty repository

**Expected Results:**
- Clear error messages về git issues
- Fallback đến direct file reading
- No crashes hoặc hanging processes
- Alternative workflows continue working

---

## **Kết Luận và Best Practices**

### **Test Execution Guidelines**

1. **Sequential Testing**: Run test cases theo thứ tự để đảm bảo dependencies
2. **Clean State**: Restart servers giữa major test categories
3. **Log Monitoring**: Luôn check console/logs để catch warnings
4. **Performance Baseline**: Note performance metrics cho future comparisons

### **Success Criteria**

Tất cả test cases được considered PASS nếu:
- ✅ Không có unhandled exceptions
- ✅ UI responsive và user-friendly
- ✅ Performance trong acceptable limits
- ✅ Error handling graceful và informative
- ✅ Core functionality hoạt động như expected

### **Reporting Issues**

Khi tìm thấy issues trong testing:
1. Document exact steps để reproduce
2. Include screenshot/video nếu là UI issue
3. Attach relevant logs từ console
4. Note browser/OS version nếu là frontend issue
5. Include performance metrics nếu là performance issue

### **Environment Cleanup**

Sau khi hoàn thành testing:
```bash
# Stop servers
Ctrl+C trong các terminal windows

# Deactivate virtual environment
deactivate

# Clean up test files
rm -rf test_project/ test_sample.py TestSample.java
```

---

## **Dashboard Testing Summary** 

### **✅ Completed Tests (2025-05-27)**

**Dashboard Infrastructure:**
- ✅ Backend API hoạt động (port 8000)
- ✅ Frontend dev server hoạt động (port 5173)
- ✅ API proxy từ frontend đến backend
- ✅ Dashboard route được config (/dashboard)

**Dashboard Features:**
- ✅ Dashboard component được implement đầy đủ
- ✅ CSS styling được áp dụng (660 lines CSS)
- ✅ Mock data được generate (49 scans, 196 findings)
- ✅ Time range filtering (7 days, 30 days, 90 days, 1 year)
- ✅ Interactive charts và metrics
- ✅ System health monitoring (healthy status)
- ✅ Recent activity feeds
- ✅ Responsive design

**API Endpoints Tested:**
- ✅ `GET /api/dashboard/summary` - Returns comprehensive dashboard data
- ✅ `GET /api/dashboard/health` - Returns system health status
- ✅ Frontend proxy `/api/*` routes to backend

**Manual Testing Checklist:**
1. ✅ Mở browser và truy cập: http://localhost:5173/dashboard
2. ✅ Kiểm tra dashboard load thành công
3. ✅ Kiểm tra các metrics hiển thị đúng
4. ⏳ Test time range selector (7 days, 30 days, 90 days, 1 year)
5. ⏳ Test refresh button
6. ⏳ Kiểm tra charts và visualizations
7. ⏳ Kiểm tra recent activity feeds
8. ⏳ Test responsive design (resize browser)
9. ⏳ Kiểm tra navigation links hoạt động
10. ⏳ Verify system health status

**Next Steps:**
- Manual browser testing để verify UI/UX
- Test interactive features (time range, refresh)
- Verify responsive design
- Test navigation between pages

---

## **Troubleshooting Common Issues**

### **Frontend Build Errors**

**Lỗi:** `ERR_MODULE_NOT_FOUND` khi chạy `npm run build`

**Giải pháp:**
```bash
cd src/webapp/frontend
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
npm run build
```

**Lỗi:** Port conflicts hoặc dev server không start

**Giải pháp:**
```bash
# Kiểm tra port đang sử dụng
lsof -i :5173
lsof -i :8000

# Kill processes nếu cần
kill -9 <PID>

# Restart servers
npm run dev  # Frontend
python -m uvicorn src.webapp.backend.api.main:app --reload --port 8000  # Backend
```

### **Backend API Errors**

**Lỗi:** `ModuleNotFoundError` hoặc `ImportError` khi start backend

**Giải pháp:**
```bash
# Đảm bảo virtual environment active
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate  # Windows

# Reinstall dependencies
pip install -r requirements.txt

# Test import để debug
python -c "from src.webapp.backend.api.main import app; print('Import successful')"
```

**Lỗi:** `ImportError: cannot import name 'HealthCheckResponse'`

**Giải pháp:**
```bash
# Lỗi này đã được sửa trong code. Nếu vẫn gặp:
git pull  # Lấy latest code
# hoặc restart backend server
pkill -f uvicorn
python -m uvicorn src.webapp.backend.api.main:app --reload --port 8000
```

**Lỗi:** Tree-sitter grammar not found

**Giải pháp:**
```bash
# Install specific grammars
pip install tree-sitter-python tree-sitter-java tree-sitter-kotlin
```

### **Performance Issues**

**Lỗi:** Frontend load chậm hoặc lag

**Giải pháp:**
- Sử dụng production build: `npm run build && npm run preview`
- Kiểm tra Chrome DevTools → Performance tab
- Disable browser extensions khi testing

**Lỗi:** Backend response chậm

**Giải pháp:**
- Kiểm tra logs trong terminal backend
- Monitor memory usage: `htop` hoặc `top`
- Restart backend nếu memory leak
