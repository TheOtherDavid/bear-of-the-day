(() => {
  const localHosts = new Set(['localhost', '127.0.0.1', '[::1]']);
  const defaultUrl = localHosts.has(window.location.hostname)
    ? 'http://localhost:4173/nav.js'
    : 'https://handcraftedai.com/nav.js';
  const navUrl = window.PORTFOLIO_NAV_URL || defaultUrl;

  const script = document.createElement('script');
  script.src = navUrl;
  script.defer = true;
  script.addEventListener('error', () => {
    console.warn(`Portfolio navigation could not be loaded from ${navUrl}`);
  });
  document.head.appendChild(script);
})();
