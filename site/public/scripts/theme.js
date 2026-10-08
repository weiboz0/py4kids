// The light/dark theme (plan 103). Loaded as an external, render-blocking file in <head> so the
// chosen theme applies before first paint (no inline script: the CSP's script-src is 'self').
// The default follows prefers-color-scheme; only an explicit choice is stored, and only the
// theme choice is ever stored. Storage may be unavailable (private window): then the choice
// lasts for the page only.
(function () {
  var KEY = 'py4kids-theme';
  var root = document.documentElement;

  function stored() {
    try {
      var value = window.localStorage.getItem(KEY);
      return value === 'light' || value === 'dark' ? value : null;
    } catch (e) {
      return null;
    }
  }

  function effective() {
    var chosen = root.getAttribute('data-theme');
    if (chosen === 'light' || chosen === 'dark') return chosen;
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  var initial = stored();
  if (initial) root.setAttribute('data-theme', initial);

  function sync(button) {
    var dark = effective() === 'dark';
    button.setAttribute('aria-pressed', dark ? 'true' : 'false');
    button.setAttribute('aria-label', dark ? 'Dark theme on; switch to light' : 'Dark theme off; switch to dark');
  }

  document.addEventListener('DOMContentLoaded', function () {
    var button = document.getElementById('theme-toggle');
    if (!button) return;
    button.hidden = false;
    sync(button);
    button.addEventListener('click', function () {
      var next = effective() === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try {
        window.localStorage.setItem(KEY, next);
      } catch (e) {
        // Storage unavailable: keep the choice for this page only.
      }
      sync(button);
    });
    if (window.matchMedia) {
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function () {
        sync(button);
      });
    }
  });
})();
