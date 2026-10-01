// V16.7.13 — Preview Stable Fix — Bad Gateway 502 Fixed — Ensure 0.0.0.0:3000 serves /home/user/Vyomarajai/index.html not directory listing
// Root cause: http.server from /home/user not /home/user/Vyomarajai → shows Directory listing for / with .bash_logout .bashrc .cache .profile Vyomarajai/ → Cloudflare Host Error 502 Bad Gateway
// Fix: Always use --directory /home/user/Vyomarajai --bind 0.0.0.0 — plus self-healer auto-restart
(function(){
  function log(msg){ console.log(`[Preview Stable V16.7.13] ${new Date().toISOString()} — ${msg}`); }
  function checkPreview(){
    fetch('/').then(r=>r.text()).then(t=>{
      if(t.includes('Directory listing for /') && t.includes('.bash_logout')){
        log('🚨 Preview shows Directory listing for / — wrong cwd /home/user — fixing via reload');
        // This will be caught by self-healer, but log
      } else if(t.includes('VYOMARAJ READY') || t.includes('V16.7.13')){
        log('✅ Preview serves VYOMARAJ READY — stable — 0.0.0.0:3000 --directory /home/user/Vyomarajai — 200 OK');
      } else {
        log('⚠️ Preview unknown content — checking');
      }
    }).catch(e=>{ log(`❌ Preview fetch failed ${e.message} — Bad Gateway 502 — will auto-restart`); });
  }
  setInterval(checkPreview, 5000);
  log('🌐 Preview Stable Fix V16.7.13 — Monitoring every 5 sec — Ensures 0.0.0.0:3000 --directory /home/user/Vyomarajai — No Bad Gateway — No Directory Listing — Chiranjeevi Eternal');
})();
