# **Dashboard Testing Quick Guide**

## **🚀 Quick Start**

### **1. Start Services**
```bash
# Terminal 1: Backend
cd /home/dino/Documents/aicode-reviewer
source venv/bin/activate
python -m uvicorn src.webapp.backend.api.main:app --reload --port 8000

# Terminal 2: Frontend  
cd src/webapp/frontend
npm run dev
```

### **2. Verify Services**
```bash
# Test backend
curl http://localhost:8000/api/dashboard/summary

# Test frontend
curl http://localhost:5173/dashboard
```

### **3. Open Dashboard**
```
Browser: http://localhost:5173/dashboard
```

---

## **✅ Test Checklist**

### **Infrastructure Tests**
- [ ] Backend API (port 8000) responds
- [ ] Frontend dev server (port 5173) responds  
- [ ] API proxy `/api/*` routes work
- [ ] Dashboard route `/dashboard` loads

### **Dashboard Features**
- [ ] Page loads without errors
- [ ] System health shows "healthy"
- [ ] Metrics display realistic data
- [ ] **NEW:** Button "➕ New Scan" hiển thị màu xanh lá trong header
- [ ] **NEW:** Click "New Scan" chuyển đến `/create-scan`
- [ ] Time range selector works (7d, 30d, 90d, 1y)
- [ ] Refresh button updates data
- [ ] Charts render properly
- [ ] Recent activity feeds show data
- [ ] Navigation links work

### **Responsive Design**
- [ ] Desktop layout (1200px+)
- [ ] Tablet layout (768px-1200px)
- [ ] Mobile layout (<768px)
- [ ] Touch interactions work

---

## **📊 Expected Data**

### **Metrics**
- **Total Scans:** ~49
- **Total Findings:** ~196  
- **System Health:** healthy
- **Uptime:** 0d 0h 0m
- **Version:** 1.0.0

### **API Responses**
- **Dashboard Summary:** ~14,661 characters
- **Health Check:** status, timestamp, version, uptime, metrics, components

---

## **🐛 Common Issues & Solutions**

### **Frontend Build Errors**
```bash
cd src/webapp/frontend
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
npm run build
```

### **Backend Import Errors**
```bash
source venv/bin/activate
pip install -r requirements.txt
python -c "from src.webapp.backend.api.main import app; print('Import successful')"
```

### **Port Conflicts**
```bash
# Check ports
lsof -i :5173
lsof -i :8000

# Kill processes
pkill -f uvicorn
pkill -f vite
```

---

## **🎯 Manual Testing Steps**

### **1. Basic Functionality**
1. Open http://localhost:5173/dashboard
2. Verify page loads in <3 seconds
3. Check no console errors
4. Verify all metrics display

### **2. Interactive Features**
1. **NEW:** Click button "➕ New Scan" và verify chuyển đến `/create-scan`
2. Test time range dropdown
3. Click refresh button
4. Verify data updates
5. Test navigation links

### **3. Visual Verification**
1. Check layout is clean
2. Verify charts render
3. Check responsive design
4. Test hover effects

### **4. Data Accuracy**
1. Compare API data with UI
2. Verify calculations are correct
3. Check timestamp formats
4. Verify status indicators

---

## **📱 Browser Testing**

### **Desktop Browsers**
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (if available)
- [ ] Edge (if available)

### **Mobile Testing**
- [ ] Chrome DevTools mobile simulation
- [ ] iPhone SE (375px)
- [ ] iPad (768px)
- [ ] Large mobile (414px)

---

## **🔧 Debug Commands**

### **Check Services Status**
```bash
# Backend health
curl http://localhost:8000/api/dashboard/health | jq .

# Frontend proxy
curl http://localhost:5173/api/dashboard/summary | jq . | head -20

# Process status
ps aux | grep -E "(uvicorn|vite)"
```

### **View Logs**
```bash
# Backend logs (if running in background)
tail -f uvicorn.log

# Frontend logs
# Check browser console (F12)
```

### **Test Script**
```bash
python test_dashboard.py
```

---

## **✨ Success Criteria**

### **Must Have**
- ✅ Dashboard loads without errors
- ✅ All metrics display realistic data  
- ✅ System health shows "healthy"
- ✅ API endpoints respond correctly
- ✅ Navigation works

### **Should Have**
- ⏳ Charts render properly
- ⏳ Time range filtering works
- ⏳ Refresh updates data
- ⏳ Responsive design adapts
- ⏳ Interactive features work

### **Nice to Have**
- ⏳ Smooth animations
- ⏳ Loading states
- ⏳ Error handling
- ⏳ Accessibility features
- ⏳ Performance optimization

---

**Last Updated:** 2025-05-27  
**Status:** ✅ Infrastructure Complete, ⏳ Manual Testing Pending 