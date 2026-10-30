import json
import os

def load_accounts(filepath="accounts.json"):
    """
    JSON ফাইল থেকে ফ্রি ফায়ার একাউন্ট এবং সার্ভার ক্রডেনশিয়াল লোড করে।
    """
    if not os.path.exists(filepath):
        print(f"⚠️ সতর্কতা: {filepath} ফাইলটি পাওয়া যায়নি! দয়া করে একটি accounts.json ফাইল তৈরি করুন।")
        return {}
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            accounts = json.load(f)
            return accounts
    except Exception as e:
        print(f"❌ একাউন্ট লোড করতে সমস্যা হয়েছে: {e}")
        return {}
