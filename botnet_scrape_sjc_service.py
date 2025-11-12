
import os
import re
import time
import threading
import asyncio
from typing import Dict

# Set Windows event loop policy for subprocess support
if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# --- Telegram Notify ---
def send_telegram_notify(message: str):
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    if not token or not chat_id:
        print('[Telegram Notify] Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID')
        return
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    payload = {'chat_id': chat_id, 'text': message, 'parse_mode': 'HTML'}
    try:
        import requests
        resp = requests.post(url, data=payload, timeout=10)
        if resp.status_code == 200:
            print('[Telegram Notify] Sent successfully')
        else:
            print(f'[Telegram Notify] Failed: {resp.text}')
    except Exception as e:
        print(f'[Telegram Notify] Error: {e}')


class SJCScrapeService:
    """
    Service for scraping SJC gold prices and managing cronjob thread
    """

    def __init__(self):
        # Biến lưu giá SJC trước đó để so sánh
        self._last_special_mua = None
        self._last_special_ban = None
        # Lưu playwright và browser instances
        self._playwright = None
        self._browser = None
        self._page = None
    
    def convert_to_telex(self, text: str) -> str:
        """Convert Vietnamese text with diacritics to Telex input - OPTIMIZED"""
        # Bảng chuyển đổi Telex tối ưu - dấu thanh đặt SAU CÙNG trong âm tiết
        telex_map = {
            # Nguyên âm đơn có dấu thanh
            'à': 'af', 'á': 'as', 'ả': 'ar', 'ã': 'ax', 'ạ': 'aj',
            'è': 'ef', 'é': 'es', 'ẻ': 'er', 'ẽ': 'ex', 'ẹ': 'ej',
            'ì': 'if', 'í': 'is', 'ỉ': 'ir', 'ĩ': 'ix', 'ị': 'ij',
            'ò': 'of', 'ó': 'os', 'ỏ': 'or', 'õ': 'ox', 'ọ': 'oj',
            'ù': 'uf', 'ú': 'us', 'ủ': 'ur', 'ũ': 'ux', 'ụ': 'uj',
            'ỳ': 'yf', 'ý': 'ys', 'ỷ': 'yr', 'ỹ': 'yx', 'ỵ': 'yj',
            
            # Nguyên âm có dấu mũ/móc (không dấu thanh)
            'ă': 'aw', 'â': 'aa', 'ê': 'ee', 'ô': 'oo', 'ơ': 'ow', 'ư': 'uw',
            
            # Nguyên âm có dấu mũ/móc + dấu thanh
            # Thứ tự: nguyên âm + dấu mũ/móc + dấu thanh (để dấu thanh cuối cùng)
            'ằ': 'awf', 'ắ': 'aws', 'ẳ': 'awr', 'ẵ': 'awx', 'ặ': 'awj',
            'ầ': 'aaf', 'ấ': 'aas', 'ẩ': 'aar', 'ẫ': 'aax', 'ậ': 'aaj',
            'ề': 'eef', 'ế': 'ees', 'ể': 'eer', 'ễ': 'eex', 'ệ': 'eej',
            'ồ': 'oof', 'ố': 'oos', 'ổ': 'oor', 'ỗ': 'oox', 'ộ': 'ooj',
            'ờ': 'owf', 'ớ': 'ows', 'ở': 'owr', 'ỡ': 'owx', 'ợ': 'owj',
            'ừ': 'uwf', 'ứ': 'uws', 'ử': 'uwr', 'ữ': 'uwx', 'ự': 'uwj',
            
            # Chữ đ
            'đ': 'dd',
            
            # Chữ hoa
            'À': 'Af', 'Á': 'As', 'Ả': 'Ar', 'Ã': 'Ax', 'Ạ': 'Aj',
            'È': 'Ef', 'É': 'Es', 'Ẻ': 'Er', 'Ẽ': 'Ex', 'Ẹ': 'Ej',
            'Ì': 'If', 'Í': 'Is', 'Ỉ': 'Ir', 'Ĩ': 'Ix', 'Ị': 'Ij',
            'Ò': 'Of', 'Ó': 'Os', 'Ỏ': 'Or', 'Õ': 'Ox', 'Ọ': 'Oj',
            'Ù': 'Uf', 'Ú': 'Us', 'Ủ': 'Ur', 'Ũ': 'Ux', 'Ụ': 'Uj',
            'Ỳ': 'Yf', 'Ý': 'Ys', 'Ỷ': 'Yr', 'Ỹ': 'Yx', 'Ỵ': 'Yj',
            
            'Ă': 'Aw', 'Â': 'Aa', 'Ê': 'Ee', 'Ô': 'Oo', 'Ơ': 'Ow', 'Ư': 'Uw',
            
            'Ằ': 'Awf', 'Ắ': 'Aws', 'Ẳ': 'Awr', 'Ẵ': 'Awx', 'Ặ': 'Awj',
            'Ầ': 'Aaf', 'Ấ': 'Aas', 'Ẩ': 'Aar', 'Ẫ': 'Aax', 'Ậ': 'Aaj',
            'Ề': 'Eef', 'Ế': 'Ees', 'Ể': 'Eer', 'Ễ': 'Eex', 'Ệ': 'Eej',
            'Ồ': 'Oof', 'Ố': 'Oos', 'Ổ': 'Oor', 'Ỗ': 'Oox', 'Ộ': 'Ooj',
            'Ờ': 'Owf', 'Ớ': 'Ows', 'Ở': 'Owr', 'Ỡ': 'Owx', 'Ợ': 'Owj',
            'Ừ': 'Uwf', 'Ứ': 'Uws', 'Ử': 'Uwr', 'Ữ': 'Uwx', 'Ự': 'Uwj',
            
            'Đ': 'Dd',
        }
        
        result = []
        for char in text:
            if char in telex_map:
                result.append(telex_map[char])
            else:
                result.append(char)
        
        return ''.join(result)

    async def scrape_sjc(self) -> Dict:
        """Open browser with Playwright and interact with content"""
        try:
            print(f"[Browser] Opening browser with Playwright... (thread: {threading.current_thread().name})")
            
            # Run sync playwright in a separate thread to avoid asyncio loop conflict
            import concurrent.futures
            
            # Define the playwright function FIRST before using it
            def run_playwright():
                from playwright.sync_api import sync_playwright
                import os
                import subprocess
                import time
                from bot_config import (
                    TYPING_ROUNDS, TYPING_DELAY_MS,
                    CHROME_STARTUP_WAIT, PAGE_READY_WAIT, BRING_TO_FRONT_WAIT,
                    INPUT_FOCUS_WAIT, ROUND_COMPLETE_WAIT,
                    CHROME_DEBUG_PORT, CHROME_USER_DATA_DIR, TARGET_URL, LOGIN_TIME, LIMIT_COUNT_WORD
                )
                import time
                
                print(f"✅ [CDP] Connecting to REAL Chrome via Chrome DevTools Protocol...")
                
                # Find Chrome on Windows
                chrome_paths = [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
                ]
                
                chrome_path = None
                for path in chrome_paths:
                    if os.path.exists(path):
                        chrome_path = path
                        print(f"✅ [CDP] Found Chrome: {chrome_path}")
                        break
                
                if not chrome_path:
                    raise Exception("❌ Chrome not found! Install Google Chrome first.")
                
                # Start Chrome with remote debugging
                print(f"🔧 [CDP] Starting Chrome with debugging port {CHROME_DEBUG_PORT}...")
                chrome_cmd = [
                    chrome_path,
                    f'--remote-debugging-port={CHROME_DEBUG_PORT}',
                    '--start-maximized',
                    f'--user-data-dir={CHROME_USER_DATA_DIR}',
                    TARGET_URL
                ]
                
                subprocess.Popen(chrome_cmd)
                print(f"⏳ [CDP] Waiting {CHROME_STARTUP_WAIT} seconds for Chrome...")
                time.sleep(CHROME_STARTUP_WAIT)
                
                # Connect via CDP
                print("🔌 [CDP] Connecting Playwright...")
                self._playwright = sync_playwright().start()
                self._browser = self._playwright.chromium.connect_over_cdp(f'http://localhost:{CHROME_DEBUG_PORT}')
                print("✅ [CDP] Connected!")
                
                # Get existing page
                contexts = self._browser.contexts
                if contexts and len(contexts) > 0:
                    pages = contexts[0].pages
                    if pages and len(pages) > 0:
                        self._page = pages[0]
                        print(f"✅ [CDP] Using tab: {self._page.url}")
                    else:
                        self._page = contexts[0].new_page()
                        print("✅ [CDP] Created new tab")
                else:
                    raise Exception("❌ No context in Chrome")
                
                # Navigate if needed
                if 'kjctest.com' not in self._page.url:
                    print(f"📡 [CDP] Navigating to {TARGET_URL}...")
                    self._page.goto(TARGET_URL, timeout=60000)
                else:
                    print(f"✅ [CDP] Already on kjctest.com")
                
                time.sleep(PAGE_READY_WAIT)
                print("✅ [CDP] Chrome ready with real profile!")
                
                # Verify window is maximized
                window_info = self._page.evaluate("""() => {
                    return {
                        width: window.outerWidth,
                        height: window.outerHeight,
                        screenX: window.screenX,
                        screenY: window.screenY,
                        screenWidth: screen.width,
                        screenHeight: screen.height
                    }
                }""")
                print(f"🖥️ Window: {window_info['width']}x{window_info['height']}")
                print(f"📊 Screen: {window_info['screenWidth']}x{window_info['screenHeight']}")
                
                if window_info['width'] >= window_info['screenWidth'] - 50:
                    print("✅ Window is MAXIMIZED!")
                else:
                    print("⚠️ Window is NOT maximized")
                
                # BRING WINDOW TO FRONT
                print("🎯 Bringing browser window to front...")
                time.sleep(BRING_TO_FRONT_WAIT)
                try:
                    import win32gui
                    import win32con
                    
                    # Find Chrome/Chromium window
                    print("� Searching for browser window...")
                    found_windows = []
                    
                    def enum_callback(hwnd, results):
                        if win32gui.IsWindowVisible(hwnd):
                            title = win32gui.GetWindowText(hwnd)
                            if title and ('Chromium' in title or 'Chrome' in title or 'KJC' in title or 'Typing Test' in title):
                                results.append((hwnd, title))
                        return True
                    
                    win32gui.EnumWindows(enum_callback, found_windows)
                    
                    if found_windows:
                        hwnd, window_title = found_windows[0]
                        print(f"✅ Found browser window: '{window_title}'")
                        
                        # Bring to front - chỉ dùng TOPMOST và SetForeground
                        print("🚀 Setting window TOPMOST...")
                        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0,
                                            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)
                        time.sleep(0.2)
                        
                        print("🚀 Setting foreground...")
                        win32gui.SetForegroundWindow(hwnd)
                        time.sleep(0.2)
                        
                        print("🚀 Removing TOPMOST flag...")
                        win32gui.SetWindowPos(hwnd, win32con.HWND_NOTOPMOST, 0, 0, 0, 0,
                                            win32con.SWP_NOMOVE | win32con.SWP_NOSIZE | win32con.SWP_SHOWWINDOW)
                        
                        print("✅ Browser window brought to front!")
                    else:
                        print("⚠️ No browser window found!")
                            
                except Exception as e:
                    print(f"⚠️ Error bringing window to front: {e}")
                
                # Get page content
                content = self._page.content()
                title = self._page.title()
                print(f"📄 Page title: {title}")
                
                # --- Trích xuất text từ typing-line element ---
                print("🔍 Extracting text from typing-line element...")
                
                # Đợi trang load (chỉ cần domcontentloaded, không cần networkidle)
                print("⏳ Waiting for page DOM to load...")
                self._page.wait_for_load_state('domcontentloaded')
                
                # Đợi thêm một chút để typing-line render
                print("⏳ Waiting for typing-line to render...")
                print("⏳ Waiting 45 seconds for login...")
                time.sleep(LOGIN_TIME)
                
                # Main task: In ra toàn bộ HTML để kiểm tra
                print("📋 Checking page HTML...")
                page_html = self._page.content()
                if 'typing-line' in page_html:
                    print("✅ Found 'typing-line' in HTML")
                else:
                    print("❌ 'typing-line' NOT found in HTML")
                
                # Khởi tạo bộ đếm tổng số từ đã extract
                total_word_count = 0
                print(f"📊 Bắt đầu đếm từ - Giới hạn: {LIMIT_COUNT_WORD} từ")
                
                # Lấy tất cả các element div.w-full.typing-line
                print("🔎 Finding all div.w-full.typing-line elements...")
                typing_elements = self._page.query_selector_all('div.w-full.typing-line')
                print(f"📊 Found {len(typing_elements)} typing-line elements")
                
                if len(typing_elements) >= 2:
                    # Lấy 2 element đầu tiên
                    first_element = typing_elements[0]
                    second_element = typing_elements[1]
                    
                    # Trích xuất text từ mỗi element
                    first_text = first_element.inner_text().strip()
                    second_text = second_element.inner_text().strip()
                    
                    print(f"📝 First element text: '{first_text}'")
                    print(f"📝 Second element text: '{second_text}'")
                    
                    # Nối 2 đoạn văn bằng khoảng trắng và thêm khoảng trắng vào cuối
                    extracted_text = f"{first_text} {second_text} "
                    
                    # Đếm số từ trong text vừa extract (tách bằng khoảng trắng)
                    word_count = len(extracted_text.split())
                    
                    print(f"📝 Combined text: '{extracted_text}'")
                    print(f"📏 Total length: {len(extracted_text)}")
                    print(f"🔢 Số từ trong đoạn này: {word_count} từ")
                    
                    # KIỂM TRA TRƯỚC KHI CỘNG: Nếu tổng sẽ vượt giới hạn, cắt bớt text
                    if total_word_count + word_count > LIMIT_COUNT_WORD:
                        print(f"⚠️ Sẽ vượt giới hạn! ({total_word_count} + {word_count} > {LIMIT_COUNT_WORD})")
                        
                        # Tính số từ cần lấy
                        words_needed = LIMIT_COUNT_WORD - total_word_count
                        print(f"📊 Số từ cần lấy: {words_needed} từ")
                        
                        # Tách text thành mảng từ
                        words_array = extracted_text.split()
                        
                        # Lấy số từ cần thiết từ đầu
                        trimmed_words = words_array[:words_needed]
                        
                        # Thêm từ "error" vào cuối
                        trimmed_words.append("error")
                        
                        # Nối lại thành text và thêm khoảng trắng cuối
                        extracted_text = " ".join(trimmed_words) + " "
                        
                        print(f"✂️ Đã cắt text: '{extracted_text}'")
                        print(f"📊 Số từ sau khi cắt + error: {len(extracted_text.split())} từ")
                        
                        # Cập nhật tổng số từ
                        total_word_count = LIMIT_COUNT_WORD  # Đặt đúng = giới hạn
                    else:
                        # Không vượt giới hạn, cộng bình thường
                        total_word_count += word_count
                    
                    print(f"📊 Tổng số từ hiện tại: {total_word_count}/{LIMIT_COUNT_WORD} từ")

                    # Tìm và focus vào input typing-input
                    print("🔍 Finding typing-input element...")
                    typing_input = self._page.query_selector('input#typing-input')
                    
                    if typing_input:
                        print("✅ Found typing-input element")
                        
                        # Scroll element vào view để đảm bảo nhìn thấy
                        print("📜 Scrolling input into view...")
                        typing_input.scroll_into_view_if_needed()
                        time.sleep(0.3)
                        
                        # Click vào input để focus - SỬ DỤNG PLAYWRIGHT API (không dùng chuột vật lý)
                        print("🖱️ Clicking on input using Playwright API...")
                        typing_input.click()
                        print("✅ Input focused via Playwright")
                        time.sleep(INPUT_FOCUS_WAIT)
                        
                        # KHÔNG DÙNG TELEX - GÕ TRỰC TIẾP UNICODE
                        # Browser không nhận bộ gõ Telex của Windows
                        # Phải gõ trực tiếp text Unicode (có dấu) vào input
                        print("⌨️ Typing UNICODE text directly (not Telex)...")
                        print(f"📝 Original text: '{extracted_text}'")
                        print(f"📏 Total characters to type: {len(extracted_text)}")
                        
                        # TYPE TRỰC TIẾP TEXT GỐC (UNICODE) - không convert Telex
                        print("⌨️ Typing with Playwright (you can use your mouse/keyboard freely)...")
                        
                        for i, char in enumerate(extracted_text):
                            # TYPE TRỰC TIẾP ký tự Unicode vào input
                            typing_input.type(char, delay=TYPING_DELAY_MS)
                            
                            # Log progress mỗi 20 ký tự
                            if (i + 1) % 20 == 0:
                                print(f"⌨️ Typed {i + 1}/{len(extracted_text)} characters")
                        
                        print("✅ Finished typing first round with Playwright API!")
                        print("💡 You were free to use VS Code while typing happened!")
                        time.sleep(1)
                        
                        # Kiểm tra nếu đã đạt giới hạn sau round đầu tiên
                        if total_word_count >= LIMIT_COUNT_WORD:
                            print(f"✅ ĐÃ ĐẠT GIỚI HẠN {LIMIT_COUNT_WORD} TỪ sau round đầu!")
                            print(f"🎯 Tổng cộng: {total_word_count} từ - HOÀN THÀNH!")
                            # Thoát luôn, không cần loop tiếp
                            print("⚠️ Browser will remain open for manual interaction")
                            return {
                                'success': True,
                                'url': TARGET_URL,
                                'title': title,
                                'total_words': total_word_count,
                                'limit_reached': True,
                                'timestamp': time.time()
                            }
                        
                        # Lặp lại theo cấu hình
                        for round_num in range(1, TYPING_ROUNDS + 1):
                            print(f"\n🔄 Starting round {round_num}/{TYPING_ROUNDS}...")
                            
                            # Tìm lại các typing-line elements (content đã update)
                            print("🔎 Re-finding typing-line elements...")
                            typing_elements = self._page.query_selector_all('div.w-full.typing-line')
                            print(f"📊 Found {len(typing_elements)} typing-line elements")
                            
                            if len(typing_elements) >= 2:
                                # Lấy 2 element đầu tiên
                                first_element = typing_elements[0]
                                second_element = typing_elements[1]
                                
                                # Trích xuất text từ mỗi element
                                first_text = first_element.inner_text().strip()
                                second_text = second_element.inner_text().strip()
                                
                                print(f"📝 First element text: '{first_text}'")
                                print(f"📝 Second element text: '{second_text}'")
                                
                                # Nối 2 đoạn văn bằng khoảng trắng và thêm khoảng trắng vào cuối
                                extracted_text = f"{first_text} {second_text} "
                                
                                # Đếm số từ trong round này
                                word_count = len(extracted_text.split())
                                
                                print(f"📝 Combined text: '{extracted_text}'")
                                print(f"📏 Total length: {len(extracted_text)}")
                                print(f"🔢 Số từ trong round {round_num}: {word_count} từ")
                                
                                # Biến để đánh dấu là round cuối cùng
                                is_final_round = False
                                
                                # KIỂM TRA TRƯỚC KHI CỘNG: Nếu tổng sẽ vượt giới hạn, cắt bớt text
                                if total_word_count + word_count > LIMIT_COUNT_WORD:
                                    print(f"⚠️ Sẽ vượt giới hạn! ({total_word_count} + {word_count} > {LIMIT_COUNT_WORD})")
                                    
                                    # Tính số từ cần lấy
                                    words_needed = LIMIT_COUNT_WORD - total_word_count
                                    print(f"📊 Số từ cần lấy: {words_needed} từ")
                                    
                                    # Tách text thành mảng từ
                                    words_array = extracted_text.split()
                                    
                                    # Lấy số từ cần thiết từ đầu
                                    trimmed_words = words_array[:words_needed]
                                    
                                    # Thêm từ "error" vào cuối
                                    trimmed_words.append("error")
                                    
                                    # Nối lại thành text và thêm khoảng trắng cuối
                                    extracted_text = " ".join(trimmed_words) + " "
                                    
                                    print(f"✂️ Đã cắt text: '{extracted_text}'")
                                    print(f"📊 Số từ sau khi cắt + error: {len(extracted_text.split())} từ")
                                    
                                    # Cập nhật tổng số từ
                                    total_word_count = LIMIT_COUNT_WORD  # Đặt đúng = giới hạn
                                    is_final_round = True  # Đánh dấu là round cuối
                                else:
                                    # Không vượt giới hạn, cộng bình thường
                                    total_word_count += word_count
                                
                                print(f"📊 Tổng số từ: {total_word_count}/{LIMIT_COUNT_WORD} từ")
                                
                                # KHÔNG CONVERT TELEX - TYPE TRỰC TIẾP UNICODE
                                print(f"📝 Typing Unicode text directly...")
                                
                                # Re-focus vào input trước khi typing - DÙNG PLAYWRIGHT API
                                print("🎯 Re-focusing on input with Playwright...")
                                typing_input = self._page.query_selector('input#typing-input')
                                if typing_input:
                                    typing_input.click()
                                    time.sleep(0.1)
                                
                                # TYPE TRỰC TIẾP UNICODE
                                print(f"⌨️ Typing round {round_num} with Unicode...")
                                
                                for i, char in enumerate(extracted_text):
                                    typing_input.type(char, delay=TYPING_DELAY_MS)
                                    
                                    if (i + 1) % 20 == 0:
                                        print(f"⌨️ Round {round_num}: Typed {i + 1}/{len(extracted_text)} characters")
                                
                                print(f"✅ Round {round_num} completed!")
                                time.sleep(ROUND_COMPLETE_WAIT)
                                
                                # Nếu là round cuối cùng (đã đạt giới hạn), thoát luôn
                                if is_final_round:
                                    print(f"🎯 ĐÃ ĐẠT GIỚI HẠN {LIMIT_COUNT_WORD} TỪ - THOÁT KHỎI VÒNG LẶP!")
                                    print(f"✅ Tổng cộng: {total_word_count} từ")
                                    break
                            else:
                                print(f"⚠️ Round {round_num}: Found less than 2 typing-line elements")
                                print(f"📊 Only found {len(typing_elements)} element(s)")
                                break
                        
                        print("\n✅ Finished all 10 rounds of typing!")
                        time.sleep(2)
                    else:
                        print("❌ typing-input element not found")
                else:
                    print("⚠️ Found less than 2 typing-line elements")
                    print(f"📊 Only found {len(typing_elements)} element(s)")
                
                print("✅ Text extraction and typing completed!")
                
                # Không đóng browser để có thể thao tác tiếp
                print("⚠️ Browser will remain open for manual interaction")
                print("💡 Browser instance is active and ready for further commands")
                
                # Lưu browser và page instance để có thể dùng sau
                # browser.close()  # Commented out - browser stays open
                
                print("✅ Browser opened and ready for interaction")
                
                return {
                    'success': True,
                    'url': TARGET_URL,
                    'title': title,
                    'timestamp': time.time()
                }
            
            # Run in thread pool to avoid blocking asyncio loop
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as pool:
                result = await loop.run_in_executor(pool, run_playwright)
            
            return result

        except Exception as e:
            error_msg = f"❌ Browser navigation failed: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e),
                'timestamp': time.time()
            }