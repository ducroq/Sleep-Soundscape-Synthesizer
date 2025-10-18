"""
SSML Compatibility Test
Tests different SSML formats to find what works
"""

import configparser
import requests
import yaml

# Load config
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Get API key
secrets = configparser.ConfigParser()
secrets.read('secrets.ini')
api_key = secrets.get('elevenlabs', 'api_key')

voice_id = config['voices'][0]
url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
headers = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": api_key
}

print("=" * 70)
print("SSML Compatibility Tests")
print("=" * 70)

tests = [
    {
        "name": "Plain text (control)",
        "text": "ruzu jaumeaio wonoze",
        "enable_ssml": False
    },
    {
        "name": "SSML with just speak tags",
        "text": "<speak>ruzu jaumeaio wonoze</speak>",
        "enable_ssml": True
    },
    {
        "name": "SSML with break tag",
        "text": '<speak>ruzu <break time="0.5s"/> jaumeaio wonoze</speak>',
        "enable_ssml": True
    },
    {
        "name": "SSML with emphasis",
        "text": '<speak>ruzu <emphasis level="strong">jaumeaio</emphasis> wonoze</speak>',
        "enable_ssml": True
    },
    {
        "name": "SSML with prosody (rate only)",
        "text": '<speak><prosody rate="90%">ruzu jaumeaio wonoze</prosody></speak>',
        "enable_ssml": True
    },
    {
        "name": "SSML with prosody (pitch only)",
        "text": '<speak><prosody pitch="+5%">ruzu jaumeaio wonoze</prosody></speak>',
        "enable_ssml": True
    },
    {
        "name": "SSML with prosody (volume only)",
        "text": '<speak><prosody volume="medium">ruzu jaumeaio wonoze</prosody></speak>',
        "enable_ssml": True
    },
    {
        "name": "SSML with prosody (rate + pitch)",
        "text": '<speak><prosody rate="90%" pitch="+5%">ruzu jaumeaio wonoze</prosody></speak>',
        "enable_ssml": True
    },
    {
        "name": "SSML with prosody (ALL: rate + pitch + volume)",
        "text": '<speak><prosody rate="87%" pitch="-7%" volume="medium">ruzu jaumeaio wonoze</prosody></speak>',
        "enable_ssml": True
    },
    {
        "name": "SSML with prosody + emphasis (like we generate)",
        "text": '<speak><prosody rate="87%" pitch="-7%" volume="medium">ruzu jaumeaio <emphasis level="strong">wonoze</emphasis></prosody></speak>',
        "enable_ssml": True
    }
]

results = []

for i, test in enumerate(tests):
    print(f"\n[Test {i+1}/{len(tests)}] {test['name']}")
    print(f"  Text: {test['text'][:60]}...")
    
    data = {
        "text": test['text'],
        "model_id": config['elevenlabs']['model_id'],
        "output_format": config['audio']['output_format'],
        "enable_ssml": test['enable_ssml']
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            audio_size = len(response.content)
            filename = f"test_{i+1:02d}.mp3"
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            print(f"  ✓ Status: {response.status_code}")
            print(f"  ✓ Audio size: {audio_size:,} bytes")
            print(f"  ✓ Saved to: {filename}")
            
            results.append({
                "test": test['name'],
                "status": "SUCCESS",
                "size": audio_size,
                "file": filename
            })
        else:
            print(f"  ✗ ERROR: Status {response.status_code}")
            print(f"  ✗ Response: {response.text[:200]}")
            results.append({
                "test": test['name'],
                "status": "FAILED",
                "error": response.text
            })
    
    except Exception as e:
        print(f"  ✗ EXCEPTION: {e}")
        results.append({
            "test": test['name'],
            "status": "EXCEPTION",
            "error": str(e)
        })

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print("\nPlay each file and note which ones have AUDIO:\n")

for i, result in enumerate(results):
    if result['status'] == 'SUCCESS':
        size_kb = result['size'] / 1024
        print(f"  {result['file']}: {result['test']}")
        print(f"    Size: {size_kb:.1f} KB - Play this and check!")
    else:
        print(f"  Test {i+1}: {result['test']} - {result['status']}")

print("\n" + "=" * 70)
print("INSTRUCTIONS:")
print("  1. Play EACH mp3 file above")
print("  2. Note which ones have actual SPEECH")
print("  3. Report back which test numbers work")
print("\nThis will tell us which SSML features are causing the problem!")
print("=" * 70)