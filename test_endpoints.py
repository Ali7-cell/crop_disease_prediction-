"""
Agrilux API -- Comprehensive Endpoint Test Script
Tests all endpoints: health, register, login, predict-crop, predict-fertilizer,
predict-yield, history, profile
"""

import requests
import json
import sys
import time
import io

# Fix Windows encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE = "http://127.0.0.1:8000"

# Use unique email to avoid conflicts
EMAIL = f"testuser_{int(time.time())}@example.com"
PASSWORD = "testpass123"
NAME = "Test User"

results = []


def test(name, method, url, expected_status, headers=None, json_body=None, params=None):
    """Run a single API test and print result."""
    try:
        r = requests.request(method, url, headers=headers, json=json_body, params=params, timeout=30)
        status_ok = r.status_code == expected_status
        symbol = "✅" if status_ok else "❌"
        print(f"\n{symbol} {name}")
        print(f"   Method: {method} {url}")
        print(f"   Status: {r.status_code} (expected {expected_status})")
        try:
            body = r.json()
            print(f"   Response: {json.dumps(body, indent=2, default=str)[:500]}")
        except Exception:
            body = r.text
            print(f"   Response: {body[:300]}")
        results.append({"name": name, "pass": status_ok, "status": r.status_code})
        return body if status_ok else None
    except Exception as e:
        print(f"\n💥 {name} — EXCEPTION: {e}")
        results.append({"name": name, "pass": False, "status": str(e)})
        return None


print("=" * 70)
print("  AGRILUX API — ENDPOINT TEST SUITE")
print("=" * 70)

# ──────────── 1. HEALTH CHECK ────────────
test("Health Check", "GET", f"{BASE}/health", 200)

# ──────────── 2. REGISTER ────────────
reg = test("Register User", "POST", f"{BASE}/register", 201, json_body={
    "name": NAME,
    "email": EMAIL,
    "password": PASSWORD,
})
TOKEN = reg.get("access_token") if reg else None

# ──────────── 3. REGISTER (Duplicate — should fail 409) ────────────
test("Register Duplicate User", "POST", f"{BASE}/register", 409, json_body={
    "name": NAME,
    "email": EMAIL,
    "password": PASSWORD,
})

# ──────────── 4. LOGIN ────────────
login = test("Login", "POST", f"{BASE}/login", 200, json_body={
    "email": EMAIL,
    "password": PASSWORD,
})
if login:
    TOKEN = login.get("access_token", TOKEN)

# ──────────── 5. LOGIN (Wrong password — should fail 401) ────────────
test("Login Wrong Password", "POST", f"{BASE}/login", 401, json_body={
    "email": EMAIL,
    "password": "wrongpassword",
})

# ──────────── Auth header for protected endpoints ────────────
AUTH = {"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}

# ──────────── 6. PREDICT CROP ────────────
test("Predict Crop", "POST", f"{BASE}/predict-crop", 200, headers=AUTH, json_body={
    "N": 90,
    "P": 42,
    "K": 43,
    "temperature": 20.87,
    "humidity": 82.0,
    "ph": 6.5,
    "rainfall": 202.93,
})

# ──────────── 7. PREDICT CROP (No auth — should fail 403) ────────────
test("Predict Crop (No Auth)", "POST", f"{BASE}/predict-crop", 403, json_body={
    "N": 90, "P": 42, "K": 43,
    "temperature": 20.87, "humidity": 82.0, "ph": 6.5, "rainfall": 202.93,
})

# ──────────── 8. PREDICT FERTILIZER ────────────
test("Predict Fertilizer", "POST", f"{BASE}/predict-fertilizer", 200, headers=AUTH, json_body={
    "temperature": 26.0,
    "humidity": 52.0,
    "moisture": 38.0,
    "soil_type": "Sandy",
    "crop_type": "Maize",
    "nitrogen": 37.0,
    "potassium": 0.0,
    "phosphorous": 0.0,
})

# ──────────── 9. PREDICT YIELD ────────────
test("Predict Yield", "POST", f"{BASE}/predict-yield", 200, headers=AUTH, json_body={
    "area": "India",
    "item": "Wheat",
    "year": 2024,
    "rainfall": 1200.0,
    "pesticides": 30000.0,
    "temperature": 25.5,
})

# ──────────── 10. HISTORY (all) ────────────
test("Get History (All)", "GET", f"{BASE}/history", 200, headers=AUTH)

# ──────────── 11. HISTORY (filtered by type) ────────────
test("Get History (Crop Filter)", "GET", f"{BASE}/history", 200, headers=AUTH, params={"type": "crop"})
test("Get History (Fertilizer Filter)", "GET", f"{BASE}/history", 200, headers=AUTH, params={"type": "fertilizer"})
test("Get History (Yield Filter)", "GET", f"{BASE}/history", 200, headers=AUTH, params={"type": "yield"})

# ──────────── 12. HISTORY (invalid filter) ────────────
test("Get History (Invalid Filter)", "GET", f"{BASE}/history", 422, headers=AUTH, params={"type": "invalid"})

# ──────────── 13. HISTORY DETAIL ────────────
# First get a valid prediction ID from history
hist = test("Get History for Detail", "GET", f"{BASE}/history", 200, headers=AUTH)
if hist and hist.get("items"):
    pred_id = hist["items"][0]["id"]
    test(f"Get History Detail (id={pred_id})", "GET", f"{BASE}/history/{pred_id}", 200, headers=AUTH)
else:
    print("\n⚠️  Skipping history detail test — no predictions found")

# ──────────── 14. HISTORY DETAIL (not found) ────────────
test("Get History Detail (Not Found)", "GET", f"{BASE}/history/999999", 404, headers=AUTH)

# ──────────── 15. PROFILE (GET) ────────────
test("Get Profile", "GET", f"{BASE}/profile", 200, headers=AUTH)

# ──────────── 16. PROFILE (UPDATE name) ────────────
test("Update Profile (Name)", "PUT", f"{BASE}/profile", 200, headers=AUTH, json_body={
    "name": "Updated Test User",
})

# ──────────── 17. PROFILE (UPDATE empty — should fail 422) ────────────
test("Update Profile (Empty Body)", "PUT", f"{BASE}/profile", 422, headers=AUTH, json_body={})

# ──────────── 18. PREDICT CROP (Invalid input — should fail 422) ────────────
test("Predict Crop (Invalid Input)", "POST", f"{BASE}/predict-crop", 422, headers=AUTH, json_body={
    "N": 999,  # out of range (max 140)
    "P": 42, "K": 43,
    "temperature": 20.87, "humidity": 82.0, "ph": 6.5, "rainfall": 202.93,
})

# ──────────── 19. PREDICT FERTILIZER (Invalid soil type — should fail 422) ────────────
test("Predict Fertilizer (Invalid Soil)", "POST", f"{BASE}/predict-fertilizer", 422, headers=AUTH, json_body={
    "temperature": 26.0, "humidity": 52.0, "moisture": 38.0,
    "soil_type": "InvalidSoil", "crop_type": "Maize",
    "nitrogen": 37.0, "potassium": 0.0, "phosphorous": 0.0,
})

# ──────────── SUMMARY ────────────
print("\n" + "=" * 70)
print("  TEST RESULTS SUMMARY")
print("=" * 70)

passed = sum(1 for r in results if r["pass"])
failed = sum(1 for r in results if not r["pass"])
total = len(results)

for r in results:
    symbol = "✅" if r["pass"] else "❌"
    print(f"  {symbol} {r['name']}  (HTTP {r['status']})")

print(f"\n  Total: {total} | Passed: {passed} | Failed: {failed}")
if failed == 0:
    print("  🎉 ALL TESTS PASSED!")
else:
    print(f"  ⚠️  {failed} test(s) FAILED!")

print("=" * 70)
