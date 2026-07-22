// functions/index.js
// Cloudflare edge function - captures URL params and triggers the bot

export async function onRequest(context) {
  // 1. Get the keyword and user ID from the URL
  const { request, url, waitUntil } = context;
  const searchParams = new URL(url).searchParams;
  
  const keyword = searchParams.get('keyword') || 'mediatakeout';
  const userId = searchParams.get('uid') || 'anonymous';

  // 2. TEMPORARY: Webhook for testing (replace with Cloud Run URL in Phase 3)
  const BOT_ENDPOINT = 'https://webhook.site/your-unique-id';
  // 👆 Go to webhook.site, copy your URL, and paste it here

  // 3. Trigger the bot in the background (user doesn't wait)
  waitUntil(
    fetch(BOT_ENDPOINT, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        action: 'search',
        userId: userId,
        keyword: keyword,
        timestamp: Date.now()
      })
    }).catch(err => console.error('Bot trigger failed:', err))
  );

  // 4. Final destination (will be replaced by bot response later)
  const finalUrl = `https://example.com/?q=${encodeURIComponent(keyword)}`;

  // 5. HTML loading page (shows for 2 seconds, then redirects)
  const html = `<!DOCTYPE html>
  <html>
  <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Loading...</title>
    <style>
      body {
        margin: 0;
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        font-family: Arial, sans-serif;
        background: #f8f9fa;
      }
      .container {
        text-align: center;
        background: white;
        padding: 2rem;
        border-radius: 16px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
      }
      .spinner {
        width: 40px;
        height: 40px;
        border: 4px solid #e9ecef;
        border-top: 4px solid #4263eb;
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
        margin: 1rem auto;
      }
      @keyframes spin { 100% { transform: rotate(360deg); } }
    </style>
    <script>
      setTimeout(() => {
        window.location.href = "${finalUrl}";
      }, 2000);
    </script>
  </head>
  <body>
    <div class="container">
      <div class="spinner"></div>
      <h3>Loading...</h3>
      <p style="color: #888;">Searching for: <strong>${keyword}</strong></p>
    </div>
  </body>
  </html>`;

  return new Response(html, {
    headers: { 'Content-Type': 'text/html' }
  });
}
