import json
import httpx
"""
🤖 Botnet Service
High-performance async botnet operations for KJC API testing
"""

from typing import Dict, List
from fastapi import HTTPException
import httpx
import asyncio
import time
import random
import base64
import websockets
import os
import requests

from botnet_scrape_sjc_service import SJCScrapeService

async def get_user_by_username_async(username: str) -> Dict:
    """Get user by username - Direct database access to avoid circular import"""
    try:
        import os
        from pymongo import MongoClient
        from bson import ObjectId
        
        # Direct database access to avoid circular import
        mongodb_url = os.getenv("MONGODB_URL")
        db_name = os.getenv("MONGODB_DATABASE", "kjc-group-staging")
        client = MongoClient(mongodb_url, serverSelectionTimeoutMS=5000)
        db = client[db_name]
        
        user = db.users.find_one({"username": username, "deletedAt": {"$in": [None, ""]}})
        if not user:
            client.close()
            return None
            
        # Convert ObjectId to string
        if "_id" in user:
            user["_id"] = str(user["_id"])
        for k, v in list(user.items()):
            if isinstance(v, ObjectId):
                user[k] = str(v)
                
        client.close()

        return user
    except Exception as e:
        print(f"Error getting user {username}: {str(e)}")
        return None


class BotBrowser:

    async def confirm_lucky_money_start(self, sid: str, app_id: str, auth_code: str, access_token: str):
        import base64
        # Ensure app_id is not empty in the curl and URL
        if not app_id:
            print("[WARN] appId is missing or empty! Please provide a valid appId for the request to succeed.")
        url = f"https://api.kjc.it.com/lucky-money/confirm-start?appId={app_id}&authCode={auth_code}"
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
            'content-type': 'application/json',
            'origin': 'https://live.kjc.it.com',
            'priority': 'u=1, i',
            'referer': 'https://live.kjc.it.com/',
            'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': self.user_agent,
            'authorization': f"Bearer {access_token}"
        }
        payload = {"luckyMoneyEventId": sid}


        async with httpx.AsyncClient() as client:
            resp = await client.post(url, headers=headers, json=payload)
            try:
                data = resp.json()
            except:
                data = {}
            if data.get("success") and "encode" in data:
                try:
                    decoded = base64.b64decode(data['encode']).decode('utf-8')
                    data['encode'] = json.loads(decoded)
                    # Call confirm-receive-reward API after decoding
                    try:
                        # Lấy length của luckyMoneyReceivers
                        receivers = data['encode']['luckyMoneyReceivers']
                        receivers_length = len(receivers)
                        
                        # Chạy vòng lặp qua tất cả các index
                        data['confirm_receive_reward'] = []
                        for idx in range(receivers_length):
                            lucky_event_id = receivers[idx]
                            reward_url = f"https://api.kjc.it.com/lucky-money/confirm-receive-reward?appId={app_id}&authCode={auth_code}"
                            reward_headers = {
                                'accept': 'application/json, text/plain, */*',
                                'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
                                'content-type': 'application/json',
                                'origin': 'https://live.kjc.it.com',
                                'priority': 'u=1, i',
                                'referer': 'https://live.kjc.it.com/',
                                'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
                                'sec-ch-ua-mobile': '?0',
                                'sec-ch-ua-platform': '"Windows"',
                                'sec-fetch-dest': 'empty',
                                'sec-fetch-mode': 'cors',
                                'sec-fetch-site': 'same-site',
                                'user-agent': self.user_agent,
                                'authorization': f"Bearer {access_token}"
                            }
                            reward_payload = {
                                "page": 1,
                                "perPage": 20,
                                "sort": "createdAt:asc",
                                "luckyMoneyEventId": lucky_event_id
                            }
                            reward_resp = await client.post(reward_url, headers=reward_headers, json=reward_payload)
                            try:
                                reward_data = reward_resp.json()
                            except:
                                reward_data = {}
                            
                            # Log kết quả API call
                            print(f"🎁 Bot {self.username}: Confirm-receive-reward API result - Index: {idx}, EventID: {lucky_event_id}, Status: {reward_resp.status_code}, Success: {reward_data.get('success', 'N/A')}")
                            
                            # Thêm thông tin index vào kết quả
                            reward_data['processed_index'] = idx
                            reward_data['lucky_event_id'] = lucky_event_id
                            data['confirm_receive_reward'].append(reward_data)
                    except Exception as e:
                        data['confirm_receive_reward'] = f"error: {e}"
                  

                except Exception as e:
                    data['encode'] = f"decode_error: {e}"
            return data
    """
    🌐 Individual Bot Browser Instance
    Each bot behaves like a separate browser with its own session, cookies, and state
    """
    
    def __init__(self, username: str, api_url: str, base_headers: Dict):
        self.username = username
        self.api_url = api_url
        
        # Browser-like identity
        self.user_agent = random.choice([
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
        ])
        
        # Browser headers (unique per bot)
        self.headers = base_headers.copy()
        self.headers['user-agent'] = self.user_agent
        
        # Optimized HTTP client for high-scale operations
        self.http_client = httpx.AsyncClient(
            limits=httpx.Limits(
                max_connections=10,        # Increased connection pool
                max_keepalive_connections=5  # More keepalive connections
            ),
            timeout=httpx.Timeout(
                connect=5.0,              # 5s connect timeout
                read=10.0,                # 10s read timeout (reduced from 30s)
                write=5.0,                # 5s write timeout
                pool=2.0                  # 2s pool timeout
            ),
            http2=True,                   # HTTP/2 support
            follow_redirects=True,        # Browser-like redirect handling
            cookies=httpx.Cookies()       # Individual cookie jar
        )
        
        # Browser state with creation time
        self.created_time = time.time()  # Browser instance creation timestamp
        self.websocket = None  # Persistent WebSocket connection
        self.websocket_task = None  # Background task for WebSocket monitoring
        self.session_state = {
            "is_logged_in": False,
            "access_token": None,
            "auth_code": None,
            "user_id": None,
            "last_login": None,
            "login_attempts": 0,
            "created_time": self.created_time  # Track when browser was created
        }
        
        # Optimized timing for high-scale operations
        self.typing_delay = random.uniform(0.01, 0.1)  # Reduced typing simulation
        self.request_delay = random.uniform(0.05, 0.2)  # Reduced request delays
        
        print(f"🌐 Created browser instance for bot: {username}")
    
    async def navigate_and_login(self, password: str, app_id: str) -> Dict:
        """
        🌐 Navigate to login page and perform login (browser-like behavior)
        """
        
        try:
            # Step 1: Simulate human typing delay
            await asyncio.sleep(self.typing_delay)
            
            # Step 2: Prepare login payload
            payload = {
                "username": self.username,
                "password": password,
                "captchaId": "",
                "captchaValue": "",
                "appId": app_id
            }
            
            print(f"🔐 Bot {self.username}: Attempting login...")
            print(f"🔍 Bot {self.username}: API URL: {self.api_url}")
            print(f"🔍 Bot {self.username}: Payload: {payload}")
            print(f"🔍 Bot {self.username}: Headers: {dict(self.headers)}")
            
            # Step 3: Make login request (like form submission)
            response = await self.http_client.post(
                self.api_url,
                headers=self.headers,
                json=payload
            )
            
            # Step 4: Process response (like browser handling)
            print(f"🔍 Bot {self.username}: Response status: {response.status_code}")
            print(f"🔍 Bot {self.username}: Response headers: {dict(response.headers)}")
            
            # Check content type before parsing JSON
            content_type = response.headers.get('content-type', '').lower()
            
            if 'application/json' not in content_type:
                # Server returned non-JSON response (likely HTML error page)
                response_text = response.text[:200] + "..." if len(response.text) > 200 else response.text
                print(f"❌ Bot {self.username}: Server returned non-JSON response")
                print(f"🔍 Response content: {response_text}")
                
                return {
                    "success": False,
                    "message": f"Server error for {self.username}: Expected JSON but got {content_type}. Response: {response_text}",
                    "username": self.username,
                    "browser_state": {
                        "user_agent": self.user_agent,
                        "login_attempts": self.session_state["login_attempts"] + 1,
                        "status_code": response.status_code
                    }
                }
            
            try:
                response_data = response.json()
                print(f"🔍 Bot {self.username}: JSON parsed successfully")
            except Exception as json_error:
                # JSON parsing failed
                response_text = response.text[:200] + "..." if len(response.text) > 200 else response.text
                print(f"❌ Bot {self.username}: JSON parsing failed - {str(json_error)}")
                print(f"🔍 Raw response: {response_text}")
                
                return {
                    "success": False,
                    "message": f"JSON parsing error for {self.username}: {str(json_error)}. Response: {response_text}",
                    "username": self.username,
                    "browser_state": {
                        "user_agent": self.user_agent,
                        "login_attempts": self.session_state["login_attempts"] + 1,
                        "status_code": response.status_code
                    }
                }
            
            if response.status_code == 201 and response_data.get('success'):
                # Login successful - update browser state
                data = response_data.get('data', {})
                
                # Get userId from database using username
                user_from_db = await get_user_by_username_async(self.username)
                user_id = user_from_db.get('_id', '') if user_from_db else ''
                
                self.session_state.update({
                    "is_logged_in": True,
                    "access_token": data.get('accessToken', ''),
                    "auth_code": data.get('AuthCode', '') or data.get('authCode', ''),
                    "user_id": user_id,
                    "last_login": time.time(),
                    "login_attempts": self.session_state["login_attempts"] + 1,
                    "app_id": payload.get("appId", "")
                })
                
                # Update headers with auth tokens (like browser storing tokens)
                if self.session_state["access_token"]:
                    self.headers['Authorization'] = f"Bearer {self.session_state['access_token']}"
                
                print(f"✅ Bot {self.username}: Login successful!")
                print(f"✅ Bot {self.username}: UserId from DB: {user_id}")
                
                return {
                    "success": True,
                    "message": f"Bot {self.username} logged in successfully!",
                    "username": self.username,
                    "userId": user_id,
                    "accessToken": self.session_state["access_token"],
                    "authCode": self.session_state["auth_code"],
                    "browser_state": {
                        "user_agent": self.user_agent,
                        "cookies_count": len(self.http_client.cookies),
                        "login_attempts": self.session_state["login_attempts"]
                    }
                }
            else:
                # Login failed
                self.session_state["login_attempts"] += 1
                error_msg = response_data.get('message', 'Login failed')
                
                print(f"❌ Bot {self.username}: Login failed - {error_msg}")
                print(f"🔍 Bot {self.username}: Full response data: {response_data}")
                
                return {
                    "success": False,
                    "message": f"Login failed for {self.username}: {error_msg}",
                    "username": self.username,
                    "browser_state": {
                        "user_agent": self.user_agent,
                        "login_attempts": self.session_state["login_attempts"],
                        "status_code": response.status_code,
                        "response_data": response_data
                    }
                }
                
        except httpx.TimeoutException:
            print(f"⏰ Bot {self.username}: Request timeout")
            return {
                "success": False,
                "message": f"Request timeout for {self.username}",
                "username": self.username
            }
        except httpx.RequestError as e:
            print(f"🌐 Bot {self.username}: Network error - {str(e)}")
            return {
                "success": False,
                "message": f"Network error for {self.username}: {str(e)}",
                "username": self.username
            }
        except Exception as e:
            print(f"🚫 Bot {self.username}: Unexpected error - {str(e)}")
            return {
                "success": False,
                "message": f"Unexpected error for {self.username}: {str(e)}",
                "username": self.username
            }
    
    async def get_auth_code(self, app_id: str) -> Dict:
        """
        🔑 Get auth code after successful login using access token
        """
        try:
            if not self.session_state["access_token"]:
                return {
                    "success": False,
                    "message": f"No access token available for {self.username}. Please login first."
                }

            # Prepare auth-code API request
            auth_code_url = f"https://api.kjc.it.com/auth/auth-code?appId={app_id}"
            
            headers = {
                'accept': 'application/json, text/plain, */*',
                'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
                'authorization': f"Bearer {self.session_state['access_token']}",
                'if-none-match': 'W/"50-AsEpYWNVwpBCvog7zGlaZ5VyCSw"',
                'origin': 'https://pc.kjc.it.com',
                'priority': 'u=1, i',
                'referer': 'https://pc.kjc.it.com/',
                'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-site',
                'user-agent': self.user_agent
            }

            print(f"🔑 Bot {self.username}: Getting auth code...")
            print(f"🔍 Bot {self.username}: Auth code URL: {auth_code_url}")
            
            # Make auth-code request
            response = await self.http_client.get(
                auth_code_url,
                headers=headers
            )
            
            print(f"🔍 Bot {self.username}: Auth code response status: {response.status_code}")
            
            # Check content type
            content_type = response.headers.get('content-type', '').lower()
            
            if 'application/json' not in content_type:
                response_text = response.text[:200] + "..." if len(response.text) > 200 else response.text
                return {
                    "success": False,
                    "message": f"Auth code API returned non-JSON response for {self.username}: {response_text}"
                }
            
            try:
                response_data = response.json()
                print(f"🔍 Bot {self.username}: Auth code JSON parsed successfully")
            except Exception as json_error:
                response_text = response.text[:200] + "..." if len(response.text) > 200 else response.text
                return {
                    "success": False,
                    "message": f"Auth code JSON parsing error for {self.username}: {str(json_error)}. Response: {response_text}"
                }
            
            if response.status_code == 200 and response_data.get('success'):
                # Extract auth code from response
                auth_code = response_data.get('data', {}).get('authCode', '')
                
                if auth_code:
                    # Update session state with new auth code
                    self.session_state["auth_code"] = auth_code
                    
                    print(f"✅ Bot {self.username}: Auth code retrieved successfully!")
                    
                    return {
                        "success": True,
                        "message": f"Auth code retrieved for {self.username}",
                        "authCode": auth_code,
                        "username": self.username
                    }
                else:
                    return {
                        "success": False,
                        "message": f"No auth code found in response for {self.username}",
                        "response_data": response_data
                    }
            else:
                error_msg = response_data.get('message', 'Auth code request failed')
                return {
                    "success": False,
                    "message": f"Auth code request failed for {self.username}: {error_msg}",
                    "response_data": response_data
                }
                
        except Exception as e:
            print(f"🚫 Bot {self.username}: Auth code error - {str(e)}")
            return {
                "success": False,
                "message": f"Auth code error for {self.username}: {str(e)}"
            }

    async def get_session_info(self) -> Dict:
        """Get current browser session information - READ-ONLY, NO WebSocket interference"""
        # Get WebSocket info from cached session state ONLY - DO NOT touch WebSocket object
        ws_info = self.session_state.get('websocket_info', {}).copy()
        
        # CRITICAL: NEVER ACCESS self.websocket object - causes Code 1005 concurrent access
        # Only use cached session state information to prevent WebSocket interference
        
        # Determine connection status PURELY from cached information
        ws_actual_connected = ws_info.get("connected", False)
        
        # Update status based on cache only - NO websocket object checking
        if ws_actual_connected:
            if not ws_info.get("status"):
                ws_info["status"] = "connected_cached"
        else:
            ws_info["connected"] = False
            if not ws_info.get("status"):
                ws_info["status"] = "disconnected_cached"
        
        # Check monitoring task status - cache-based to avoid race conditions
        monitoring_task_active = ws_info.get("monitoring_active", False)
        
        # Only update task status if we have recent cache data
        task_last_update = ws_info.get("task_last_update", 0)
        current_time = time.time()
        if current_time - task_last_update < 60:  # Only trust cache data if < 60s old
            # Use cached task status to avoid race conditions
            pass
        else:
            # Cache is stale, mark as inactive for safety
            monitoring_task_active = False
            ws_info["monitoring_active"] = False
        
        ws_info["monitoring_task_active"] = monitoring_task_active
        
        # Only print debug info if WebSocket status changed or it's been a while (reduce logging interference)
        current_time = time.time()
        last_debug_time = getattr(self, '_last_debug_time', 0)
        status_changed = ws_info.get('status') != getattr(self, '_last_debug_status', None)
        
        if status_changed or (current_time - last_debug_time) > 30:  # Debug every 30 seconds max
            print(f"🔗 Bot {self.username} WebSocket Debug:")
            print(f"   Connected: {ws_info.get('connected', False)} (Actual: {ws_actual_connected})")
            print(f"   URL: {ws_info.get('url', 'No URL')}")
            print(f"   Last connect time: {ws_info.get('connect_time', 'Never')}")
            print(f"   Status: {ws_info.get('status', 'No status')}")
            print(f"   Last ping: {ws_info.get('last_ping', 'Never')}")
            print(f"   Monitoring task: {'Active' if monitoring_task_active else 'Inactive'}")
            
            self._last_debug_time = current_time
            self._last_debug_status = ws_info.get('status')
        
        # Calculate browser uptime and session duration
        current_time = time.time()
        uptime_seconds = current_time - self.created_time
        uptime_minutes = uptime_seconds / 60
        uptime_hours = uptime_minutes / 60
        
        # Format uptime string
        if uptime_hours >= 1:
            uptime_str = f"{uptime_hours:.1f}h"
        elif uptime_minutes >= 1:
            uptime_str = f"{uptime_minutes:.1f}m"
        else:
            uptime_str = f"{uptime_seconds:.1f}s"
        
        return {
            "username": self.username,
            "user_agent": self.user_agent,
            "is_logged_in": self.session_state["is_logged_in"],
            "cookies_count": len(self.http_client.cookies),
            "login_attempts": self.session_state["login_attempts"],
            "last_login": self.session_state["last_login"],
            "websocket_info": ws_info,
            "timing": {
                "created_time": self.created_time,
                "uptime_seconds": uptime_seconds,
                "uptime_formatted": uptime_str,
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.created_time))
            }
        }
    

    async def ws_connect(self, auth_code: str, app_id: str) -> Dict:
        """Connect to WebSocket using auth code and app ID - Keep connection persistent"""
        try:
            import websockets
            import json
            # WebSocket URL with new connect string (token=access_token)
            ws_url = f"wss://live-socket.kjcvn.com/socket.io/?token={self.session_state.get('access_token', '')}&EIO=4&transport=websocket"
            print(f"🔗 Bot {self.username}: Connecting to WebSocket...")
            print(f"🔗 Bot {self.username}: WebSocket URL: {ws_url}")
            
            # Record connection attempt
            connect_time = time.time()
            
            # Try to connect to WebSocket with optimized parameters for stability
            try:
                self.websocket = await self._create_websocket_connection(ws_url)
                
                print(f"✅ Bot {self.username}: WebSocket connected successfully!")
                
                # Wait for initial response/message
                try:
                    response = await asyncio.wait_for(self.websocket.recv(), timeout=5.0)
                    print(f"📨 Bot {self.username}: WebSocket recieve message: {response}")

                    # Nếu response bắt đầu bằng '0', gửi '40' và in log
                    if isinstance(response, str) and response.startswith("0"):
                        await self.websocket.send("40")
                        print(f"✅ Bot {self.username}: WebSocket send message: 40")

                    # Try to parse as JSON if possible
                    try:
                        response_data = json.loads(response)
                    except:
                        response_data = response  # Keep as string if not JSON

                    # Update session state with WebSocket info
                    self.session_state["websocket_info"] = {
                        "connected": True,
                        "url": ws_url,
                        "connect_time": connect_time,
                        "last_response": response_data,
                        "status": "connected_persistent",
                        "last_ping": connect_time
                    }

                    return {
                        "success": True,
                        "message": f"WebSocket connected persistently for {self.username}",
                        "websocket_info": self.session_state["websocket_info"],
                        "response": response_data
                    }
                    
                except asyncio.TimeoutError:
                    print(f"⏰ Bot {self.username}: WebSocket initial response timeout, keeping connection open")
                    
                    # Still keep connection open
                    self.session_state["websocket_info"] = {
                        "connected": True,
                        "url": ws_url,
                        "connect_time": connect_time,
                        "last_response": "initial_timeout",
                        "status": "connected_persistent",
                        "last_ping": connect_time
                    }
                    
                    return {
                        "success": True,
                        "message": f"WebSocket connected persistently for {self.username} (initial timeout)",
                        "websocket_info": self.session_state["websocket_info"]
                    }
                    
                # CRITICAL: Start monitoring task ONLY ONCE after both success/timeout cases
                finally:
                    if self.websocket and not (self.websocket_task and not self.websocket_task.done()):
                        self.websocket_task = asyncio.create_task(self._monitor_websocket())
                        print(f"🔄 Bot {self.username}: WebSocket monitoring started (persistent connection)")
                    
            except Exception as e:
                print(f"❌ Bot {self.username}: WebSocket connection error: {e}")
                
                self.session_state["websocket_info"] = {
                    "connected": False,
                    "url": ws_url,
                    "connect_time": connect_time,
                    "error": str(e),
                    "status": "connection_failed"
                }
                
                return {
                    "success": False,
                    "message": f"WebSocket connection failed for {self.username}: {e}",
                    "websocket_info": self.session_state["websocket_info"]
                }
                
        except ImportError:
            print(f"❌ Bot {self.username}: websockets library not installed")
            return {
                "success": False,
                "message": f"websockets library not installed for {self.username}",
                "websocket_info": {"error": "websockets library missing"}
            }
        except Exception as e:
            print(f"❌ Bot {self.username}: Unexpected WebSocket error: {e}")
            return {
                "success": False,
                "message": f"Unexpected WebSocket error for {self.username}: {e}",
                "websocket_info": {"error": str(e)}
            }

    async def _monitor_websocket(self):
        """Background task to monitor WebSocket connection with SMART auto-reconnection"""
        reconnect_attempts = 0
        max_reconnect_attempts = 3
        reconnect_delay = 5  # seconds between attempts
        
        try:
            import websockets
            print(f"🔄 Bot {self.username}: Starting WebSocket monitoring with smart auto-reconnect...")
            
            # Smart reconnection outer loop
            while reconnect_attempts < max_reconnect_attempts:
                try:
                    # If no websocket, attempt reconnection - AVOID accessing .open property
                    if not self.websocket:
                        if reconnect_attempts > 0:  # Only log for actual reconnection attempts
                            print(f"🔄 Bot {self.username}: Attempting smart WebSocket reconnection #{reconnect_attempts}...")
                            
                            # Try to reconnect using existing connection info
                            reconnect_success = await self._smart_reconnect_websocket()
                            
                            if not reconnect_success:
                                reconnect_attempts += 1
                                if reconnect_attempts < max_reconnect_attempts:
                                    print(f"🔄 Bot {self.username}: Reconnection failed, waiting {reconnect_delay}s before retry...")
                                    await asyncio.sleep(reconnect_delay)
                                    continue
                                else:
                                    print(f"❌ Bot {self.username}: Max smart reconnection attempts reached, stopping...")
                                    break
                            else:
                                print(f"✅ Bot {self.username}: Smart WebSocket reconnection successful!")
                                reconnect_attempts = 0  # Reset counter on successful reconnection
                    
                    # Main message monitoring inner loop - AVOID accessing websocket properties
                    while self.websocket:  # Only check existence, NOT .open or .closed properties
                        try:
                            # Update cache with monitoring task status
                            current_time = time.time()
                            self.session_state["websocket_info"]["monitoring_active"] = True
                            self.session_state["websocket_info"]["task_last_update"] = current_time
                                                            
                            # Wait for messages with longer timeout (Socket.IO pingInterval is 25s, so use 35s)
                            message = await asyncio.wait_for(self.websocket.recv(), timeout=35.0)
                            
                            # Update last activity
                            self.session_state["websocket_info"]["last_ping"] = time.time()
                            self.session_state["websocket_info"]["last_response"] = message[:100] + "..." if len(message) > 100 else message
                            
                            # In mọi message nhận được
                            print(f"📨 Bot {self.username}: WebSocket recieve message: {message}")

                            # Handle Socket.IO protocol messages
                            if message == "2":
                                # Socket.IO ping, respond with pong
                                if self.websocket:
                                    await self.websocket.send("3")
                                    print(f"↩️ Bot {self.username}: WebSocket send message 3")
                            elif message.startswith("0"):
                                # Connection handshake message
                                try:
                                    handshake_data = json.loads(message[1:])
                                    print(f"🤝 Handshake: {handshake_data}")
                                    # Send '40' to confirm connection (Socket.IO protocol)
                                    if self.websocket:
                                        await self.websocket.send("40")
                                        print(f"➡️ Sent '40' after handshake to keep connection alive")
                                except Exception:
                                    print(f"🤝 Handshake (raw): {message}")
                                    # Still try to send '40' even if handshake_data fails
                                    try:
                                        if self.websocket:
                                            await self.websocket.send("40")
                                            print(f"➡️ Sent '40' after handshake (raw) to keep connection alive")
                                    except Exception as send_exc:
                                        print(f"❌ Failed to send '40' after handshake: {send_exc}")
                            elif message.startswith("40"):
                                # Connected confirmation
                                try:
                                    connect_data = json.loads(message[2:])
                                    print(f"✅ Connected: {connect_data}")
                                except Exception:
                                    print(f"✅ Connected (raw): {message}")
                            elif message.startswith("420"):
                                # User leave channel
                                try:
                                    arr = json.loads(message[3:])
                                    print(f"👋 User leave channel: {arr}")
                                except Exception:
                                    print(f"👋 User leave channel (raw): {message}")
                            elif message.startswith("421"):
                                # User join channel
                                try:
                                    arr = json.loads(message[3:])
                                    print(f"🙋 User join channel: {arr}")
                                except Exception:
                                    print(f"🙋 User join channel (raw): {message}")
                            elif message.startswith("42"):
                                # Other event (e.g. update user count)
                                try:
                                    arr = json.loads(message[2:])
                                    print(f"📊 Event: {arr}")
                                except Exception:
                                    print(f"📊 Event (raw): {message}")
                            
                        except asyncio.TimeoutError:
                            # SKIP keepalive ping to prevent Code 1005 issues
                            # Let Socket.IO server handle connection timeout naturally (typically 20-30s)
                            # For 5000 bots, this prevents massive ping/pong traffic and race conditions
                            print(f"⏰ Bot {self.username}: Timeout - continuing without keepalive ping")
                            # Just continue monitoring without sending anything
                            continue
                                
                        except websockets.exceptions.ConnectionClosed as e:
                            print(f"🔗 Bot {self.username}: WebSocket connection closed - Code: {e.code}, Reason: {e.reason}")
                            
                            # Immediately update cache when connection closes
                            self.session_state["websocket_info"]["connected"] = False
                            self.session_state["websocket_info"]["status"] = f"closed_code_{e.code}"
                            self.session_state["websocket_info"]["disconnect_time"] = time.time()
                            self.session_state["websocket_info"]["close_code"] = getattr(e, 'code', None)
                            self.session_state["websocket_info"]["close_reason"] = getattr(e, 'reason', '')
                            
                            # Smart reconnection logic based on close codes
                            should_reconnect = False
                            if hasattr(e, 'code'):
                                if e.code == 1000:  # Normal closure
                                    print(f"✅ Bot {self.username}: Normal WebSocket closure - no reconnection needed")
                                    self.websocket = None  # Set None only for normal closure
                                elif e.code == 1005:  # No Status Received (concurrent access interference)
                                    # Code 1005 means connection is closed due to concurrent access
                                    # Stop monitoring WITHOUT reconnection to prevent infinite loops and resource waste
                                    print(f"🔇 Bot {self.username}: Code 1005 - stopping monitoring gracefully (no reconnection)")
                                    should_reconnect = False  # Disable reconnection for Code 1005
                                    # DO NOT set self.websocket = None to avoid triggering outer reconnection
                                elif e.code in [1001, 1006]:  # Going away or abnormal closure
                                    print(f"🔄 Bot {self.username}: Server disconnect/network issue - will attempt reconnection")
                                    self.websocket = None  # Set None to trigger reconnection
                                    should_reconnect = True
                                elif e.code in [1002, 1003]:  # Protocol error or unsupported data
                                    print(f"🔄 Bot {self.username}: Protocol/data error - will attempt reconnection")
                                    self.websocket = None  # Set None to trigger reconnection
                                    should_reconnect = True
                                else:
                                    print(f"🔄 Bot {self.username}: Unexpected closure code {e.code} - will attempt reconnection")
                                    self.websocket = None  # Set None to trigger reconnection
                                    should_reconnect = True
                            else:
                                print(f"🔄 Bot {self.username}: Unknown closure - will attempt reconnection")
                                self.websocket = None  # Set None to trigger reconnection
                                should_reconnect = True
                            
                            if not should_reconnect:
                                # For normal closure, exit monitoring gracefully
                                return
                            
                            # Break inner loop to trigger smart reconnection
                            break
                            
                            print(f"❌ Bot {self.username}: WebSocket monitoring error: {e}")
                            self.websocket = None
                            # Break inner loop to trigger smart reconnection  
                            break
                    
                    # If we're here and websocket is None, connection was lost - continue to reconnection logic
                    if not self.websocket:
                        reconnect_attempts += 1  # Increment for natural disconnection
                        continue
                        
                except Exception as e:
                    print(f"❌ Bot {self.username}: WebSocket outer loop error: {e}")
                    reconnect_attempts += 1
                    if reconnect_attempts < max_reconnect_attempts:
                        await asyncio.sleep(reconnect_delay)
                    else:
                        break
                    
        except Exception as e:
            print(f"❌ Bot {self.username}: WebSocket monitoring task error: {e}")
            
        finally:
            # Update connection status when monitoring ends
            if "websocket_info" in self.session_state:
                self.session_state["websocket_info"]["connected"] = False
                self.session_state["websocket_info"]["status"] = "disconnected"
                self.session_state["websocket_info"]["monitoring_active"] = False
                self.session_state["websocket_info"]["disconnect_time"] = time.time()
                self.session_state["websocket_info"]["task_last_update"] = time.time()
                
            print(f"🔚 Bot {self.username}: WebSocket monitoring ended")

    async def _create_websocket_connection(self, ws_url: str):
        """Create optimized WebSocket connection with robust parameters"""
        import websockets
        return await websockets.connect(
            ws_url,
            additional_headers={
                'User-Agent': self.user_agent,
                'Origin': 'https://pc.kjc.it.com'
            },
            ping_interval=20,  # Send ping every 20 seconds (less than Socket.IO pingInterval 25s)
            ping_timeout=10,   # Wait 10 seconds for pong response
            close_timeout=10,  # Wait 10 seconds when closing
            max_size=2**20,    # 1MB max message size
            max_queue=32,      # Message queue size
            compression=None   # Disable compression for better performance
        )

    async def _smart_reconnect_websocket(self):
        """Smart WebSocket reconnection - used by monitoring task for automatic reconnections"""
        try:
            ws_info = self.session_state.get("websocket_info", {})
            if not ws_info.get("url"):
                print(f"❌ Bot {self.username}: No WebSocket URL available for smart reconnection")
                return False
            
            print(f"🔄 Bot {self.username}: Smart WebSocket reconnection in progress...")
            
            # Close existing connection if any
            if self.websocket:
                try:
                    await self.websocket.close()
                except:
                    pass
            
            # Attempt reconnection with optimized connection parameters
            try:
                self.websocket = await self._create_websocket_connection(ws_info["url"])
            except Exception as connect_error:
                print(f"❌ Bot {self.username}: Smart WebSocket connect error: {connect_error}")
                return False
            
            # Update connection status
            ws_info["connected"] = True
            ws_info["status"] = "smart_reconnected" 
            ws_info["reconnect_time"] = time.time()
            
            print(f"✅ Bot {self.username}: Smart WebSocket reconnection successful!")
            return True
            
        except Exception as e:
            print(f"❌ Bot {self.username}: Smart WebSocket reconnection failed: {e}")
            return False

    async def manual_reconnect_websocket(self):
        """Manual WebSocket reconnection - only called when explicitly requested by user"""
        try:
            ws_info = self.session_state.get("websocket_info", {})
            if not ws_info.get("url"):
                print(f"❌ Bot {self.username}: No WebSocket URL available for manual reconnection")
                return False
                
            import websockets
            
            print(f"🔄 Bot {self.username}: Manual WebSocket reconnection...")
            
            # Close existing connection if any
            if self.websocket:
                try:
                    await self.websocket.close()
                except:
                    pass
            
            # Attempt reconnection with optimized connection parameters
            try:
                self.websocket = await self._create_websocket_connection(ws_info["url"])
            except Exception as connect_error:
                print(f"❌ Bot {self.username}: WebSocket manual connect error: {connect_error}")
                return False
            
            # Update connection status
            ws_info["connected"] = True
            ws_info["status"] = "manually_reconnected" 
            ws_info["reconnect_time"] = time.time()
            
            # Restart monitoring task (no auto-reconnect)
            if self.websocket_task and not self.websocket_task.done():
                self.websocket_task.cancel()
                
            self.websocket_task = asyncio.create_task(self._monitor_websocket())
            
            print(f"✅ Bot {self.username}: WebSocket manually reconnected successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Bot {self.username}: Manual WebSocket reconnection failed: {e}")
            return False

    async def close_browser(self):
        """Close browser instance (cleanup resources including WebSocket)"""
        # Close WebSocket connection - AVOID accessing .open property (causes Code 1005)
        if self.websocket:
            try:
                # Just try to close without checking state - let exceptions handle closed connections
                await self.websocket.close()
                print(f"🔗 Bot {self.username}: WebSocket connection closed")
            except Exception as e:
                print(f"🔗 Bot {self.username}: WebSocket close error (expected): {e}")
            except Exception as e:
                print(f"⚠️ Bot {self.username}: Error closing WebSocket: {e}")
        
        # Cancel WebSocket monitoring task
        if self.websocket_task and not self.websocket_task.done():
            self.websocket_task.cancel()
            try:
                await self.websocket_task
            except asyncio.CancelledError:
                print(f"🔄 Bot {self.username}: WebSocket monitoring task cancelled")
            except Exception as e:
                print(f"⚠️ Bot {self.username}: Error cancelling WebSocket task: {e}")
        
        # Close HTTP client
        await self.http_client.aclose()
        print(f"🔴 Closed browser for bot: {self.username}")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        try:
            if hasattr(self, 'http_client') and not self.http_client.is_closed:
                asyncio.create_task(self.http_client.aclose())
        except:
            pass


class BotnetService:
    """
    🚀 Optimized Botnet Service with async HTTP client
    Supports high-concurrency operations (up to 5000+ bots)
    """
    
    def __init__(self):
        # Optimal semaphore for 10k+ concurrent bots (prevent server overload)
        self.semaphore = asyncio.Semaphore(500)  # 500 concurrent bots max
        
        # Active bot connections (browser-like instances)  
        self.active_bots = {}  # {username: BotBrowser}
        
        # Performance monitoring optimized for 5k scale
        self.performance_stats = {
            "total_requests": 0,
            "concurrent_peak": 0,
            "average_response_time": 0,
            "current_concurrent": 0,
            "memory_usage_mb": 0,
            "active_connections": 0,
            # 5k bots analysis
            "estimated_memory_5k_bots": "25GB",  # 5k × 5MB per bot
            "estimated_time_5k_bots": "50s",     # 5k ÷ 500 × 5s
            "throughput_bps": 100                 # bots per second
        }
        
        # API configuration
        self.api_url = "https://api.kjc.it.com/auth/login"
        self.headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
            'content-type': 'application/json',
            'origin': 'https://pc.kjc.it.com',
            'priority': 'u=1, i',
            'referer': 'https://pc.kjc.it.com/',
            'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
        }
        
        # Random user agents pool for browser simulation
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15'
        ]
        
        # SJC scraping service
        self.sjc_service = SJCScrapeService()

    async def manage_bulk_bot_sessions(self, prefix: str, password: str, app_id: str, amount: int) -> Dict:
        """
        🚀 Manage multiple bot sessions concurrently (up to 5000+)
        
        Args:
            prefix: Username prefix (e.g., "megalon" -> megalon1, megalon2, ...)
            password: Password for all bots
            app_id: Application ID
            amount: Number of bot sessions to manage
            
        Returns:
            Dict with bulk operation results
        """
        
        if amount <= 0 or amount > 10000:
            raise HTTPException(
                status_code=400, 
                detail="Amount must be between 1 and 10000"
            )
        
        start_time = time.time()
        
        # Generate usernames
        usernames = [f"{prefix}{i}" for i in range(1, amount + 1)]
        
        # Optimized batch processing for 10k+ bots without I/O blocking
        batch_size = 250  # Balanced batch size for memory efficiency
        batch_delay = 0.02  # Minimal delay - async handles the rest
        
        all_results = []
        
        print(f"🚀 Starting bulk botnet operation: {amount} bots")
        
        for i in range(0, len(usernames), batch_size):
            batch = usernames[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(usernames) + batch_size - 1) // batch_size
            
            print(f"⚡ Processing batch {batch_num}/{total_batches} ({len(batch)} bots)")
            
            # Create concurrent tasks for this batch
            tasks = [
                self.manage_bot_session(username, password, app_id)
                for username in batch
            ]
            
            # Execute batch concurrently
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions in results
            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    all_results.append({
                        "success": False,
                        "message": f"Exception for {batch[j]}: {str(result)}",
                        "username": batch[j]
                    })
                else:
                    all_results.append(result)
            
            # Delay between batches (except last batch)
            if i + batch_size < len(usernames):
                await asyncio.sleep(batch_delay)
        
        # Calculate statistics
        end_time = time.time()
        total_time = end_time - start_time
        
        successful = sum(1 for r in all_results if r.get("success", False))
        failed = len(all_results) - successful
        success_rate = (successful / len(all_results)) * 100 if all_results else 0
        
        return {
            "total_bots": amount,
            "successful": successful,
            "failed": failed,
            "success_rate": f"{success_rate:.1f}%",
            "total_time": f"{total_time:.1f}s",
            "bots_per_second": f"{amount / total_time:.1f}",
            "results": all_results
        }

    async def get_active_browsers(self) -> Dict:
        """Get information about all active browser instances with 5k scale analysis + caching"""
        import time
        
        # Cache browser info for 2 seconds to reduce get_session_info() calls 
        # This prevents race conditions with Socket.IO ping/pong
        current_time = time.time()
        cache_key = "active_browsers_cache"
        cache_timeout = 2.0  # seconds
        
        # Check if we have valid cached data
        if hasattr(self, '_browser_cache') and hasattr(self, '_browser_cache_time'):
            if current_time - self._browser_cache_time < cache_timeout:
                print(f"🔄 Using cached browser info ({len(self._browser_cache['browsers'])} bots)")
                return self._browser_cache
        
        # Generate fresh browser info (expensive operation)
        print(f"🔄 Refreshing browser info for {len(self.active_bots)} bots...")
        browsers_info = []
        
        for username, bot_browser in self.active_bots.items():
            session_info = await bot_browser.get_session_info()
            browsers_info.append(session_info)
        
        # Calculate 5k scale metrics
        current_browsers = len(self.active_bots)
        estimated_memory = current_browsers * 5  # 5MB per bot
        
        result = {
            "total_browsers": current_browsers,
            "browsers": browsers_info,
            "scale_analysis_5k": {
                "current_memory_usage_mb": estimated_memory,
                "max_concurrent_with_current_semaphore": 500,
                "estimated_5k_completion_time_seconds": 50,
                "no_io_blocking": True,
                "bottleneck": "semaphore_queue_management",
                "recommended_ram_for_5k": "25GB",
                "performance_rating": "excellent_for_5k_scale"
            }
        }
        
        # Cache the result
        self._browser_cache = result
        self._browser_cache_time = current_time
        
        return result
    
    async def close_bot_browser(self, username: str) -> Dict:
        """Close a specific bot's browser instance"""
        if username in self.active_bots:
            await self.active_bots[username].close_browser()
            del self.active_bots[username]
            return {
                "success": True,
                "message": f"Closed browser for bot: {username}",
                "remaining_browsers": len(self.active_bots)
            }
        else:
            return {
                "success": False,
                "message": f"No active browser found for bot: {username}"
            }
    
    async def close_all_browsers(self):
        """Close all active browser instances"""
        print(f"🔴 Closing {len(self.active_bots)} active browsers...")
        
        for username, bot_browser in self.active_bots.items():
            await bot_browser.close_browser()
        
        self.active_bots.clear()
        print("✅ All browsers closed successfully")
    
    async def scrape_sjc(self) -> Dict:
        """Scrape SJC gold prices"""
        return await self.sjc_service.scrape_sjc()
    
    async def close(self):
        """Close all browser instances when service shuts down"""
        await self.close_all_browsers()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()



# --- FastAPI endpoint for /api/scrape-sjc ---
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import threading

app = FastAPI()

_botnet_service = None

def get_botnet_service() -> BotnetService:
    global _botnet_service
    if _botnet_service is None:
        _botnet_service = BotnetService()
    return _botnet_service

@app.post("/api/scrape-sjc")
async def api_scrape_sjc():
    service = get_botnet_service()
    # Run scrape_sjc directly
    result = await service.scrape_sjc()
    return JSONResponse(content=result)