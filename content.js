// ============================================
// CourseWeb LabSheet Tracker — Content Script
// ============================================

(function () {
  "use strict";

  // ---- Config ----
  const FILTER_KEYWORDS = [
    "lab sheet",
    "labsheet",
    "lab submission",
    "practical",
    "submission link",
    "submission",
  ];

  const MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
  ];

  const CACHE_TTL_MS = 10 * 60 * 1000; // 10 minutes stale window
  const CACHE_MAX_AGE_MS = 30 * 24 * 60 * 60 * 1000; // Keep old months for 30 days
  const CACHE_STORAGE_KEY = `cwLabsheetCache:v1:${window.location.origin}`;

  // ---- State ----
  let panelOpen = false;
  let currentYear = new Date().getFullYear();
  let currentMonth = new Date().getMonth() + 1; // 1-indexed
  let selectedCourseFilter = "All"; // Active course filter
  let cachedResults = {};
  let cacheMeta = {};
  let isLoading = false;
  const inFlightRequests = {};
  const refreshingKeys = new Set();

  // ---- Helpers ----

  function getSesskey() {
    try {
      // Moodle stores the sesskey in the global M.cfg object
      if (typeof M !== "undefined" && M.cfg && M.cfg.sesskey) {
        return M.cfg.sesskey;
      }
    } catch (_) { }
    // Fallback: find it in a hidden input
    const input = document.querySelector('input[name="sesskey"]');
    if (input) return input.value;
    // Fallback: parse from a link
    const link = document.querySelector('a[href*="sesskey="]');
    if (link) {
      const match = link.href.match(/sesskey=([a-zA-Z0-9]+)/);
      if (match) return match[1];
    }
    return null;
  }

  function getMonthKey(year, month) {
    return `${year}-${month}`;
  }

  function hasChromeStorage() {
    return typeof chrome !== "undefined" && chrome.storage && chrome.storage.local;
  }

  function storageGetRaw(key) {
    if (hasChromeStorage()) {
      return new Promise((resolve) => {
        chrome.storage.local.get([key], (result) => {
          const runtimeError = chrome.runtime && chrome.runtime.lastError;
          if (runtimeError) {
            console.warn("[LabSheet Tracker] Failed to read extension storage:", runtimeError.message);
            resolve(null);
            return;
          }
          resolve(result ? (result[key] || null) : null);
        });
      });
    }

    try {
      const raw = localStorage.getItem(key);
      return Promise.resolve(raw ? JSON.parse(raw) : null);
    } catch (err) {
      console.warn("[LabSheet Tracker] Failed to read localStorage cache:", err);
      return Promise.resolve(null);
    }
  }

  function storageSetRaw(key, value) {
    if (hasChromeStorage()) {
      return new Promise((resolve) => {
        chrome.storage.local.set({ [key]: value }, () => {
          const runtimeError = chrome.runtime && chrome.runtime.lastError;
          if (runtimeError) {
            console.warn("[LabSheet Tracker] Failed to write extension storage:", runtimeError.message);
            resolve(false);
            return;
          }
          resolve(true);
        });
      });
    }

    try {
      localStorage.setItem(key, JSON.stringify(value));
      return Promise.resolve(true);
    } catch (err) {
      console.warn("[LabSheet Tracker] Failed to write localStorage cache:", err);
      return Promise.resolve(false);
    }
  }

  async function readPersistedCache() {
    const cache = await storageGetRaw(CACHE_STORAGE_KEY);
    return cache && typeof cache === "object" ? cache : {};
  }

  function rememberResults(cacheKey, results, updatedAt) {
    cachedResults[cacheKey] = Array.isArray(results) ? results : [];
    cacheMeta[cacheKey] = updatedAt || Date.now();
  }

  async function hydrateMonthFromStorage(cacheKey) {
    if (Object.prototype.hasOwnProperty.call(cachedResults, cacheKey)) {
      return {
        data: cachedResults[cacheKey],
        updatedAt: cacheMeta[cacheKey] || Date.now(),
      };
    }

    const persisted = await readPersistedCache();
    const entry = persisted[cacheKey];
    if (!entry || !Array.isArray(entry.data)) return null;

    const updatedAt = entry.updatedAt || 0;
    if (updatedAt && Date.now() - updatedAt > CACHE_MAX_AGE_MS) {
      delete persisted[cacheKey];
      await storageSetRaw(CACHE_STORAGE_KEY, persisted);
      return null;
    }

    rememberResults(cacheKey, entry.data, updatedAt || Date.now());
    return { data: entry.data, updatedAt: updatedAt || Date.now() };
  }

  async function persistMonthCache(cacheKey, results) {
    const now = Date.now();
    rememberResults(cacheKey, results, now);

    const persisted = await readPersistedCache();
    persisted[cacheKey] = {
      updatedAt: now,
      data: Array.isArray(results) ? results : [],
    };

    // Keep storage bounded by removing stale month entries.
    for (const key of Object.keys(persisted)) {
      const updatedAt = persisted[key] && persisted[key].updatedAt;
      if (!updatedAt || now - updatedAt > CACHE_MAX_AGE_MS) {
        delete persisted[key];
      }
    }

    await storageSetRaw(CACHE_STORAGE_KEY, persisted);
  }

  function isCacheFresh(updatedAt) {
    return Boolean(updatedAt) && Date.now() - updatedAt < CACHE_TTL_MS;
  }

  function formatRelativeTime(timestamp) {
    const elapsedMs = Date.now() - timestamp;
    const elapsedSeconds = Math.floor(elapsedMs / 1000);
    if (elapsedSeconds < 45) return "just now";

    const elapsedMinutes = Math.floor(elapsedSeconds / 60);
    if (elapsedMinutes < 60) return `${elapsedMinutes}m ago`;

    const elapsedHours = Math.floor(elapsedMinutes / 60);
    if (elapsedHours < 24) return `${elapsedHours}h ago`;

    return new Date(timestamp).toLocaleString([], {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  function getSyncMessage(cacheKey) {
    const updatedAt = cacheMeta[cacheKey];
    const isRefreshing = refreshingKeys.has(cacheKey);

    if (isRefreshing && updatedAt) {
      return "Showing cached data while updating...";
    }
    if (isRefreshing) {
      return "Updating...";
    }
    if (!updatedAt) {
      return "";
    }
    return `Updated ${formatRelativeTime(updatedAt)}`;
  }

  function updateRefreshButtonState() {
    const refreshBtn = document.getElementById("cw-refresh");
    if (!refreshBtn) return;
    const currentKey = getMonthKey(currentYear, currentMonth);
    if (isLoading || refreshingKeys.has(currentKey)) {
      refreshBtn.classList.add("spinning");
    } else {
      refreshBtn.classList.remove("spinning");
    }
  }

  // ---- Moodle Calendar API ----

  async function fetchCalendarEvents(year, month) {
    const sesskey = getSesskey();
    if (!sesskey) throw new Error("Could not find Moodle session key. Are you logged in?");

    const url = `/lib/ajax/service.php?sesskey=${sesskey}&info=core_calendar_get_calendar_monthly_view`;

    const payload = [
      {
        index: 0,
        methodname: "core_calendar_get_calendar_monthly_view",
        args: {
          year: String(year),
          month: String(month),
          courseid: 1,
          day: 1,
          view: "monthblock",
        },
      },
    ];

    const resp = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "same-origin",
      body: JSON.stringify(payload),
    });

    if (!resp.ok) throw new Error(`Calendar API returned ${resp.status}`);
    const data = await resp.json();

    if (data[0] && data[0].error) {
      throw new Error(data[0].exception?.message || "Calendar API error");
    }

    return data[0]?.data || null;
  }

  // ---- Event Filtering ----

  function extractEventsFromCalendar(calendarData) {
    const events = [];
    if (!calendarData || !calendarData.weeks) return events;

    for (const week of calendarData.weeks) {
      for (const day of week.days) {
        if (!day.events || day.events.length === 0) continue;
        for (const evt of day.events) {
          events.push(evt);
        }
      }
    }
    return events;
  }

  function isLabSubmission(event) {
    const name = (event.name || "").toLowerCase();
    return FILTER_KEYWORDS.some((kw) => name.includes(kw));
  }

  function filterLabSubmissions(events) {
    return events.filter(isLabSubmission);
  }

  // ---- Submission Page Scraper ----

  async function fetchSubmissionDetails(event) {
    // The event URL is typically the action URL pointing to the assignment
    let assignUrl = event.url || "";
    if (!assignUrl && event.action && event.action.url) {
      assignUrl = event.action.url;
    }
    // Sometimes the URL is in event.viewurl
    if (!assignUrl && event.viewurl) {
      assignUrl = event.viewurl;
    }

    if (!assignUrl) {
      return {
        eventName: event.name,
        error: "No URL available",
        url: null,
      };
    }

    try {
      const resp = await fetch(assignUrl, {
        credentials: "same-origin",
        headers: { Accept: "text/html" },
      });

      if (!resp.ok) {
        return { eventName: event.name, error: `HTTP ${resp.status}`, url: assignUrl };
      }

      const html = await resp.text();
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, "text/html");

      return parseSubmissionPage(doc, event, assignUrl);
    } catch (err) {
      return { eventName: event.name, error: err.message, url: assignUrl };
    }
  }

  function parseSubmissionPage(doc, event, url) {
    const result = {
      eventName: event.name || "Unknown",
      url: url,
      dueDate: event.formattedtime || "",
      timestart: event.timestart || 0,
      error: null,
    };

    // ---- Module / Course name from breadcrumbs ----
    const breadcrumbs = doc.querySelectorAll("nav#breadcrumb-nav ol li a, .breadcrumb li a, ol.breadcrumb li a");
    const crumbTexts = Array.from(breadcrumbs).map((a) => a.textContent.trim());

    // Course name is typically the one containing module code like "SE3032 - ..."
    result.moduleName = crumbTexts.find((t) => /^[A-Z]{2,4}\d{3,4}/.test(t)) || "";
    if (!result.moduleName && crumbTexts.length >= 3) {
      // Fallback: second or third breadcrumb is often the course
      result.moduleName = crumbTexts[crumbTexts.length - 2] || "";
    }

    // Extract short course code, e.g. "SE3032" from "SE3032 - Software Engineering"
    const codeMatch = result.moduleName.match(/^([A-Z]{2,4}\s?\d{3,4})/i);
    result.courseCode = codeMatch ? codeMatch[1].trim() : result.moduleName.trim();

    // ---- Assignment name ----
    // Prioritize specific selectors to avoid matching sr-only "Blocks" h2
    const heading =
      doc.querySelector(".page-header-headings h1") ||
      doc.querySelector("#page-header h1") ||
      doc.querySelector("#region-main h2:not(.sr-only)") ||
      doc.querySelector(".activity-header h2");
    if (heading) {
      result.assignmentName = heading.textContent.trim();
    } else {
      // Fallback: extract from page title (format: "CourseCode: Assignment Name | CourseWeb")
      const titleMatch = (doc.title || "").match(/:\s*(.+?)\s*\|/);
      result.assignmentName = titleMatch ? titleMatch[1].trim() : event.name;
    }

    // ---- Opened / Due dates from the assignment description area ----
    const infoItems = doc.querySelectorAll(".box.generalbox .generaltable tr, .submissionstatustable .cell");

    // Try to find "Opened" and "Due" from the assignment intro
    const openedEl = findTextInDoc(doc, "Opened:");
    const dueEl = findTextInDoc(doc, "Due:");
    if (openedEl) result.openedDate = openedEl;
    if (dueEl) result.dueDate = dueEl;

    // ---- Submission status table ----
    const statusTable = doc.querySelector(".submissionstatustable, .generaltable");
    if (statusTable) {
      const rows = statusTable.querySelectorAll("tr");
      for (const row of rows) {
        const cells = row.querySelectorAll("td, th");
        if (cells.length < 2) continue;

        const label = cells[0].textContent.trim().toLowerCase();
        const value = cells[1].textContent.trim();

        if (label.includes("submission status")) {
          result.submissionStatus = value;
        } else if (label.includes("grading status")) {
          result.gradingStatus = value;
        } else if (label.includes("time remaining")) {
          result.timeRemaining = value;
        } else if (label.includes("last modified")) {
          result.lastModified = value;
        } else if (label.includes("file submission")) {
          result.fileSubmissions = value;
        } else if (label.includes("due date")) {
          result.dueDate = value;
        }
      }
    }

    // Fallback: try the info box at the top for dates
    if (!result.dueDate || result.dueDate === "") {
      const allText = doc.body ? doc.body.innerText : "";
      const dueMatch = allText.match(/Due:\s*(.+?)(?:\n|$)/);
      if (dueMatch) result.dueDate = dueMatch[1].trim();
    }

    return result;
  }

  function findTextInDoc(doc, prefix) {
    // Search for text nodes containing "Opened:" or "Due:"
    const allElements = doc.querySelectorAll("p, div, span, td, th");
    for (const el of allElements) {
      const text = el.textContent.trim();
      if (text.startsWith(prefix)) {
        return text.replace(prefix, "").trim();
      }
    }
    return null;
  }

  // ---- Main Pipeline ----

  async function runScraper(year, month, options = {}) {
    const cacheKey = getMonthKey(year, month);
    const { background = false, forceRefresh = false } = options;

    if (!forceRefresh && Object.prototype.hasOwnProperty.call(cachedResults, cacheKey)) {
      return cachedResults[cacheKey];
    }

    if (inFlightRequests[cacheKey]) {
      return inFlightRequests[cacheKey];
    }

    const request = (async () => {
      if (background) {
        refreshingKeys.add(cacheKey);
      } else {
        isLoading = true;
        renderPanel();
        updateLoadingText("Fetching calendar events...");
      }
      updateRefreshButtonState();

      try {
        // Step 1: Fetch calendar
        const calendarData = await fetchCalendarEvents(year, month);
        const allEvents = extractEventsFromCalendar(calendarData);

        // Step 2: Filter lab submissions
        const labEvents = filterLabSubmissions(allEvents);
        if (!background) {
          updateLoadingText(`Found ${labEvents.length} lab submissions. Fetching details...`);
        }

        if (labEvents.length === 0) {
          if (!background) isLoading = false;
          await persistMonthCache(cacheKey, []);
          if (panelOpen && getMonthKey(currentYear, currentMonth) === cacheKey) {
            renderPanel();
          }
          return [];
        }

        // Step 3: Fetch submission details (with concurrency limit)
        const results = [];
        const batchSize = 3; // Fetch 3 at a time to avoid overwhelming the server

        for (let i = 0; i < labEvents.length; i += batchSize) {
          const batch = labEvents.slice(i, i + batchSize);
          const batchResults = await Promise.all(
            batch.map((evt) => fetchSubmissionDetails(evt))
          );
          results.push(...batchResults);

          if (!background) {
            updateLoadingText(
              `Fetched ${Math.min(i + batchSize, labEvents.length)}/${labEvents.length} submission details...`
            );
          }
        }

        if (!background) isLoading = false;
        await persistMonthCache(cacheKey, results);
        if (panelOpen && getMonthKey(currentYear, currentMonth) === cacheKey) {
          renderPanel();
        }
        return results;
      } catch (err) {
        if (!background) {
          isLoading = false;
          renderError(err.message);
        } else {
          console.warn("[LabSheet Tracker] Background refresh failed:", err);
        }
        return Object.prototype.hasOwnProperty.call(cachedResults, cacheKey)
          ? cachedResults[cacheKey]
          : [];
      } finally {
        if (background) {
          refreshingKeys.delete(cacheKey);
          if (panelOpen && getMonthKey(currentYear, currentMonth) === cacheKey) {
            renderPanel();
          }
        }
        delete inFlightRequests[cacheKey];
        updateRefreshButtonState();
      }
    })();

    inFlightRequests[cacheKey] = request;
    return request;
  }

  async function loadMonthData(year, month, options = {}) {
    const cacheKey = getMonthKey(year, month);
    const { forceRefresh = false } = options;
    const cachedEntry = await hydrateMonthFromStorage(cacheKey);

    if (cachedEntry) {
      if (panelOpen && getMonthKey(currentYear, currentMonth) === cacheKey) {
        renderPanel();
      }

      if (forceRefresh) {
        runScraper(year, month, { background: true, forceRefresh: true });
      } else if (!isCacheFresh(cachedEntry.updatedAt)) {
        runScraper(year, month, { background: true, forceRefresh: true });
      }
      return cachedEntry.data;
    }

    return runScraper(year, month, { background: false, forceRefresh: true });
  }

  function loadCurrentMonth(options = {}) {
    loadMonthData(currentYear, currentMonth, options).catch((err) => {
      console.error("[LabSheet Tracker] Failed to load month data:", err);
      if (!isLoading && panelOpen) {
        renderError(err.message || "Failed to load data");
      }
    });
  }

  // ---- UI Rendering ----

  function createTriggerButton() {
    if (document.getElementById("cw-labsheet-trigger")) return;

    const btn = document.createElement("button");
    btn.id = "cw-labsheet-trigger";
    btn.title = "LabSheet Tracker";
    btn.innerHTML = `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z"/>
      <polyline points="14 2 14 8 20 8" fill="none" stroke="currentColor" stroke-width="1.5"/>
      <line x1="16" y1="13" x2="8" y2="13" stroke="currentColor" stroke-width="1.5"/>
      <line x1="16" y1="17" x2="8" y2="17" stroke="currentColor" stroke-width="1.5"/>
      <line x1="10" y1="9" x2="8" y2="9" stroke="currentColor" stroke-width="1.5"/>
    </svg>`;
    btn.addEventListener("click", togglePanel);
    document.body.appendChild(btn);

    // Backdrop
    const backdrop = document.createElement("div");
    backdrop.id = "cw-labsheet-backdrop";
    backdrop.addEventListener("click", togglePanel);
    document.body.appendChild(backdrop);
  }

  function createPanel() {
    if (document.getElementById("cw-labsheet-panel")) return;

    const panel = document.createElement("div");
    panel.id = "cw-labsheet-panel";
    panel.innerHTML = `
      <div class="cw-panel-header">
        <h2>📋 LabSheet Tracker</h2>
        <p class="cw-subtitle">Lab & Practical Submissions</p>
      </div>
      <div class="cw-controls">
        <div class="cw-month-nav">
          <button id="cw-prev-month" title="Previous month">◀</button>
          <span class="cw-month-label" id="cw-month-label">${MONTH_NAMES[currentMonth - 1]} ${currentYear}</span>
          <button id="cw-next-month" title="Next month">▶</button>
        </div>
        <button class="cw-refresh-btn" id="cw-refresh" title="Refresh">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <polyline points="23 4 23 10 17 10"/>
            <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
          </svg>
        </button>
      </div>
      <div class="cw-stats" id="cw-stats"></div>
      <div class="cw-filters" id="cw-filters" style="display: none;"></div>
      <div class="cw-pill-tooltip" id="cw-pill-tooltip"></div>
      <div class="cw-submissions-list" id="cw-submissions-list">
        <div class="cw-empty">
          <div class="cw-empty-icon">📄</div>
          <div class="cw-empty-text">Click the refresh button or change months to load submissions.</div>
        </div>
      </div>
    `;
    document.body.appendChild(panel);

    // Event listeners
    document.getElementById("cw-prev-month").addEventListener("click", () => {
      currentMonth--;
      if (currentMonth < 1) {
        currentMonth = 12;
        currentYear--;
      }
      selectedCourseFilter = "All"; // Reset filter on month change
      updateMonthLabel();
      loadCurrentMonth();
    });

    document.getElementById("cw-next-month").addEventListener("click", () => {
      currentMonth++;
      if (currentMonth > 12) {
        currentMonth = 1;
        currentYear++;
      }
      selectedCourseFilter = "All"; // Reset filter on month change
      updateMonthLabel();
      loadCurrentMonth();
    });

    document.getElementById("cw-refresh").addEventListener("click", () => {
      loadCurrentMonth({ forceRefresh: true });
    });

    updateRefreshButtonState();
  }

  function togglePanel() {
    panelOpen = !panelOpen;
    const panel = document.getElementById("cw-labsheet-panel");
    const backdrop = document.getElementById("cw-labsheet-backdrop");
    const trigger = document.getElementById("cw-labsheet-trigger");

    if (panelOpen) {
      panel.classList.add("open");
      backdrop.classList.add("visible");
      trigger.classList.add("active");
      loadCurrentMonth();
    } else {
      panel.classList.remove("open");
      backdrop.classList.remove("visible");
      trigger.classList.remove("active");
    }
  }

  function updateMonthLabel() {
    const label = document.getElementById("cw-month-label");
    if (label) label.textContent = `${MONTH_NAMES[currentMonth - 1]} ${currentYear}`;
    updateRefreshButtonState();
  }

  function updateLoadingText(text, progress) {
    const list = document.getElementById("cw-submissions-list");
    if (!list) return;

    list.innerHTML = `
      <div class="cw-loading">
        <div class="cw-loading-spinner"></div>
        <div class="cw-loading-text">${text}</div>
        ${progress ? `<div class="cw-loading-progress">${progress}</div>` : ""}
      </div>
    `;
  }

  function renderError(message) {
    const list = document.getElementById("cw-submissions-list");
    if (!list) return;
    list.innerHTML = `<div class="cw-error">⚠️ ${message}</div>`;
  }

  function getStatusClass(status) {
    if (!status) return "unknown";
    const s = status.toLowerCase();
    if (s.includes("submitted")) return "submitted";
    if (s.includes("no attempt") || s.includes("no submission")) return "no-attempt";
    if (s.includes("draft")) return "draft";
    return "unknown";
  }

  function getGradeClass(status) {
    if (!status) return "not-graded";
    return status.toLowerCase().includes("graded") && !status.toLowerCase().includes("not graded")
      ? "graded"
      : "not-graded";
  }

  function renderPanel() {
    const cacheKey = getMonthKey(currentYear, currentMonth);
    const results = cachedResults[cacheKey];
    const list = document.getElementById("cw-submissions-list");
    const stats = document.getElementById("cw-stats");
    const filtersContainer = document.getElementById("cw-filters");
    const syncMessage = getSyncMessage(cacheKey);

    if (!list || !stats || !filtersContainer) return;

    // Clean up existing download-all bar to prevent duplicates
    const existingDlBar = document.querySelector('.cw-download-all-bar');
    if (existingDlBar) existingDlBar.remove();

    if (isLoading) return; // Loading state handled by updateLoadingText

    if (!results || results.length === 0) {
      stats.innerHTML = syncMessage ? `<div class="cw-cache-note">${escapeHtml(syncMessage)}</div>` : "";
      filtersContainer.style.display = 'none';
      list.innerHTML = `
        <div class="cw-empty">
          <div class="cw-empty-icon">📭</div>
          <div class="cw-empty-text">No lab submissions found for ${MONTH_NAMES[currentMonth - 1]} ${currentYear}</div>
        </div>
      `;
      return;
    }

    // Extract unique course modules
    const courseNames = new Set();
    const courseTitles = new Map(); // Store full name for tooltip mappings
    results.forEach(r => {
      // Fallback to moduleName if courseCode is missing from older caches
      const code = r.courseCode || r.moduleName;
      if (code && code.trim() !== '') {
        const trimmedCode = code.trim();
        courseNames.add(trimmedCode);
        if (!courseTitles.has(trimmedCode) && r.moduleName) {
          courseTitles.set(trimmedCode, r.moduleName.trim());
        }
      }
    });

    const uniqueCourses = Array.from(courseNames).sort();

    // Reset filter if current choice isn't in this month's courses
    if (selectedCourseFilter !== "All" && !uniqueCourses.includes(selectedCourseFilter)) {
      selectedCourseFilter = "All";
    }

    // Render Filters
    if (uniqueCourses.length > 1) {
      filtersContainer.style.display = 'flex';
      let filtersHtml = `<button class="cw-filter-pill ${selectedCourseFilter === 'All' ? 'active' : ''}" data-course="All" data-tooltip="All Submissions">All</button>`;
      uniqueCourses.forEach(course => {
        const fullName = courseTitles.get(course) || course;
        filtersHtml += `<button class="cw-filter-pill ${selectedCourseFilter === course ? 'active' : ''}" data-course="${escapeHtml(course)}" data-tooltip="${escapeHtml(fullName)}">${escapeHtml(course)}</button>`;
      });
      filtersContainer.innerHTML = filtersHtml;

      filtersContainer.querySelectorAll('.cw-filter-pill').forEach(btn => {
        btn.addEventListener('click', (e) => {
          selectedCourseFilter = e.target.getAttribute('data-course');
          const tooltip = document.getElementById('cw-pill-tooltip');
          if (tooltip) tooltip.classList.remove('visible');
          renderPanel(); // Re-render logic to apply filter
        });

        btn.addEventListener('mouseenter', (e) => {
          const tooltip = document.getElementById('cw-pill-tooltip');
          if (tooltip) {
            tooltip.textContent = e.target.getAttribute('data-tooltip');
            tooltip.classList.add('visible');
            const rect = e.target.getBoundingClientRect();
            const panelRect = document.getElementById('cw-labsheet-panel').getBoundingClientRect();

            tooltip.style.left = (rect.left - panelRect.left + (rect.width / 2)) + 'px';
            tooltip.style.top = (rect.top - panelRect.top - 8) + 'px';
          }
        });

        btn.addEventListener('mouseleave', () => {
          const tooltip = document.getElementById('cw-pill-tooltip');
          if (tooltip) {
            tooltip.classList.remove('visible');
          }
        });
      });
    } else {
      filtersContainer.style.display = 'none';
    }

    // Apply Filter
    const filteredResults = selectedCourseFilter === "All" ? results : results.filter(r => (r.courseCode || r.moduleName).trim() === selectedCourseFilter);

    // Compute stats using filtered results
    const submitted = filteredResults.filter(
      (r) => r.submissionStatus && r.submissionStatus.toLowerCase().includes("submitted")
    ).length;
    const noAttempt = filteredResults.filter(
      (r) =>
        !r.submissionStatus ||
        r.submissionStatus.toLowerCase().includes("no attempt") ||
        r.submissionStatus.toLowerCase().includes("no submission")
    ).length;
    const overdue = filteredResults.filter(
      (r) => r.timeRemaining && r.timeRemaining.toLowerCase().includes("overdue")
    ).length;

    stats.innerHTML = `
      <div class="cw-stat-card total">
        <div class="cw-stat-value">${filteredResults.length}</div>
        <div class="cw-stat-label">Total</div>
      </div>
      <div class="cw-stat-card submitted">
        <div class="cw-stat-value">${submitted}</div>
        <div class="cw-stat-label">Submitted</div>
      </div>
      <div class="cw-stat-card pending">
        <div class="cw-stat-value">${noAttempt}</div>
        <div class="cw-stat-label">Pending</div>
      </div>
      <div class="cw-stat-card overdue">
        <div class="cw-stat-value">${overdue}</div>
        <div class="cw-stat-label">Overdue</div>
      </div>
      ${syncMessage ? `<div class="cw-cache-note">${escapeHtml(syncMessage)}</div>` : ""}
    `;

    // Store ALL results globally for the template generator (we probably still want to download all pending for the month or conditionally the selected)
    // Actually, users might prefer downloading only for the filtered list
    window.__cwLabResults = filteredResults;

    // Add download all pending button if there are pending items
    if (noAttempt + overdue > 0 && window.__labTemplateGenerator) {
      const dlAllBtn = document.createElement('div');
      dlAllBtn.className = 'cw-download-all-bar';
      dlAllBtn.innerHTML = `<button class="cw-download-all-btn" id="cw-download-all" title="Download DOCX templates for all pending labs">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
        Download All Pending Templates
      </button>`;
      stats.parentElement.insertBefore(dlAllBtn, list);
      document.getElementById('cw-download-all').addEventListener('click', () => {
        window.__labTemplateGenerator.generateAllPendingTemplates(results);
      });
    }

    // Sort: pending/no-attempt first, then by due date
    const sorted = [...filteredResults].sort((a, b) => {
      const aSubmitted = a.submissionStatus && a.submissionStatus.toLowerCase().includes("submitted");
      const bSubmitted = b.submissionStatus && b.submissionStatus.toLowerCase().includes("submitted");
      if (aSubmitted !== bSubmitted) return aSubmitted ? 1 : -1;
      return (a.timestart || 0) - (b.timestart || 0);
    });

    list.innerHTML = sorted
      .map((r) => {
        const statusClass = getStatusClass(r.submissionStatus);
        const statusText = r.submissionStatus || "Unknown";
        const gradeClass = getGradeClass(r.gradingStatus);
        const gradeText = r.gradingStatus || "—";
        const timeClass = r.timeRemaining
          ? r.timeRemaining.toLowerCase().includes("early")
            ? "early"
            : r.timeRemaining.toLowerCase().includes("overdue") || r.timeRemaining.toLowerCase().includes("late")
              ? "overdue"
              : ""
          : "";

        // Determine if this card should show a download button
        const isPending = statusClass === 'no-attempt' || statusClass === 'unknown' || statusClass === 'draft';
        const isOverdue = r.timeRemaining && (r.timeRemaining.toLowerCase().includes('overdue') || r.timeRemaining.toLowerCase().includes('late'));
        const showDownload = (isPending || isOverdue) && window.__labTemplateGenerator;

        return `
          <div class="cw-submission-card" ${r.url ? `data-url="${escapeHtml(r.url)}"` : ""}>
            <div class="cw-card-header">
              <div class="cw-assignment-name">
                ${r.url ? `<a href="${r.url}" target="_blank">${escapeHtml(r.assignmentName || r.eventName)}</a>` : escapeHtml(r.assignmentName || r.eventName)}
              </div>
              <span class="cw-status-badge ${statusClass}">${escapeHtml(statusText)}</span>
            </div>
            <div class="cw-card-details">
              ${r.dueDate ? `<div class="cw-detail-row"><span class="cw-detail-label">Due</span><span class="cw-detail-value">${escapeHtml(r.dueDate)}</span></div>` : ""}
              ${r.gradingStatus ? `<div class="cw-detail-row"><span class="cw-detail-label">Grade</span><span class="cw-grade-badge ${gradeClass}">${escapeHtml(gradeText)}</span></div>` : ""}
              ${r.timeRemaining ? `<div class="cw-detail-row"><span class="cw-detail-label">Time</span><span class="cw-detail-value ${timeClass}">${escapeHtml(r.timeRemaining)}</span></div>` : ""}
              ${r.lastModified ? `<div class="cw-detail-row"><span class="cw-detail-label">Modified</span><span class="cw-detail-value">${escapeHtml(r.lastModified)}</span></div>` : ""}
              ${r.fileSubmissions ? `<div class="cw-detail-row"><span class="cw-detail-label">Files</span><span class="cw-detail-value">${escapeHtml(r.fileSubmissions)}</span></div>` : ""}
              ${r.moduleName ? `<span class="cw-module-tag">${escapeHtml(r.moduleName)}</span>` : ""}
            </div>
            ${showDownload ? `<button class="cw-download-btn" data-result-index="${results.indexOf(r)}" title="Download DOCX template">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
              Download Template
            </button>` : ""}
            ${r.error ? `<div class="cw-error" style="padding:6px 0;font-size:11px;">⚠️ ${escapeHtml(r.error)}</div>` : ""}
          </div>
        `;
      })
      .join("");

    // ---- Event delegation for cards (runs in content script world) ----
    // Card click → open URL
    list.querySelectorAll('.cw-submission-card[data-url]').forEach((card) => {
      card.addEventListener('click', (e) => {
        // Don't navigate if clicking a link or download button
        if (e.target.closest('a') || e.target.closest('.cw-download-btn')) return;
        window.open(card.dataset.url, '_blank');
      });
    });

    // Download button click → generate DOCX
    list.querySelectorAll('.cw-download-btn[data-result-index]').forEach((btn) => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const idx = parseInt(btn.dataset.resultIndex, 10);
        if (window.__labTemplateGenerator && results[idx]) {
          window.__labTemplateGenerator.generateLabTemplate(results[idx]);
        }
      });
    });
  }

  function escapeHtml(str) {
    if (!str) return "";
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }

  // ---- Init ----

  function init() {
    createTriggerButton();
    createPanel();
    console.log("[LabSheet Tracker] Extension loaded on", window.location.href);
  }

  // Wait for page readiness
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
