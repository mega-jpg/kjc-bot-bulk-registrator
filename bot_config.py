# Bot Configuration
# Cấu hình cho automation bot

#Login time
LOGIN_TIME = 1 
# === TYPING CONFIGURATION ===
# Số lần lặp lại typing (ngoài lần đầu tiên)
TYPING_ROUNDS = 10  # Tổng = 1 lần đầu + 3 lần lặp = 4 lần typing (~135 words/60s)

# Delay giữa các ký tự khi typing (milliseconds)
TYPING_DELAY_MS = 65  # ~65ms để đạt 135 từ trong 60 giây

# === TIMING CONFIGURATION ===
# Thời gian chờ Chrome khởi động (seconds)
CHROME_STARTUP_WAIT = 4

# Thời gian chờ sau khi page ready (seconds)
PAGE_READY_WAIT = 2

# Thời gian chờ trước khi bring to front (seconds)
BRING_TO_FRONT_WAIT = 1

# Thời gian chờ sau khi click vào input (seconds)
INPUT_FOCUS_WAIT = 0.2

# Thời gian chờ sau mỗi round typing (seconds)
ROUND_COMPLETE_WAIT = 0.5

# === CHROME CDP CONFIGURATION ===
# Chrome remote debugging port
CHROME_DEBUG_PORT = 9222

# Chrome user data directory
CHROME_USER_DATA_DIR = r"C:\temp\chrome_bot_profile"

# === TARGET CONFIGURATION ===
# Target URL
TARGET_URL = "https://kjctest.com/"

# === WORD COUNT LIMIT ===
# Giới hạn số từ tối đa để extract (dừng khi đạt giới hạn này)
LIMIT_COUNT_WORD = 135
