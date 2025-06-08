$body = @{
    user_id = 111111111
    message = "👋 Don't forget to track your habits!"
} | ConvertTo-Json -Depth 3

$bytes = [System.Text.Encoding]::UTF8.GetBytes($body)
$stream = New-Object System.IO.MemoryStream(,$bytes)

Invoke-RestMethod -Uri "http://localhost:8080/notify" `
  -Method POST `
  -ContentType "application/json" `
  -Body $stream
