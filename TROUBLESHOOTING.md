# 🔧 CSIS - Troubleshooting Guide

## Current Status Check

### ✅ Backend is Running
```
INFO: Uvicorn running on http://0.0.0.0:8000
```
**Status:** WORKING ✅

### ✅ Backend API is Accessible
```bash
curl http://localhost:8000
# Returns: {"message":"CSIS Backend API","version":"1.0.0","status":"running"}
```
**Status:** WORKING ✅

---

## 🔍 What to Check Now

### Step 1: Open Browser Console
1. Go to `http://localhost:3000`
2. Press **F12** to open Developer Tools
3. Click **Console** tab
4. Look for these messages:

**Expected Output:**
```
🔌 Connecting to WebSocket...
✅ WebSocket connected
📹 Camera 1: Camera 1 started
```

**If you see errors:**
- Check if backend is still running
- Make sure port 8000 is not blocked
- Try refreshing the page (Ctrl + Shift + R)

---

### Step 2: Check Connection Status
On the Dashboard, you should see at the top:
- 🟢 **"Connected to AI Backend"** (green) = GOOD ✅
- 🔴 **"Connecting to backend..."** (orange) = Problem ❌

---

### Step 3: Check Network Tab
1. In Developer Tools, click **Network** tab
2. Filter by **WS** (WebSocket)
3. You should see: `ws://localhost:8000/ws`
4. Status should be: **101 Switching Protocols** (green)

---

## 🎥 Webcam Issues

### Why Webcam Might Not Show:

#### Issue 1: Backend Can't Access Webcam
**Check backend console for:**
```
❌ Failed to open video source: 0
```

**Solutions:**
1. Close other apps using webcam (Zoom, Teams, Skype)
2. Check if webcam works in other apps
3. Try restarting backend
4. Check webcam drivers

#### Issue 2: OpenCV Can't Find Webcam
**Test manually:**
```bash
cd backend
python -c "import cv2; cap = cv2.VideoCapture(0); print('Webcam:', cap.isOpened())"
```

**Should print:** `Webcam: True`

**If False:**
- Webcam is being used by another app
- Webcam drivers issue
- Try different camera index (1, 2, etc.)

---

## 🔌 WebSocket Connection Issues

### Problem: "Connecting to backend..." stuck

#### Solution 1: Check Backend
```bash
# Backend should show:
✅ Server ready!
INFO: Uvicorn running on http://0.0.0.0:8000
```

#### Solution 2: Check Firewall
- Windows Firewall might be blocking port 8000
- Allow Python through firewall
- Or temporarily disable firewall for testing

#### Solution 3: Check CORS
Backend has CORS enabled for all origins, so this shouldn't be an issue.

#### Solution 4: Try Different Browser
- Chrome (recommended)
- Firefox
- Edge

---

## 📊 No Data Showing

### Problem: Risk scores stay at 0

#### Reason 1: Camera Not Started
**Check backend console:**
```
✅ Video processor started for camera 1
```

**If not there:**
- WebSocket might not be connected
- API call to start camera failed
- Check browser console for errors

#### Reason 2: No Detections
- YOLOv8 might not detect anything
- Move in front of camera
- Ensure good lighting
- Wait a few seconds

#### Reason 3: Processing Not Running
**Backend should show:**
```
📨 Processing frame for camera 1...
```

---

## 🐛 Common Errors & Fixes

### Error: "Module not found"
**In backend console:**
```
ModuleNotFoundError: No module named 'xxx'
```

**Fix:**
```bash
cd backend
python -m pip install xxx
```

### Error: "Address already in use"
**Port 8000 is busy**

**Fix:**
```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID)
taskkill /PID <PID> /F

# Or change port in main.py:
uvicorn.run(app, host="0.0.0.0", port=8001)
```

### Error: "WebSocket connection failed"
**CORS or network issue**

**Fix:**
1. Check backend is running
2. Try `http://localhost:8000` in browser
3. Check firewall settings
4. Restart both backend and frontend

---

## 🎯 Quick Verification Steps

### 1. Backend Health Check
```bash
curl http://localhost:8000
```
**Expected:** JSON response with "status": "running"

### 2. WebSocket Test
Open browser console and run:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onopen = () => console.log('✅ Connected!');
ws.onerror = (e) => console.error('❌ Error:', e);
```

### 3. Camera API Test
```bash
curl -X POST http://localhost:8000/api/camera/start -F "camera_id=1" -F "source=0"
```
**Expected:** `{"success": true, "message": "Camera 1 started"}`

---

## 📹 Manual Webcam Test

### Test if OpenCV can access webcam:
```python
import cv2

cap = cv2.VideoCapture(0)
if cap.isOpened():
    ret, frame = cap.read()
    if ret:
        print("✅ Webcam working!")
        cv2.imshow('Test', frame)
        cv2.waitKey(0)
    else:
        print("❌ Can't read frame")
else:
    print("❌ Can't open webcam")

cap.release()
cv2.destroyAllWindows()
```

---

## 🔄 Fresh Start Procedure

If nothing works, try this:

### 1. Stop Everything
```bash
# Stop backend (Ctrl+C in backend terminal)
# Stop frontend (Ctrl+C in frontend terminal)
```

### 2. Clear Browser Cache
```
Ctrl + Shift + Delete
Clear cache and cookies
```

### 3. Restart Backend
```bash
cd backend
python main.py
```
**Wait for:** "✅ Server ready!"

### 4. Restart Frontend
```bash
npm start
```

### 5. Hard Refresh Browser
```
Ctrl + Shift + R
```

---

## 📱 What You Should See

### Dashboard Top:
```
🟢 Connected to AI Backend
```

### Camera 1:
```
[Live Webcam Feed]
or
[Camera icon with "Starting webcam..."]
```

### Console:
```
🔌 Connecting to WebSocket...
✅ WebSocket connected
📹 Camera 1: Camera 1 started
```

### Backend Console:
```
✅ Video processor started for camera 1
📨 Processing frame...
```

---

## 🎯 Expected Behavior

### When Working Correctly:

1. **Dashboard loads** → Shows "Connecting to backend..."
2. **WebSocket connects** → Changes to "Connected to AI Backend"
3. **Camera starts** → Shows "Starting webcam..."
4. **Webcam opens** → Live video appears
5. **Detection runs** → Blue boxes appear around people
6. **Risk updates** → Score changes every 0.5 seconds
7. **Data logs** → Incidents saved to database

---

## 🆘 Still Not Working?

### Check These Files:

1. **Backend running?**
   ```
   Look for: INFO: Uvicorn running on http://0.0.0.0:8000
   ```

2. **Frontend running?**
   ```
   Look for: webpack compiled successfully
   ```

3. **Browser console errors?**
   ```
   Press F12 → Console → Look for red errors
   ```

4. **Backend console errors?**
   ```
   Look for: ❌ or Traceback messages
   ```

---

## 📞 Debug Checklist

- [ ] Backend shows "Server ready!"
- [ ] Frontend shows "webpack compiled"
- [ ] Browser at http://localhost:3000
- [ ] Console shows "WebSocket connected"
- [ ] Dashboard shows "Connected to AI Backend"
- [ ] No red errors in console
- [ ] Webcam works in other apps
- [ ] Port 8000 not blocked
- [ ] Python packages installed
- [ ] Node modules installed

---

## 💡 Pro Tips

### For Better Detection:
- Sit directly in front of camera
- Good lighting is crucial
- Avoid cluttered background
- Move slowly for better tracking

### For Better Performance:
- Close unnecessary apps
- Use Chrome browser
- Ensure good internet (for voice alerts)
- GPU makes it much faster

### For Demo:
- Test everything before presentation
- Have backup plan (screenshots)
- Explain what's happening
- Show console logs
- Point out real-time updates

---

## 🎉 Success Indicators

### You'll know it's working when:
1. ✅ Green "Connected" status
2. ✅ Live video in Camera 1
3. ✅ Blue boxes around people
4. ✅ Risk score updating
5. ✅ Worker count shows numbers
6. ✅ Console shows data streaming

---

**If you see all these, your AI system is LIVE!** 🚀

---

**CSIS - Safety in Sight** 🛡️
