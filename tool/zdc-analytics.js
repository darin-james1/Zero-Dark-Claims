/**
 * Zero Dark Claims — zdc-analytics.js
 *
 * PostHog event tracking for the ZDC letter builder tool.
 * Injected the same way as zdc-letter-prefill.js — no React source needed.
 *
 * EVENTS TRACKED:
 *   app_loaded           — tool first opens (once per session)
 *   letter_type_selected — veteran clicks "Start Letter" on a card
 *   letter_generated     — veteran clicks the generate/create button
 *   pdf_downloaded       — veteran clicks a download/export button
 *   form_step_advanced   — veteran moves to the next step in a form
 *
 * SETUP:
 *   1. Add PostHog snippet to tool/index.html (see instructions below)
 *   2. Drop this file into your repo at tool/zdc-analytics.js
 *   3. Add <script src="./zdc-analytics.js" defer></script> to tool/index.html body
 *   4. Replace YOUR_POSTHOG_KEY in index.html with your actual key from posthog.com
 *
 * NOTE: PostHog project API keys are public by design (write-only / capture-only).
 * It is safe to include them directly in frontend HTML — the same as a GA4 tag.
 */

(function () {
  'use strict';

  // ── TRACK HELPER ─────────────────────────────────────────────────────

  function track(event, props) {
    if (window.posthog && typeof window.posthog.capture === 'function') {
      window.posthog.capture(event, props || {});
    }
  }

  // ── APP LOADED (once per session) ────────────────────────────────────

  track('app_loaded');


  // ── CLICK DELEGATION ─────────────────────────────────────────────────
  // One listener on the document catches all button clicks.
  // This works even after React re-renders the DOM.

  document.addEventListener('click', function (e) {
    const btn = e.target.closest('button, [role="button"], a');
    if (!btn) return;

    const btnText = btn.textContent.trim();
    const btnTextLower = btnText.toLowerCase();

    // ── 1. Letter type selected — "Start Letter →" cards ──────────────
    if (btnTextLower.includes('start letter')) {
      // Walk up to the card container and grab its heading
      const card = btn.closest('[class*="rounded"]') ||
                   btn.closest('[class*="border"]') ||
                   btn.parentElement?.parentElement;

      let letterType = 'unknown';
      if (card) {
        const heading = card.querySelector('h2, h3, [class*="font-bold"], [class*="font-semibold"], strong');
        if (heading) letterType = heading.textContent.trim();
      }

      track('letter_type_selected', { letter_type: letterType });
    }

    // ── 2. Letter generated — "Generate", "Create Letter", "Build" ─────
    else if (
      btnTextLower.includes('generate') ||
      btnTextLower.includes('create letter') ||
      btnTextLower.includes('build letter') ||
      btnTextLower.includes('create my letter') ||
      btnTextLower.includes('finalize')
    ) {
      track('letter_generated', { button_text: btnText });
    }

    // ── 3. PDF downloaded — "Download", "Save", "Export" ───────────────
    else if (
      btnTextLower.includes('download') ||
      btnTextLower.includes('save pdf') ||
      btnTextLower.includes('export') ||
      btnTextLower.includes('save letter')
    ) {
      track('pdf_downloaded', { button_text: btnText });
    }

    // ── 4. Form step advanced — "Next", "Continue", "Next Step" ────────
    else if (
      btnTextLower === 'next' ||
      btnTextLower === 'continue' ||
      btnTextLower.includes('next step') ||
      btnTextLower.includes('next section')
    ) {
      // Try to capture the current step number from the DOM
      const stepIndicator = document.querySelector(
        '[class*="step"], [class*="Step"], [aria-label*="step"], [aria-label*="Step"]'
      );
      const stepText = stepIndicator ? stepIndicator.textContent.trim() : null;

      track('form_step_advanced', { step_label: stepText });
    }
  }, true); // useCapture: true so we catch clicks before React can prevent them


  // ── URL CHANGE TRACKING (SPA navigation) ─────────────────────────────
  // React Router changes the URL without a page reload.
  // We listen for pushState and popstate to catch route changes.

  function onRouteChange() {
    track('page_viewed', { path: window.location.pathname + window.location.hash });
  }

  // Patch pushState to detect programmatic navigation
  const originalPushState = history.pushState.bind(history);
  history.pushState = function (...args) {
    originalPushState(...args);
    onRouteChange();
  };

  window.addEventListener('popstate', onRouteChange);
  window.addEventListener('hashchange', onRouteChange);


  console.log('[ZDC Analytics] Ready');

})();
