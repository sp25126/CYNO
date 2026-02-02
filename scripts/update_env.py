"""
Auto-URL Updater for Cyno Cloud Brain
Automatically updates .env when Colab generates new Ngrok URL
"""
import os
import re
from pathlib import Path

def update_env_url(new_url: str):
    """Update COLAB_SERVER_URL in .env file"""
    env_path = Path(".env")
    
    if not env_path.exists():
        print("❌ .env file not found!")
        return False
    
    # Read current .env
    content = env_path.read_text()
    
    # Update or add COLAB_SERVER_URL
    if "COLAB_SERVER_URL" in content:
        updated = re.sub(
            r'COLAB_SERVER_URL=.*',
            f'COLAB_SERVER_URL={new_url}',
            content
        )
    else:
        updated = content + f"\\nCOLAB_SERVER_URL={new_url}\\n"
    
    # Write back
    env_path.write_text(updated)
    print(f"✅ Updated .env with URL: {new_url}")
    return True

def show_qr_code(url: str):
    """Display QR code for easy mobile copying"""
    try:
        import qrcode
        qr = qrcode.QRCode()
        qr.add_data(url)
        qr.print_ascii()
        print("\\n📱 Scan QR code to copy URL")
    except ImportError:
        print("💡 Install qrcode for QR display: pip install qrcode")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python scripts/update_env.py <ngrok_url>")
        print("Example: python scripts/update_env.py https://abc123.ngrok-free.app")
        sys.exit(1)
    
    url = sys.argv[1].strip()
    
    # Validate URL
    if not url.startswith("https://") or "ngrok" not in url:
        print("❌ Invalid Ngrok URL. Must be https://xxx.ngrok-free.app")
        sys.exit(1)
    
    # Update .env
    if update_env_url(url):
        show_qr_code(url)
        print("\\n✅ Cloud Brain URL updated!")
        print("   Test with: python tests/verify_production.py")
