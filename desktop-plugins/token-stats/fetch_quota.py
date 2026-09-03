import os, sys, json, base64, ctypes, ctypes.wintypes, requests

class DATA_BLOB(ctypes.Structure):
    _fields_ = [('cbData', ctypes.wintypes.DWORD),
                ('pbData', ctypes.POINTER(ctypes.c_byte))]

CryptUnprotectData = ctypes.windll.crypt32.CryptUnprotectData
LocalFree = ctypes.windll.kernel32.LocalFree

def decrypt_dpapi(encrypted_b64):
    raw = base64.b64decode(encrypted_b64)
    blob_in = DATA_BLOB(len(raw), ctypes.cast(ctypes.create_string_buffer(raw), ctypes.POINTER(ctypes.c_byte)))
    blob_out = DATA_BLOB()
    if CryptUnprotectData(ctypes.byref(blob_in), None, None, None, None, 0, ctypes.byref(blob_out)):
        data = ctypes.string_at(blob_out.pbData, blob_out.cbData)
        LocalFree(blob_out.pbData)
        return data.decode('utf-8')
    else:
        raise Exception("DPAPI Decrypt Failed")

def get_quota_direct():
    auth_dir = os.path.expandvars(r"%LOCALAPPDATA%\ZCodeAntigravity\auth")
    if not os.path.exists(auth_dir):
        return {"error": "Auth dir not found"}
    
    auth_files = [f for f in os.listdir(auth_dir) if f.startswith("antigravity-") and f.endswith(".json")]
    if not auth_files:
        return {"error": "No antigravity auth file found"}
    
    target_auth = os.path.join(auth_dir, auth_files[0])
    with open(target_auth, "r", encoding="utf-8") as f:
        auth_data = json.load(f)
    
    enc_token = auth_data.get("access_token", "").replace("dpapi:v1:", "")
    token = decrypt_dpapi(enc_token)
    project_id = auth_data.get("project_id", "")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "antigravity/hub/2.8.1 windows/amd64"
    }
    
    proxies = {"http": "http://127.0.0.1:3067", "https": "http://127.0.0.1:3067"}
    endpoints = [
        "https://cloudcode-pa.googleapis.com/v1internal:retrieveUserQuotaSummary",
        "https://daily-cloudcode-pa.googleapis.com/v1internal:retrieveUserQuotaSummary"
    ]
    
    payload = {"project": project_id}
    
    for ep in endpoints:
        try:
            r = requests.post(ep, headers=headers, json=payload, proxies=proxies, timeout=6)
            if r.status_code == 200:
                res = r.json()
                groups = res.get("groups", [])
                quota5h = None
                quotaWeekly = None
                for g in groups:
                    for b in g.get("buckets", []):
                        bid = b.get("bucketId", "")
                        frac = b.get("remainingFraction", 1.0)
                        pct = round(frac * 100, 1)
                        if "5h" in bid and quota5h is None:
                            quota5h = pct
                        elif "week" in bid and quotaWeekly is None:
                            quotaWeekly = pct
                
                output = {
                    "account": auth_data.get("email", ""),
                    "plan": "Google AI Pro",
                    "quota5h": quota5h,
                    "quotaWeekly": quotaWeekly,
                    "fetchedAt": r.headers.get("Date", "")
                }
                return output
        except Exception as e:
            continue
            
    return {"error": "All endpoints failed"}

if __name__ == "__main__":
    result = get_quota_direct()
    # Save to local cache file for plugin to read directly without blocking
    cache_path = os.path.expandvars(r"%LOCALAPPDATA%\hermes\desktop-plugins\token-stats\direct-quota.json")
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(json.dumps(result, ensure_ascii=False))
