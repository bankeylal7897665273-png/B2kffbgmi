import os
import io
import time
import requests
from flask import Flask, render_template, request, send_file, jsonify
from rembg import remove

app = Flask(__name__)
# Exact wahi database URL
FIREBASE_URL = "https://earning-a9b0c-default-rtdb.firebaseio.com/Bankey_BG_System"

@app.route('/')
def index(): 
    return render_template('index.html')

@app.route('/admin')
def admin_page(): 
    return render_template('admin.html')

# --- BG REMOVER API ENGINE (SUPPORTS BOTH URL & FILE UPLOAD) ---
@app.route('/api/remove-bg/<username>', methods=['GET', 'POST'])
def remove_bg_api(username):
    # 1. API Fetch Karo
    api_res = requests.get(f"{FIREBASE_URL}/apis/{username}.json")
    api_data = api_res.json() if api_res.ok else None
    
    if not api_data or 'uid' not in api_data: 
        return jsonify({"error": "Invalid API Username. API disabled or deleted."}), 404
    
    uid = api_data['uid']
    user_res = requests.get(f"{FIREBASE_URL}/users/{uid}.json").json()
    
    # 2. Limit Check (Free: 100, VIP: 1000)
    is_vip = user_res.get('is_vip', False)
    usage_limit = 1000 if is_vip else 100
    current_usage = api_data.get('usage', 0)
    
    if current_usage >= usage_limit:
        return jsonify({"error": f"API Limit Reached! You have used {current_usage}/{usage_limit} images. API is disabled. Please buy VIP or renew."}), 403

    # 3. Image Process Karo (FILE UPLOAD OR URL)
    try:
        input_image = None
        
        # METHOD A: Agar POST request hai aur file upload ki hai
        if request.method == 'POST' and 'image' in request.files:
            file = request.files['image']
            if file.filename == '':
                return jsonify({"error": "No selected file"}), 400
            input_image = file.read()
            
        # METHOD B: Agar GET request hai aur URL diya hai
        elif request.method == 'GET' and request.args.get('url'):
            img_url = request.args.get('url')
            response = requests.get(img_url)
            input_image = response.content
            
        else:
            return jsonify({"error": "Please upload an image file via POST (key: 'image') or provide an image URL via GET (?url=...)"}), 400

        # Background Remove (rembg AI Model)
        output_image = remove(input_image)
        
        # Usage Badhao
        new_usage = current_usage + 1
        requests.patch(f"{FIREBASE_URL}/apis/{username}.json", json={"usage": new_usage})
        
        # Dashboard Success Stat Badhao
        stats = user_res.get('stats', {"success": 0, "reject": 0})
        stats['success'] += 1
        requests.put(f"{FIREBASE_URL}/users/{uid}/stats.json", json=stats)
        
        return send_file(io.BytesIO(output_image), mimetype='image/png')
        
    except Exception as e:
        # Error aaye toh Reject Stat badhao
        stats = user_res.get('stats', {"success": 0, "reject": 0})
        stats['reject'] += 1
        requests.put(f"{FIREBASE_URL}/users/{uid}/stats.json", json=stats)
        return jsonify({"error": "Failed to process image.", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
