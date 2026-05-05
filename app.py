import os
import io
import time
import requests
from flask import Flask, render_template, request, send_file, jsonify
from rembg import remove
from PIL import Image

app = Flask(__name__)
FIREBASE_URL = "https://earning-a9b0c-default-rtdb.firebaseio.com/BG_Remover_System"

@app.route('/')
def index(): return render_template('index.html')

@app.route('/admin-panel')
def admin_page(): return render_template('admin.html')

# --- THE REAL API ---
@app.route('/api/remove-bg/<username>')
def remove_bg_api(username):
    # 1. Check API Data
    api_res = requests.get(f"{FIREBASE_URL}/apis/{username}.json").json()
    if not api_res: return jsonify({"error": "Invalid API Username"}), 404
    
    uid = api_res['uid']
    user_data = requests.get(f"{FIREBASE_URL}/users/{uid}.json").json()
    
    # 2. Check Expiry (Free: 2 days, VIP: 30 days)
    days_limit = 30 if user_data.get('is_vip') else 2
    if (time.time() - api_res['created_at']) > (days_limit * 86400):
        return jsonify({"error": f"API Expired! This {api_res['type']} API was valid for {days_limit} days."}), 403

    # 3. Check Usage Limit (Free: 100, VIP: 1000)
    usage_limit = 1000 if api_res['type'] == 'VIP' else 100
    current_usage = api_res.get('usage', 0)
    
    if current_usage >= usage_limit:
        return jsonify({"error": f"Limit Reached! {api_res['type']} API limit is {usage_limit} images."}), 403

    # 4. Processing
    img_url = request.args.get('url')
    if not img_url: return jsonify({"error": "No image URL provided"}), 400

    try:
        response = requests.get(img_url)
        input_image = response.content
        output_image = remove(input_image)
        
        # Update Usage in Firebase
        requests.patch(f"{FIREBASE_URL}/apis/{username}.json", json={"usage": current_usage + 1})
        # Log success for dashboard
        requests.post(f"{FIREBASE_URL}/users/{uid}/history.json", json={"url": img_url, "time": time.time(), "status": "success"})
        
        return send_file(io.BytesIO(output_image), mimetype='image/png')
    except Exception as e:
        requests.post(f"{FIREBASE_URL}/users/{uid}/history.json", json={"url": img_url, "time": time.time(), "status": "failed"})
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
