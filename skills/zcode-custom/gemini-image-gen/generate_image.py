#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini / Nano Banana 2 Image Generation Script for ZCode Antigravity Bridge
Generates images directly via local Antigravity Bridge or Google AI Studio.
"""

import os
import sys
import json
import base64
import argparse
from datetime import datetime
import requests

CONFIG_FILE = os.path.expanduser("~/.zcode/config/gemini.json")
LOCAL_BRIDGE_URL = "http://127.0.0.1:18080"
LOCAL_BRIDGE_KEY = "wY5Xr4HVPT3BZivioFX2L_3XhXdFfU8QBjT_Ff4xGJ0"

def get_bridge_config():
    # Check if local ZCode Antigravity config exists
    antigravity_config = os.path.expanduser("~/AppData/Local/ZCodeAntigravity/config.yaml")
    base_url = LOCAL_BRIDGE_URL
    api_key = LOCAL_BRIDGE_KEY

    if os.path.exists(antigravity_config):
        try:
            with open(antigravity_config, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("port:"):
                        port = line.split(":", 1)[1].strip().strip('"')
                        base_url = f"http://127.0.0.1:{port}"
                    elif line.startswith("- \"") and len(line) > 10:
                        # api-keys entry
                        api_key = line.strip("- ").strip('"')
        except Exception:
            pass

    return base_url, api_key

def generate_via_antigravity(prompt, base_url, api_key, model="gemini-3.1-flash-image", timeout=60):
    url = f"{base_url}/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    response = requests.post(url, json=payload, headers=headers, timeout=timeout)
    if response.status_code != 200:
        raise Exception(f"Antigravity Bridge Error ({response.status_code}): {response.text}")
        
    data = response.json()
    choices = data.get("choices", [])
    if not choices:
        raise Exception("No choices returned by Antigravity Bridge")
        
    msg = choices[0].get("message", {})
    images = []
    
    # Check images array
    if "images" in msg and msg["images"]:
        for img_obj in msg["images"]:
            url_val = img_obj.get("image_url", {}).get("url", "")
            if url_val.startswith("data:image"):
                header, b64_data = url_val.split(",", 1)
                mime = "image/jpeg" if "jpeg" in header or "jpg" in header else "image/png"
                images.append((base64.b64decode(b64_data), mime))
            elif url_val.startswith("http"):
                # Remote URL download
                r = requests.get(url_val, timeout=30)
                images.append((r.content, "image/jpeg"))
                
    # Fallback: check content for data URL
    content = msg.get("content") or ""
    if not images and "data:image" in content:
        import re
        matches = re.findall(r'data:image\/[a-zA-Z]+;base64,[A-Za-z0-9+/=]+', content)
        for m in matches:
            header, b64_data = m.split(",", 1)
            mime = "image/jpeg" if "jpeg" in header or "jpg" in header else "image/png"
            images.append((base64.b64decode(b64_data), mime))
            
    if not images:
        raise Exception(f"No image was generated. Model reply: {content}")
        
    return images

def main():
    parser = argparse.ArgumentParser(description="Generate images via Gemini / Antigravity Bridge")
    parser.add_argument("--prompt", "-p", required=True, help="Image generation prompt")
    parser.add_argument("--model", "-m", default="gemini-3.1-flash-image", help="Model name")
    parser.add_argument("--output-dir", "-o", default="generated_images", help="Output directory")
    parser.add_argument("--output-name", "-n", default=None, help="Output file name")
    parser.add_argument("--base-url", default=None, help="Antigravity bridge base URL")
    parser.add_argument("--api-key", "-k", default=None, help="Antigravity bridge API key")
    
    args = parser.parse_args()
    
    base_url, api_key = get_bridge_config()
    if args.base_url:
        base_url = args.base_url
    if args.api_key:
        api_key = args.api_key
        
    os.makedirs(args.output_dir, exist_ok=True)
    
    print(f"[*] Calling {args.model} via Antigravity Bridge ({base_url}) ...")
    
    try:
        images = generate_via_antigravity(args.prompt, base_url, api_key, model=args.model)
        
        saved_paths = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        for i, (img_bytes, mime) in enumerate(images):
            ext = "png" if "png" in mime else "jpg"
            if args.output_name:
                filename = f"{args.output_name}.{ext}" if not args.output_name.endswith(f".{ext}") else args.output_name
            else:
                filename = f"gemini_image_{timestamp}_{i+1}.{ext}"
                
            filepath = os.path.abspath(os.path.join(args.output_dir, filename))
            with open(filepath, "wb") as f:
                f.write(img_bytes)
            saved_paths.append(filepath)
            
        result = {
            "status": "success",
            "model": args.model,
            "prompt": args.prompt,
            "images": saved_paths
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        error_result = {
            "status": "error",
            "error_type": "GENERATION_FAILED",
            "message": str(e)
        }
        print(json.dumps(error_result, ensure_ascii=False, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()
