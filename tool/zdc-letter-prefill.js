/**
 * Zero Dark Claims — zdc-letter-prefill.js
 *
 * Injects a drag-and-drop "Upload Previous Letter" zone at the top of each
 * letter builder step form. When a veteran drops a .txt, .pdf, or .docx file,
 * the script parses the text and attempts to auto-fill the form fields by
 * matching content against known field labels.
 *
 * WHY THIS EXISTS:
 * Veterans shouldn't have to re-type everything when they want a refined letter.
 * They can take a previously generated letter (or a pre-filled VA form they
 * started on their own), drop it in, and the tool pre-fills matching fields.
 *
 * PRIVACY:
 * - File is read LOCAL ONLY (FileReader API — never uploaded anywhere)
 * - Text lives in browser memory only during the session
 * - Nothing is transmitted, stored, or logged
 *
 * INTEGRATION:
 * Add this script tag to tool.zerodarkclaims.com's index.html:
 *   <script src="/zdc-letter-prefill.js" defer></script>
 *
 * OR if the tool HTML can't be modified, load it from the main domain:
 *   <script src="https://www.zerodarkclaims.com/zdc-letter-prefill.js" defer></script>
 */

(function () {
  'use strict';

  // ── CONFIGURATION ────────────────────────────────────────────────────

  // Known field labels from the compiled React tool (case-insensitive match)
  // These are the exact label strings used in the tool's step forms.
  const FIELD_LABELS = [
    'Full Name',
    "Veteran's Full Name",
    'Branch of Service',
    'Dates of Service',
    'Date of Birth',
    'Last 4 of SSN / VA File Number',
    "Veteran's Last 4 SSN / VA File Number",
    'Claimed Condition(s)',
    'Condition This Statement Supports',
    'Condition(s) / Issue(s) Being Appealed',
    'In-Service Event / Stressor / Exposure',
    'In-Service Event or Injury',
    'Current PTSD / Mental Health Symptoms',
    'Describe the Traumatic Event(s)',
    'Type of Stressor',
    'Unit / Ship / Installation at Time of Event',
    'Approximate Date(s) / Location',
    'Daily Activity Limitations',
    'Impact on Employment',
    'Impact on Work and Social Life',
    'Impact on Relationships / Social Life',
    'Treatment History',
    'Treatment Received',
    'When Did Symptoms First Begin?',
    'Have Symptoms Been Continuous Since Service?',
    'Frequency and Severity',
    'Before vs. After Comparison (if applicable)',
    'Current Rating & Effective Date',
    'Current Rating for Primary Condition',
    'Current Combined Disability Rating',
    'How Has Your Condition Worsened?',
    'When Did You Notice the Worsening?',
    'New or Increased Functional Limitations',
    'Treatment Changes / Increased Medical Care',
    'Service-Connected Condition',
    'Service-Connected Condition Seeking Increase For',
    'Primary Service-Connected Condition',
    'Secondary (New) Condition Being Claimed',
    'How Does the Primary Condition Cause the Secondary?',
    'Secondary Condition Symptoms',
    'Treatment for Secondary Condition',
    'Functional Impact of Secondary Condition',
    'Diagnosed Condition (ICD-10 if available)',
    'Nexus Opinion (At Least As Likely As Not)',
    'Supporting Medical Literature (Optional)',
    'Records Reviewed',
    'Provider Full Name & Credentials',
    'Facility / Practice Name',
    'Provider Address',
    'Provider Phone / Contact',
    'Service-Connected Disability(ies) Causing Unemployability',
    'Employment History (Last 5 Years)',
    'Education and Occupational Training',
    "Why Can't You Maintain Substantially Gainful Employment?",
    'When Were You Last Substantially Gainfully Employed?',
    'Any Marginal / Occasional Work Attempted?',
    'Witness Full Name',
    'Relationship to Veteran',
    'How Long Have You Known the Veteran?',
    'Symptoms / Changes You Have Observed',
    'What Did You Witness During Service? (if applicable)',
    'How Does the Condition Affect Their Daily Life?',
    'Contact Information (Optional)',
    'Errors in the VA\'s Decision',
    'Date of VA Rating Decision',
    'VA Regional Office That Issued the Decision',
    'What Outcome Are You Seeking?',
    'Evidence / Documents You Are Submitting',
    'Evidence Being Submitted',
    'New & Relevant Evidence (for Supplemental Claims)',
    'Appeal Lane / Type',
    'What Specific Error Was Made?',
    'What Was the Prior Decision?',
    'What Would the Correct Decision Have Been?',
    'Date of Prior Final VA Decision Containing CUE',
    'Which Disability / Issue Contains the CUE?',
    'Evidence Supporting the CUE',
    'Applicable Regulation / Law That Was Misapplied',
    'Earlier Effective Date Being Sought',
    'Current Effective Date Assigned by VA',
    'Legal Basis for Earlier Effective Date',
    'Facts Supporting the Earlier Effective Date',
    'Caregiver Full Name',
    "Caregiver's Relationship to Veteran",
    'Service-Connected Conditions Requiring Care',
    'Service-Connected Conditions Causing This Need',
    'Daily Activities Requiring Assistance',
    'Activities of Daily Living (ADLs) Requiring Assistance',
    'Hours of Care Provided Per Day / Week',
    'Safety Risks Without Caregiver',
    'Housebound Details (if claiming housebound)',
    'Who Provides Your Care?',
    'Possible Corroborating Evidence',
    'Why Do You Believe a Higher Rating Is Warranted?',
    'Anything Else You Want the VA to Know',
    'Anything Else You Want to Add',
    'Describe Your Need for Daily Assistance or Housebound Status',
    'Type of Claim',
    'Explain How This Condition Affects Your Daily Life, Work, and Relationships TODAY',
  ];

  // ── DROP ZONE STYLES ─────────────────────────────────────────────────

  const DROPZONE_CSS = `
    .zdc-prefill-zone {
      position: relative;
      border: 2px dashed rgba(0, 224, 255, 0.25);
      border-radius: 14px;
      padding: 1.25rem 1.5rem;
      margin-bottom: 1.5rem;
      background: rgba(0, 224, 255, 0.03);
      cursor: pointer;
      transition: all 0.25s ease;
      text-align: center;
    }
    .zdc-prefill-zone:hover,
    .zdc-prefill-zone.dragover {
      border-color: rgba(0, 224, 255, 0.55);
      background: rgba(0, 224, 255, 0.07);
    }
    .zdc-prefill-zone.dragover {
      transform: scale(1.01);
    }
    .zdc-prefill-zone.filled {
      border-color: rgba(34, 197, 94, 0.4);
      background: rgba(34, 197, 94, 0.04);
    }
    .zdc-prefill-zone .zdc-pf-icon {
      font-size: 1.5rem;
      margin-bottom: 0.35rem;
    }
    .zdc-prefill-zone .zdc-pf-title {
      font-size: 0.85rem;
      font-weight: 600;
      color: inherit;
      margin-bottom: 0.2rem;
    }
    .zdc-prefill-zone .zdc-pf-sub {
      font-size: 0.72rem;
      opacity: 0.6;
    }
    .zdc-prefill-zone input[type="file"] {
      position: absolute;
      inset: 0;
      opacity: 0;
      cursor: pointer;
    }
    .zdc-pf-status {
      margin-top: 0.75rem;
      padding: 0.65rem 1rem;
      border-radius: 10px;
      font-size: 0.78rem;
      line-height: 1.5;
      display: none;
    }
    .zdc-pf-status.visible { display: block; }
    .zdc-pf-status.success {
      background: rgba(34, 197, 94, 0.08);
      border: 1px solid rgba(34, 197, 94, 0.2);
      color: #4ade80;
    }
    .zdc-pf-status.warning {
      background: rgba(245, 158, 11, 0.08);
      border: 1px solid rgba(245, 158, 11, 0.2);
      color: #fbbf24;
    }
    .zdc-pf-status.error {
      background: rgba(239, 68, 68, 0.08);
      border: 1px solid rgba(239, 68, 68, 0.2);
      color: #f87171;
    }
    .zdc-pf-privacy {
      font-size: 0.65rem;
      opacity: 0.45;
      margin-top: 0.5rem;
    }
  `;

  // ── INJECT STYLES ────────────────────────────────────────────────────

  function injectStyles() {
    if (document.getElementById('zdc-prefill-styles')) return;
    const style = document.createElement('style');
    style.id = 'zdc-prefill-styles';
    style.textContent = DROPZONE_CSS;
    document.head.appendChild(style);
  }

  // ── CREATE DROP ZONE ELEMENT ─────────────────────────────────────────

  function createDropZone() {
    const zone = document.createElement('div');
    zone.className = 'zdc-prefill-zone';
    zone.innerHTML = `
      <div class="zdc-pf-icon">📄</div>
      <div class="zdc-pf-title">Drop a previously generated letter or your pre-filled VA form</div>
      <div class="zdc-pf-sub">Supports .txt, .pdf — auto-fills matching fields below</div>
      <input type="file" accept=".txt,.pdf,.text,text/plain,application/pdf" />
      <div class="zdc-pf-status" id="zdcPrefillStatus"></div>
      <div class="zdc-pf-privacy">🔒 File is read locally in your browser — never uploaded or stored anywhere</div>
    `;

    const fileInput = zone.querySelector('input[type="file"]');

    // Drag events
    zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('dragover'); });
    zone.addEventListener('dragleave', () => { zone.classList.remove('dragover'); });
    zone.addEventListener('drop', e => {
      e.preventDefault();
      zone.classList.remove('dragover');
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file, zone);
    });

    // Click upload
    fileInput.addEventListener('change', e => {
      const file = e.target.files[0];
      if (file) handleFile(file, zone);
    });

    return zone;
  }

  // ── FILE HANDLING ────────────────────────────────────────────────────

  async function handleFile(file, zone) {
    const statusEl = zone.querySelector('.zdc-pf-status');

    // Show processing state
    statusEl.textContent = 'Reading file...';
    statusEl.className = 'zdc-pf-status visible warning';

    let text = '';

    try {
      if (file.type === 'application/pdf' || file.name.endsWith('.pdf')) {
        text = await readPDF(file);
      } else {
        text = await readTextFile(file);
      }
    } catch (err) {
      statusEl.textContent = 'Could not read this file. Try a .txt or .pdf file.';
      statusEl.className = 'zdc-pf-status visible error';
      return;
    }

    if (!text || text.trim().length < 20) {
      statusEl.textContent = 'File appears empty or too short. Make sure it contains letter text.';
      statusEl.className = 'zdc-pf-status visible error';
      return;
    }

    // Parse and fill fields
    const filled = fillFormFields(text);

    if (filled > 0) {
      zone.classList.add('filled');
      zone.querySelector('.zdc-pf-icon').textContent = '✅';
      zone.querySelector('.zdc-pf-title').textContent = `Auto-filled ${filled} field${filled > 1 ? 's' : ''}`;
      zone.querySelector('.zdc-pf-sub').textContent = 'Review each field below and make any corrections needed.';
      statusEl.textContent = `✓ ${filled} field${filled > 1 ? 's' : ''} pre-filled from "${file.name}". Scroll down to review.`;
      statusEl.className = 'zdc-pf-status visible success';
    } else {
      statusEl.textContent = 'Could not match any fields. Try a different letter or manually enter your information below.';
      statusEl.className = 'zdc-pf-status visible warning';
    }
  }

  function readTextFile(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsText(file);
    });
  }

  async function readPDF(file) {
    // Load pdf.js from CDN if not already present
    if (!window.pdfjsLib) {
      await loadScript('https://cdnjs.cloudflare.com/ajax/libs/pdf.js/4.4.168/pdf.min.mjs', true);
      // The ESM build sets pdfjsLib on window
      if (!window.pdfjsLib && window['pdfjs-dist/build/pdf']) {
        window.pdfjsLib = window['pdfjs-dist/build/pdf'];
      }
    }

    // Fallback: try loading the UMD version if ESM didn't work
    if (!window.pdfjsLib) {
      await loadScript('https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js', false);
    }

    if (!window.pdfjsLib) {
      throw new Error('PDF.js could not be loaded');
    }

    window.pdfjsLib.GlobalWorkerOptions.workerSrc =
      'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

    const arrayBuffer = await file.arrayBuffer();
    const pdf = await window.pdfjsLib.getDocument({ data: arrayBuffer }).promise;
    let fullText = '';

    for (let i = 1; i <= pdf.numPages; i++) {
      const page = await pdf.getPage(i);
      const content = await page.getTextContent();
      const pageText = content.items.map(item => item.str).join(' ');
      fullText += pageText + '\n';
    }

    return fullText;
  }

  function loadScript(src, isModule) {
    return new Promise((resolve) => {
      const script = document.createElement('script');
      script.src = src;
      if (isModule) script.type = 'module';
      script.onload = resolve;
      script.onerror = resolve; // Don't fail hard — we'll try fallback
      document.head.appendChild(script);
    });
  }

  // ── FIELD MATCHING + FILLING ─────────────────────────────────────────

  /**
   * Smart field matching: parses the letter text and tries to extract
   * values for each visible form field on the current step.
   *
   * Strategy:
   *  1. Find all visible <textarea> and <input> elements in the form
   *  2. For each, find the closest label text
   *  3. Search the letter text for content that matches that label
   *  4. Use React's native input value setter to fill the field
   *     (required because React ignores direct .value assignments)
   */
  function fillFormFields(letterText) {
    let filledCount = 0;

    // Normalize letter text for searching
    const normalizedText = letterText.replace(/\r\n/g, '\n').trim();

    // Find all textareas and text inputs currently visible in the form
    const fields = document.querySelectorAll('textarea, input[type="text"], input[type="date"]');

    fields.forEach(field => {
      // Skip hidden fields, file inputs, search bars
      if (field.offsetParent === null) return;
      if (field.closest('.zdc-prefill-zone')) return;
      if (field.type === 'file' || field.type === 'hidden') return;

      // Find the label for this field
      const labelText = findLabelForField(field);
      if (!labelText) return;

      // Try to extract matching content from the letter
      const extracted = extractValueForLabel(labelText, normalizedText);
      if (!extracted) return;

      // Fill the field using React's native input setter
      setReactValue(field, extracted);
      filledCount++;
    });

    return filledCount;
  }

  /**
   * Find the label text associated with a form field.
   * Looks for: <label> elements, preceding text, aria-label, placeholder
   */
  function findLabelForField(field) {
    // Check for explicit label via for/id
    if (field.id) {
      const label = document.querySelector(`label[for="${field.id}"]`);
      if (label) return label.textContent.trim();
    }

    // Check parent container for label element
    const container = field.closest('.flex.flex-col.gap-1\\.5') ||
                      field.closest('.space-y-2') ||
                      field.closest('.grid.gap-1') ||
                      field.parentElement;
    if (container) {
      const label = container.querySelector('label');
      if (label) return label.textContent.trim();
    }

    // Check aria-label
    if (field.getAttribute('aria-label')) return field.getAttribute('aria-label');

    // Fall back to placeholder (less reliable)
    if (field.placeholder && field.placeholder.length < 100) return field.placeholder;

    return null;
  }

  /**
   * Extract a value from the letter text that matches a given field label.
   *
   * Uses multiple strategies:
   *  1. Exact section headers (e.g., "Full Name: John Smith")
   *  2. Common letter patterns (e.g., "My name is John Smith")
   *  3. Structured VA form patterns
   */
  function extractValueForLabel(label, text) {
    const labelLower = label.toLowerCase().replace(/[*:?]/g, '').trim();

    // ── STRATEGY 1: Look for "Label: value" or "Label - value" patterns ──
    // Build a regex that finds the label followed by a colon/dash and captures the value
    const escapedLabel = labelLower.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const colonPattern = new RegExp(
      escapedLabel + '\\s*[:—–-]\\s*(.+?)(?:\\n|$)',
      'im'
    );
    const colonMatch = text.match(colonPattern);
    if (colonMatch && colonMatch[1]) {
      const val = colonMatch[1].trim();
      if (val.length > 1 && val.length < 2000) return val;
    }

    // ── STRATEGY 2: Common natural language patterns ──
    const patterns = {
      'full name': [
        /(?:my name is|i,?\s+)\s*([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)/i,
        /(?:veteran|claimant|declarant)[:,]?\s+([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)/i,
      ],
      "veteran's full name": [
        /(?:veteran|service\s*member)[:,]?\s+([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)/i,
      ],
      'branch of service': [
        /(?:served in|branch[:\s]+)\s*((?:U\.?S\.?\s+)?(?:Army|Navy|Marine Corps|Marines|Air Force|Coast Guard|Space Force|National Guard))/i,
        /(Army|Navy|Marine Corps|Marines|Air Force|Coast Guard|Space Force)\s+(?:from|veteran|service)/i,
      ],
      'dates of service': [
        /(?:served?|service[:\s]+|active duty)\s*(?:from)?\s*(\d{1,2}\/\d{1,4}(?:\s*[-–to]+\s*\d{1,2}\/\d{1,4})?)/i,
        /(\d{4}\s*[-–to]+\s*\d{4})/,
      ],
      'date of birth': [
        /(?:date of birth|DOB|born)[:\s]+\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})/i,
      ],
      'last 4 of ssn': [
        /(?:SSN|last\s*4|VA\s*file)[:\s#]+\s*(\d{4})/i,
        /xxx-xx-(\d{4})/i,
      ],
    };

    // Check if any pattern group matches the label
    for (const [key, regexes] of Object.entries(patterns)) {
      if (labelLower.includes(key)) {
        for (const regex of regexes) {
          const match = text.match(regex);
          if (match && match[1]) return match[1].trim();
        }
      }
    }

    // ── STRATEGY 3: Section-based extraction for longer fields ──
    // For textareas (multi-line fields), look for a section with a matching header
    // and capture everything until the next section header
    const sectionPattern = new RegExp(
      '(?:^|\\n)\\s*(?:\\d+\\.\\s*)?(?:' + escapedLabel + ')\\s*[:—–\\n]\\s*([\\s\\S]+?)(?=\\n\\s*(?:\\d+\\.\\s*)?(?:' +
      FIELD_LABELS.map(l => l.toLowerCase().replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|') +
      ')\\s*[:—–\\n]|$)',
      'im'
    );
    const sectionMatch = text.match(sectionPattern);
    if (sectionMatch && sectionMatch[1]) {
      const val = sectionMatch[1].trim();
      if (val.length > 2 && val.length < 5000) return val;
    }

    return null;
  }

  /**
   * Set a value on a React-controlled input/textarea.
   * React ignores direct .value assignments because it tracks state internally.
   * We use the native input value setter and dispatch an input event.
   */
  function setReactValue(element, value) {
    const nativeInputValueSetter =
      element.tagName === 'TEXTAREA'
        ? Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, 'value').set
        : Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;

    nativeInputValueSetter.call(element, value);
    element.dispatchEvent(new Event('input', { bubbles: true }));
    element.dispatchEvent(new Event('change', { bubbles: true }));
  }

  // ── DOM OBSERVER: INJECT DROP ZONE WHEN FORM APPEARS ─────────────────

  let currentDropZone = null;

  /**
   * Watch for the step form container to appear in the DOM.
   * When a veteran selects a letter type and the form renders,
   * we inject the drop zone at the top of the first step.
   */
  function observeForForms() {
    const observer = new MutationObserver(() => {
      // Look for the form container — the tool uses these class patterns
      const formContainers = document.querySelectorAll(
        '.space-y-4, [class*="flex flex-col gap-5"]'
      );

      formContainers.forEach(container => {
        // Only inject into containers that have form fields (inputs/textareas)
        const hasFields = container.querySelector('textarea, input[type="text"]');
        if (!hasFields) return;

        // Don't inject twice
        if (container.querySelector('.zdc-prefill-zone')) return;

        // Don't inject into the main selection screen (only into step forms)
        if (container.closest('[class*="grid grid-cols"]')) return;

        // Inject drop zone at the top of the form
        const zone = createDropZone();
        container.insertBefore(zone, container.firstChild);
        currentDropZone = zone;
      });
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
    });
  }

  // ── INIT ─────────────────────────────────────────────────────────────

  function init() {
    injectStyles();
    observeForForms();
    console.log('[ZDC Letter Prefill] Ready — watching for forms');
  }

  // Start when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
