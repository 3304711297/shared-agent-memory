param(
    [string]$RawUrl
)

if (-not $RawUrl) {
    exit
}

# 1. 清理协议头与引号
$cleanUrl = $RawUrl.Trim('"', "'")
if ($cleanUrl -match '(?i)^screenbox:/*(.*)$') {
    $cleanUrl = $matches[1]
}

# 2. URL 解码（如果被浏览器转义过）
try {
    $cleanUrl = [System.Uri]::UnescapeDataString($cleanUrl)
} catch {
}

# 3. 复制到系统剪贴板
try {
    Set-Clipboard -Value $cleanUrl
} catch {
}

# 4. 唤醒/启动 Screenbox (UWP)
try {
    Start-Process "shell:appsFolder\18496Starpine.Screenbox_rm8wvch11q4my!App"
} catch {
}

# 5. 弹出轻量 Windows 系统通知
try {
    [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
    $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
    $textNodes = $template.GetElementsByTagName("text")
    $textNodes.Item(0).AppendChild($template.CreateTextNode("🎬 猫抓 · Screenbox 调用成功")) > $null
    $textNodes.Item(1).AppendChild($template.CreateTextNode("视频直链已复制到剪贴板！Screenbox 已唤起。")) > $null
    $toast = [Windows.UI.Notifications.ToastNotification]::new($template)
    [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Screenbox").Show($toast)
} catch {
}
