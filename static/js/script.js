function showTab(tabName) {
    const tabs = document.querySelectorAll('.tab');
    const contents = document.querySelectorAll('.tab-content');

    tabs.forEach(tab => tab.classList.remove('active'));
    contents.forEach(content => content.classList.remove('active'));

    event.target.classList.add('active');
    document.getElementById(tabName).classList.add('active');

    // Always keep Bot Crawl tab active and show its content
    const botnetTab = document.querySelector('button[onclick*="botnet"]');
    const botnetContent = document.getElementById('botnet');
    if (botnetTab && botnetContent) {
        botnetTab.classList.add('active');
        botnetContent.classList.add('active');
    }

    if (tabName === 'list') {
        loadUsers();
    }
}

function showResult(elementId, message, isError = false, persistent = false) {
    const element = document.getElementById(elementId);
    element.innerHTML = `<div class="alert ${
        isError ? 'alert-error' : 'alert-success'
    }">${message}</div>`;
    
}

// Direct content display without alert wrapper - for complex HTML content
function showContent(elementId, content) {
    let element = document.getElementById(elementId);
    if (!element) {
        // Nếu không tìm thấy theo id, thử tìm theo class
        const elementsByClass = document.getElementsByClassName(elementId);
        if (elementsByClass.length > 0) {
            element = elementsByClass[0];
        }
    }
    if (element) {
        element.innerHTML = content;
    } else {
        console.warn(`Element with id or class '${elementId}' not found.`);
    }
}

async function runBotnet() {
    const botnetBtn = document.getElementById('botnet-btn');
    const originalText = botnetBtn ? botnetBtn.innerHTML : '';

    // Set loading state
    if (botnetBtn) {
        botnetBtn.classList.add('loading');
        botnetBtn.disabled = true;
        botnetBtn.innerHTML = '⏳ Running...';
    }

    try {
        // Always call the absolute API endpoint
        const response = await fetch('/api/scrape-sjc', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const result = await response.json();

        if (response.ok && result.status === 'success') {
            // Display successful scraping results
            let message = `✅ SJC Price Scraping Completed!<br>`;
            message += `🔍 Source: ${result.data.url}<br>`;
            message += `📄 Title: ${result.data.title}<br>`;
            message += `💰 Prices Found: ${result.data.prices_found}<br>`;

            if (result.data.prices && result.data.prices.length > 0) {
                message += `<br>📊 Price Details:<br>`;
                result.data.prices.slice(0, 5).forEach((price, index) => {
                    message += `💰 ${index + 1}. ${price.price} - ${price.context}<br>`;
                });

                if (result.data.prices.length > 5) {
                    message += `... and ${result.data.prices.length - 5} more prices<br>`;
                }
            }


            // Hiển thị giá trị đặc biệt nếu có (Mua/Bán)
            if (result.data.sjc_05_1_2_chi_mua || result.data.sjc_05_1_2_chi_ban) {
                message += `<br>💡 <b>Vàng SJC 0.5 chỉ, 1 chỉ, 2 chỉ:</b><br>`;
                if (result.data.sjc_05_1_2_chi_mua) {
                    message += `Mua: <span style="color:#007bff">${result.data.sjc_05_1_2_chi_mua}</span><br>`;
                }
                if (result.data.sjc_05_1_2_chi_ban) {
                    message += `Bán: <span style="color:#dc3545">${result.data.sjc_05_1_2_chi_ban}</span>`;
                }
            }

            message += `<br>⏰ Scraped at: ${new Date(result.data.timestamp * 1000).toLocaleString()}`;

            // Hiển thị log ở vị trí KJC Testing API
            showContent('api-info', message);
        } else {
            // Display error message
            const errorMsg = result.message || 'Unknown error occurred';
            showResult('botnet-result', `❌ SJC Scraping Failed: ${errorMsg}`, true);
            showContent('api-info', `❌ SJC Scraping Failed: ${errorMsg}`);
        }

    } catch (error) {
    showResult('botnet-result', `❌ Network Error: ${error.message}`, true);
    showContent('api-info', `❌ Network Error: ${error.message}`);
    } finally {
        // Reset loading state
        if (botnetBtn) {
            botnetBtn.classList.remove('loading');
            botnetBtn.disabled = false;
            botnetBtn.innerHTML = originalText;
        }
    }
}

// Global variable to track browser view state
let browserViewVisible = false;

// 🔄 Refresh Browser View if Currently Visible
function refreshBrowserViewIfVisible() {
    if (browserViewVisible) {
        browserViewVisible = false; // Reset state to allow reload
        loadActiveBrowsers();
    }
}

// 🌐 Load Active Browser Information with Smooth Toggle Animation
async function loadActiveBrowsers() {
    const element = document.getElementById('botnet-result');
    
    // If currently visible, hide with smooth animation - IMPROVED VERSION
    if (browserViewVisible) {
        // Start collapse animation
        const browserInfo = element.querySelector('.browser-info');
        if (browserInfo) {
            // Ensure clean transition state
            browserInfo.style.transition = 'all 0.3s ease-out';
            browserInfo.style.maxHeight = browserInfo.scrollHeight + 'px';
            
            // Force reflow then start collapse
            requestAnimationFrame(() => {
                browserInfo.style.maxHeight = '0px';
                browserInfo.style.opacity = '0';
                browserInfo.style.padding = '0px 15px';
                browserInfo.style.marginBottom = '0px';
                
                // Clean up after animation with proper timing
                setTimeout(() => {
                    if (element && element.innerHTML) {  // Safety check
                        element.innerHTML = '';
                    }
                    browserViewVisible = false;
                }, 350);  // Slightly longer than animation duration
            });
        } else {
            // Fallback for instant hide if no animation element
            element.innerHTML = '';
            browserViewVisible = false;
        }
        return;
    }
    
    try {
        const response = await fetch('/api/botnet/browsers');
        const result = await response.json();
        
        if (response.ok) {
            // Create HTML with initial hidden state for animation
            let browserHtml = `<div class="browser-info" style="
                border: 1px solid #ddd; 
                border-radius: 8px; 
                padding: 0px 15px; 
                background: #f9f9f9; 
                max-height: 0px; 
                opacity: 0; 
                overflow: hidden;
                transition: all 0.4s ease-in-out;
                margin-bottom: 0px;
            ">`;
            browserHtml += `<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 15px; margin-top: 15px;">
                <h4 style="margin: 0;">🌐 Active Bot Browsers (${result.total_browsers})</h4>
                <button onclick="loadActiveBrowsers()" style="background: #dc3545; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 12px; transition: all 0.2s;">
                    ❌ Hide Browser List
                </button>
            </div>`;
            
            if (result.total_browsers === 0) {
                browserHtml += `<p>No active browsers found.</p>`;
            } else {
                browserHtml += `<table border="1" style="width:100%; border-collapse: collapse; margin-top: 10px;">`;
                browserHtml += `<tr style="background-color: #f0f0f0;">
                    <th>Bot Username</th>
                    <th>Status</th>
                    <th>WebSocket</th>
                    <th>Uptime</th>
                    <th>User Agent</th>
                    <th>Cookies</th>
                    <th>Login Attempts</th>
                    <th>Actions</th>
                </tr>`;
                
                result.browsers.forEach(browser => {
                    const statusIcon = browser.is_logged_in ? '✅' : '❌';
                    const statusText = browser.is_logged_in ? 'Logged In' : 'Not Logged';
                    const userAgentShort = browser.user_agent.substring(0, 50) + '...';
                    
                    // WebSocket information
                    const wsInfo = browser.websocket_info || {};
                    const wsConnected = wsInfo.connected || false;
                    const wsStatus = wsInfo.status || 'No connection';
                    const wsUrl = wsInfo.url || 'No URL';
                    const wsConnectTime = wsInfo.connect_time ? new Date(wsInfo.connect_time * 1000).toLocaleTimeString() : 'Never';
                    const wsLastPing = wsInfo.last_ping ? new Date(wsInfo.last_ping * 1000).toLocaleTimeString() : 'Never';
                    
                    const isPersistent = wsStatus.includes('persistent');
                    const wsIcon = wsConnected ? (isPersistent ? '�' : '�🔗') : '❌';
                    const wsColor = wsConnected ? 'green' : 'red';
                    const wsStatusText = wsConnected ? (isPersistent ? 'Persistent' : 'Connected') : 'Failed';
                    const wsTitle = `Status: ${wsStatus}\nURL: ${wsUrl}\nConnect Time: ${wsConnectTime}\nLast Ping: ${wsLastPing}`;
                    
                    // Timing information
                    const timing = browser.timing || {};
                    const uptimeFormatted = timing.uptime_formatted || 'Unknown';
                    const createdAt = timing.created_at || 'Unknown';
                    const uptimeTitle = `Created: ${createdAt}\nUptime: ${uptimeFormatted}`;
                    
                    browserHtml += `<tr>
                        <td><strong>${browser.username}</strong></td>
                        <td>${statusIcon} ${statusText}</td>
                        <td title="${wsTitle}" style="color: ${wsColor}; cursor: help;">
                            ${wsIcon} ${wsStatusText}
                            <br><small style="font-size: 10px;">${wsStatus}</small>
                        </td>
                        <td title="${uptimeTitle}" style="cursor: help; text-align: center;">
                            ⏱️ ${uptimeFormatted}
                            <br><small style="font-size: 10px;">${createdAt.split(' ')[1] || 'Unknown'}</small>
                        </td>
                        <td title="${browser.user_agent}" style="font-size: 11px;">${userAgentShort}</td>
                        <td>${browser.cookies_count} cookies</td>
                        <td>${browser.login_attempts} attempts</td>
                        <td>
                            <button onclick="viewBrowserDetails('${browser.username}')" 
                                    style="background: #007bff; color: white; border: none; padding: 2px 6px; border-radius: 3px; cursor: pointer; margin-right: 4px; transition: all 0.2s ease;"
                                    onmouseover="this.style.background='#0056b3'; this.style.transform='scale(1.05)'"
                                    onmouseout="this.style.background='#007bff'; this.style.transform='scale(1)'">
                                👁️ View
                            </button>
                            <button onclick="closeBrowser('${browser.username}')" 
                                    style="background: #dc3545; color: white; border: none; padding: 2px 6px; border-radius: 3px; cursor: pointer; transition: all 0.2s ease;"
                                    onmouseover="this.style.background='#c82333'; this.style.transform='scale(1.05)'"
                                    onmouseout="this.style.background='#dc3545'; this.style.transform='scale(1)'">
                                🗑️ Close
                            </button>
                        </td>
                    </tr>`;
                });
                
                browserHtml += `</table>`;
                browserHtml += `<div style="margin-top: 15px; text-align: center; border-top: 1px solid #ddd; padding-top: 10px;">
                    <button onclick="closeAllBrowsers()" 
                            style="background: #dc3545; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; margin-right: 10px; transition: all 0.2s ease; box-shadow: 0 2px 4px rgba(0,0,0,0.1);"
                            onmouseover="this.style.background='#c82333'; this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 8px rgba(0,0,0,0.2)'"
                            onmouseout="this.style.background='#dc3545'; this.style.transform='translateY(0px)'; this.style.boxShadow='0 2px 4px rgba(0,0,0,0.1)'">
                        🗑️ Close All Browsers
                    </button>
                    <button onclick="refreshBrowserViewIfVisible()" 
                            style="background: #28a745; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; transition: all 0.2s ease; box-shadow: 0 2px 4px rgba(0,0,0,0.1);"
                            onmouseover="this.style.background='#218838'; this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 8px rgba(0,0,0,0.2)'"
                            onmouseout="this.style.background='#28a745'; this.style.transform='translateY(0px)'; this.style.boxShadow='0 2px 4px rgba(0,0,0,0.1)'">
                        🔄 Refresh List
                    </button>
                </div>`;
            }
            
            browserHtml += `</div>`;
            
            // Use showContent() to avoid alert wrapper interference
            showContent('botnet-result', browserHtml);
            
            // SIMPLIFIED STABLE ANIMATION - No complex timing issues
            setTimeout(() => {
                const browserInfo = document.querySelector('.browser-info');
                if (browserInfo && browserViewVisible) {  // Safety check
                    // Get natural content height first
                    browserInfo.style.maxHeight = 'none';
                    const contentHeight = browserInfo.scrollHeight;
                    
                    // Reset to collapsed state
                    browserInfo.style.maxHeight = '0px';
                    browserInfo.style.opacity = '0';
                    
                    // Single requestAnimationFrame for clean animation
                    requestAnimationFrame(() => {
                        if (browserInfo && browserViewVisible) {  // Double safety check
                            browserInfo.style.maxHeight = contentHeight + 'px';
                            browserInfo.style.opacity = '1';
                            browserInfo.style.padding = '15px';
                            browserInfo.style.marginBottom = '10px';
                        }
                    });
                    
                    // Final cleanup - set to auto height after animation
                    setTimeout(() => {
                        if (browserInfo && browserViewVisible) {
                            browserInfo.style.maxHeight = 'none';
                        }
                    }, 500);  // Clean timeout after animation
                }
            }, 50);  // Clean initial delay
            
            browserViewVisible = true;
        } else {
            showResult('botnet-result', `❌ Error loading browsers: ${result.detail || 'Unknown error'}`, true);
        }
    } catch (error) {
        showResult('botnet-result', `❌ Error: ${error.message}`, true);
    }
}

// �️ View Browser Details with WebSocket Information
async function viewBrowserDetails(username) {
    try {
        const response = await fetch('/api/botnet/browsers');
        const result = await response.json();
        
        if (response.ok) {
            const browser = result.browsers.find(b => b.username === username);
            if (!browser) {
                showResult('botnet-result', `❌ Browser for ${username} not found`, true);
                return;
            }
            
            // WebSocket information
            const wsInfo = browser.websocket_info || {};
            const wsConnected = wsInfo.connected || false;
            const wsStatus = wsInfo.status || 'No connection';
            const wsUrl = wsInfo.url || 'No URL';
            const wsConnectTime = wsInfo.connect_time ? new Date(wsInfo.connect_time * 1000).toLocaleString() : 'Never';
            const wsLastResponse = wsInfo.last_response || 'No response';
            const wsError = wsInfo.error || 'No error';
            const wsLastPing = wsInfo.last_ping ? new Date(wsInfo.last_ping * 1000).toLocaleString() : 'Never';
            const wsTaskActive = wsInfo.monitoring_task_active || false;
            const isPersistent = wsStatus.includes('persistent') || wsStatus.includes('monitoring');
            
            let detailsHtml = `<div class="browser-details" style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0; border: 1px solid #ddd;">`;
            detailsHtml += `<div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 15px; border-bottom: 2px solid #007bff; padding-bottom: 10px;">
                <h4 style="margin: 0; color: #007bff;">🌐 Browser Details: ${username}</h4>
                <button onclick="loadActiveBrowsers()" style="background: #6c757d; color: white; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-size: 12px;">
                    ← Back to Browser List
                </button>
            </div>`;
            
            // Browser timing information
            const timing = browser.timing || {};
            const uptimeFormatted = timing.uptime_formatted || 'Unknown';
            const createdAt = timing.created_at || 'Unknown';
            const uptimeSeconds = timing.uptime_seconds || 0;
            
            // Basic Info
            detailsHtml += `<div style="margin-bottom: 15px;">
                <h5>📊 Basic Information</h5>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr><td><strong>Username:</strong></td><td>${browser.username}</td></tr>
                    <tr><td><strong>Login Status:</strong></td><td>${browser.is_logged_in ? '✅ Logged In' : '❌ Not Logged'}</td></tr>
                    <tr><td><strong>Cookies:</strong></td><td>${browser.cookies_count} active cookies</td></tr>
                    <tr><td><strong>Login Attempts:</strong></td><td>${browser.login_attempts}</td></tr>
                    <tr><td><strong>Last Login:</strong></td><td>${browser.last_login ? new Date(browser.last_login * 1000).toLocaleString() : 'Never'}</td></tr>
                    <tr><td><strong>User Agent:</strong></td><td style="font-size: 12px; word-break: break-all;">${browser.user_agent}</td></tr>
                </table>
            </div>`;
            
            // Timing Information
            detailsHtml += `<div style="margin-bottom: 15px;">
                <h5>⏱️ Browser Timing Information</h5>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr><td><strong>Created At:</strong></td><td>${createdAt}</td></tr>
                    <tr><td><strong>Uptime:</strong></td><td>${uptimeFormatted} (${Math.round(uptimeSeconds)}s total)</td></tr>
                    <tr><td><strong>Session Duration:</strong></td><td>${uptimeFormatted}</td></tr>
                </table>
            </div>`;
            
            // WebSocket Info
            detailsHtml += `<div style="margin-bottom: 15px;">
                <h5>🔗 WebSocket Information ${isPersistent ? '(Persistent Connection)' : ''}</h5>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr><td><strong>Connection Status:</strong></td><td style="color: ${wsConnected ? 'green' : 'red'};">${wsConnected ? (isPersistent ? '🔄 Persistent Connected' : '✅ Connected') : '❌ Disconnected'}</td></tr>
                    <tr><td><strong>Connection Type:</strong></td><td style="color: ${isPersistent ? 'blue' : 'orange'};">${isPersistent ? '🔄 Persistent (Background Monitoring)' : '⚡ Standard'}</td></tr>
                    <tr><td><strong>Status:</strong></td><td>${wsStatus}</td></tr>
                    <tr><td><strong>Monitoring Task:</strong></td><td style="color: ${wsTaskActive ? 'green' : 'red'};">${wsTaskActive ? '✅ Active' : '❌ Inactive'}</td></tr>
                    <tr><td><strong>WebSocket URL:</strong></td><td style="font-size: 11px; word-break: break-all;">${wsUrl}</td></tr>
                    <tr><td><strong>Connect Time:</strong></td><td>${wsConnectTime}</td></tr>
                    <tr><td><strong>Last Ping:</strong></td><td>${wsLastPing}</td></tr>
                    <tr><td><strong>Last Response:</strong></td><td style="font-size: 11px; max-width: 300px; word-break: break-all;">${typeof wsLastResponse === 'object' ? JSON.stringify(wsLastResponse) : wsLastResponse}</td></tr>
                    ${wsError && wsError !== 'No error' ? `<tr><td><strong>Error:</strong></td><td style="color: red; font-size: 11px;">${wsError}</td></tr>` : ''}
                </table>
            </div>`;
            
            detailsHtml += `<div style="text-align: center; margin-top: 15px; border-top: 1px solid #ddd; padding-top: 15px;">
                <button onclick="closeBrowser('${username}')" 
                        style="background: #dc3545; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; margin-right: 10px;">
                    🗑️ Close This Browser
                </button>
                <button onclick="loadActiveBrowsers()" 
                        style="background: #007bff; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer;">
                    ← Return to Browser List
                </button>
            </div>`;
            
            detailsHtml += `</div>`;
            
            // Use showContent() to avoid alert wrapper interference
            showContent('botnet-result', detailsHtml);
            browserViewVisible = true; // Keep browser view state
        } else {
            showResult('botnet-result', `❌ Error loading browser details: ${result.detail || 'Unknown error'}`, true);
        }
    } catch (error) {
        showResult('botnet-result', `❌ Error: ${error.message}`, true);
    }
}

// �🗑️ Close Specific Browser
async function closeBrowser(username) {
    try {
        const response = await fetch(`/api/botnet/browsers/${username}`, {
            method: 'DELETE'
        });
        const result = await response.json();
        
        if (response.ok) {
            showResult('botnet-result', `✅ Browser for ${username} closed successfully! Remaining: ${result.remaining_browsers}`);
            // Reload browser list immediately if currently visible
            setTimeout(refreshBrowserViewIfVisible, 1000);
        } else {
            showResult('botnet-result', `❌ Error closing browser: ${result.detail || 'Unknown error'}`, true);
        }
    } catch (error) {
        showResult('botnet-result', `❌ Error: ${error.message}`, true);
    }
}

// 🗑️ Close All Browsers
async function closeAllBrowsers() {
    const confirm = window.confirm('⚠️ Are you sure you want to close all active browser sessions?');
    if (!confirm) return;
    
    try {
        const response = await fetch('/api/botnet/browsers', {
            method: 'DELETE'
        });
        const result = await response.json();
        
        if (response.ok) {
            showResult('botnet-result', `✅ All browsers closed successfully!`);
            browserViewVisible = false; // Reset browser view state
        } else {
            showResult('botnet-result', `❌ Error closing browsers: ${result.detail || 'Unknown error'}`, true);
        }
    } catch (error) {
        showResult('botnet-result', `❌ Error: ${error.message}`, true);
    }
}

function loadUsers() {
    // Placeholder function - implement if needed
    console.log('Loading users...');
}

// Load users on page load and initialize Bot Crawl tab
window.onload = () => {
    loadUsers();
    // Ensure Bot Crawl tab is active and content is visible on page load
    const botnetTab = document.querySelector('button[onclick*="botnet"]');
    const botnetContent = document.getElementById('botnet');
    if (botnetTab && botnetContent) {
        botnetTab.classList.add('active');
        botnetContent.classList.add('active');
    }
};
