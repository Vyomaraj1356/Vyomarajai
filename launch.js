(() => {
  const installButton = document.getElementById('installButton');
  const installStatus = document.getElementById('installStatus');
  let deferredInstall = null;

  window.addEventListener('beforeinstallprompt', (event) => {
    event.preventDefault();
    deferredInstall = event;
    if (installButton) installButton.hidden = false;
    if (installStatus) installStatus.textContent = 'This browser can install the Vyomaraj web preview. The installed app contains only the public landing page.';
  });

  installButton?.addEventListener('click', async () => {
    if (!deferredInstall) {
      if (installStatus) installStatus.textContent = 'To install, use your browser menu and choose “Install app” or “Add to Home Screen”.';
      return;
    }
    deferredInstall.prompt();
    const result = await deferredInstall.userChoice;
    deferredInstall = null;
    installButton.hidden = true;
    if (installStatus) installStatus.textContent = result?.outcome === 'accepted'
      ? 'The public web preview was installed. It does not include native Android/macOS features or a live private control plane.'
      : 'Installation was dismissed. You can continue using the preview in your browser.';
  });

  window.addEventListener('appinstalled', () => {
    if (installButton) installButton.hidden = true;
    if (installStatus) installStatus.textContent = 'The public web preview is installed on this device.';
  });

  if ('serviceWorker' in navigator && (location.protocol === 'https:' || location.hostname === 'localhost')) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('./sw.js', { scope: './' }).catch(() => {
        if (installStatus) installStatus.textContent = 'Online preview is available. Offline caching could not be enabled in this browser.';
      });
    });
  }
})();
