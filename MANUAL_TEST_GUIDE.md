# 🌐 HƯỚNG DẪN MANUAL TEST ENHANCED SOLUTION SUGGESTION AGENT

## **Tổng quan**
Hướng dẫn này sẽ giúp bạn manual test tính năng Enhanced Solution Suggestion Agent mới được thêm vào hệ thống AI Code Reviewer thông qua web browser.

## **🚀 Chuẩn bị**

### **1. Khởi động Backend**
```bash
cd /home/dino/Documents/aicode-reviewer
python -m uvicorn src.webapp.backend.api.main:app --reload --port 8000
```

### **2. Kiểm tra Backend Health**
Mở browser và truy cập: http://localhost:8000/health
- ✅ Kết quả mong đợi: `{"status":"healthy","service":"AI Code Reviewer Backend"}`

## **📱 CÁC URL QUAN TRỌNG**

| URL | Mô tả | Mục đích test |
|-----|-------|---------------|
| http://localhost:8000/docs | Swagger UI API Documentation | Test interactive API endpoints |
| http://localhost:8000/redoc | ReDoc API Documentation | Xem chi tiết API specification |
| http://localhost:8000/api/scans/ | List available scans | Kiểm tra danh sách scan hiện có |
| http://localhost:8000/api/scans/demo_scan_1/report | Demo scan report | Xem report mẫu với enhanced solutions |
| http://localhost:8000/health | Backend health check | Verify backend is running |

## **🔧 MANUAL TEST SCENARIOS**

### **Scenario 1: Kiểm tra API Documentation**

1. **Mở Swagger UI**: http://localhost:8000/docs
2. **Tìm kiếm endpoints liên quan đến Enhanced Solutions**:
   - `POST /api/scans/initiate` - Khởi tạo scan với enhanced settings
   - `GET /api/scans/{scan_id}/report` - Lấy report với enhanced solutions
   - `GET /api/scans/jobs/{job_id}/status` - Monitor scan progress

3. **Kiểm tra request/response schemas**:
   ```json
   // Enhanced scan request example
   {
     "scan_id": "enhanced_test_scan",
     "repo_url": "https://github.com/test/repo",
     "scan_type": "pr",
     "pr_id": 123,
     "settings": {
       "enable_enhanced_solutions": true,
       "max_alternatives": 3,
       "confidence_threshold": 0.7
     }
   }
   ```

### **Scenario 2: Test Existing Demo Report**

1. **Lấy demo report**: http://localhost:8000/api/scans/demo_scan_1/report
2. **Kiểm tra structure của response**:
   - Tìm field `findings` trong response
   - Với mỗi finding, kiểm tra `solution_suggestion`
   - Xác định enhanced solutions có các features:
     ```json
     {
       "confidence_score": 0.85,
       "evidence": [...],
       "alternative_solutions": [...],
       "xai_reasoning": {...},
       "implementation_complexity": "low"
     }
     ```

### **Scenario 3: Test New Enhanced Scan Creation**

1. **Mở Swagger UI**: http://localhost:8000/docs
2. **Navigate đến `POST /scans/initiate`**
3. **Click "Try it out"**
4. **Input enhanced scan request**:
   ```json
   {
     "scan_id": "test_enhanced_2024",
     "repo_url": "https://github.com/example/test-repo", 
     "scan_type": "full_project",
     "settings": {
       "enable_enhanced_solutions": true,
       "max_alternatives": 2,
       "confidence_threshold": 0.8,
       "suggestion_types": [
         "security_fix",
         "performance_optimization",
         "best_practice"
       ]
     }
   }
   ```
5. **Click "Execute"**
6. **Kiểm tra response**:
   - Status code: 200
   - Response có `job_id`
   - Message xác nhận scan initiated

### **Scenario 4: Monitor Scan Progress**

1. **Sử dụng job_id từ Scenario 3**
2. **Test endpoint**: `GET /scans/jobs/{job_id}/status`
3. **Kiểm tra response**:
   ```json
   {
     "job_id": "...",
     "status": "running|completed|failed",
     "progress": 75,
     "current_stage": "llm_analysis",
     "enhanced_features_enabled": true
   }
   ```

### **Scenario 5: Validate Enhanced Solution Structure**

1. **Sau khi scan complete, lấy report**: `GET /scans/{scan_id}/report`
2. **Kiểm tra enhanced solution fields**:

   #### **🥇 Primary Solution**
   ```json
   {
     "approach_name": "Parameterized Query Implementation",
     "description": "Replace string concatenation...",
     "reasoning": {
       "primary_reason": "Parameterized queries provide...",
       "confidence_score": 0.95,
       "evidence": [
         {
           "type": "security_principle",
           "description": "OWASP Top 10 recommendation"
         }
       ],
       "assumptions": ["Database driver supports parameters"],
       "limitations": ["Cannot parameterize table names"]
     },
     "implementation_complexity": "low",
     "code_suggestions": [...]
   }
   ```

   #### **🔄 Alternative Solutions**
   ```json
   {
     "alternative_solutions": [
       {
         "approach_name": "ORM-Based Query Builder",
         "confidence_score": 0.82,
         "implementation_complexity": "medium",
         "pros_cons": {
           "pros": ["Higher abstraction", "Type safety"],
           "cons": ["Learning curve", "Performance overhead"]
         }
       }
     ]
   }
   ```

   #### **🧠 XAI Reasoning**
   ```json
   {
     "overall_reasoning": {
       "confidence_score": 0.93,
       "confidence_level": "HIGH",
       "primary_reason": "Security vulnerability requires immediate attention",
       "evidence": [...],
       "assumptions": [...],
       "limitations": [...]
     }
   }
   ```

## **✅ VALIDATION CHECKLIST**

### **API Endpoints**
- [ ] `/health` trả về status healthy
- [ ] `/docs` hiển thị Swagger UI đầy đủ 
- [ ] `/scans/` liệt kê các scan available
- [ ] `/scans/demo_scan_1/report` trả về valid JSON report

### **Enhanced Solution Features**
- [ ] **Confidence Scoring**: Numerical scores 0.0-1.0
- [ ] **Multiple Alternatives**: Ít nhất 1-3 alternative solutions
- [ ] **Evidence-Based Reasoning**: Evidence array với type và description
- [ ] **Pros/Cons Analysis**: Detailed pros/cons cho mỗi approach
- [ ] **Implementation Complexity**: Low/Medium/High assessment
- [ ] **XAI Transparency**: Clear reasoning và assumptions

### **Error Handling**
- [ ] Invalid scan_id trả về 404 với error message rõ ràng
- [ ] Malformed request trả về 422 với validation errors
- [ ] Network timeouts được handle gracefully

## **🛠️ ADVANCED TESTING**

### **Test 1: Confidence Threshold Behavior**
```bash
# Test với confidence threshold cao
curl -X POST "http://localhost:8000/scans/initiate" \
  -H "Content-Type: application/json" \
  -d '{
    "scan_id": "high_confidence_test",
    "confidence_threshold": 0.9,
    "settings": {"enable_enhanced_solutions": true}
  }'
```

### **Test 2: Max Alternatives Limit**
```bash
# Test với nhiều alternatives
curl -X POST "http://localhost:8000/scans/initiate" \
  -H "Content-Type: application/json" \
  -d '{
    "scan_id": "multiple_alternatives_test", 
    "settings": {
      "enable_enhanced_solutions": true,
      "max_alternatives": 5
    }
  }'
```

### **Test 3: Suggestion Type Filtering**
```bash
# Test chỉ với security suggestions
curl -X POST "http://localhost:8000/scans/initiate" \
  -H "Content-Type: application/json" \
  -d '{
    "scan_id": "security_only_test",
    "settings": {
      "enable_enhanced_solutions": true,
      "suggestion_types": ["security_fix"]
    }
  }'
```

## **🐛 TROUBLESHOOTING**

### **Backend không respond**
```bash
# Kiểm tra process
ps aux | grep uvicorn

# Restart backend
pkill -f uvicorn
python -m uvicorn src.webapp.backend.api.main:app --reload --port 8000
```

### **API trả về 404/500 errors**
1. Kiểm tra backend logs trong terminal
2. Verify rằng enhanced agents đã được import đúng
3. Check database/file permissions

### **Enhanced solutions không hiển thị**
1. Verify `enable_enhanced_solutions: true` trong request
2. Kiểm tra agent có được initialize với enhanced capabilities
3. Check LLM orchestrator connection

## **📊 EXPECTED RESULTS**

### **Successful Enhanced Solution**
```json
{
  "finding_id": "sql_injection_001",
  "suggestion_type": "security_fix",
  "confidence_score": 0.95,
  "processing_time_ms": 1200,
  "primary_solution": {
    "approach_name": "Parameterized Query Implementation",
    "implementation_complexity": "low",
    "reasoning": {
      "confidence_score": 0.95,
      "evidence": [{"type": "security_principle", "description": "OWASP Top 10"}]
    }
  },
  "alternative_solutions": [
    {
      "approach_name": "ORM-Based Query Builder",
      "confidence_score": 0.82
    }
  ],
  "overall_reasoning": {
    "primary_reason": "SQL injection is critical security vulnerability",
    "confidence_level": "HIGH"
  }
}
```

## **🎯 SUCCESS CRITERIA**

1. **✅ All API endpoints respond correctly**
2. **✅ Enhanced solutions contain XAI features**
3. **✅ Multiple alternatives are generated when enabled**
4. **✅ Confidence scores are realistic (0.3-0.98 range)**
5. **✅ Error handling works for invalid inputs**
6. **✅ Performance is acceptable (<5s for simple scans)**

## **📝 MANUAL TEST REPORT TEMPLATE**

```
## Enhanced Solution Suggestion Agent Test Report

**Date**: [Date]
**Tester**: [Name]
**Backend Version**: [Version]

### API Health Check
- [ ] Health endpoint accessible
- [ ] Swagger UI loads completely
- [ ] Authentication working (if applicable)

### Enhanced Solution Features
- [ ] Confidence scoring functional
- [ ] Multiple alternatives generated
- [ ] XAI reasoning present
- [ ] Evidence-based analysis working
- [ ] Implementation complexity assessed

### Performance
- Scan initiation time: ___ms
- Report generation time: ___ms
- Average confidence score: ___

### Issues Found
1. [Issue description]
2. [Issue description]

### Recommendations
1. [Recommendation]
2. [Recommendation]
```

---

**🎉 Kết luận**: Enhanced Solution Suggestion Agent cung cấp khả năng XAI tiên tiến với multiple alternatives, confidence scoring, và evidence-based reasoning, giúp developers hiểu rõ hơn về các giải pháp được đề xuất và đưa ra quyết định thông minh hơn. 