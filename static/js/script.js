/**
 * script.js — Digital Notebook
 * Handles: Instant search, delete confirmation, API calls,
 *          form validation, toast notifications, character counter.
 */

/* ═══════════════════════════════════════════════════════════════════════════
   Utility helpers
   ═══════════════════════════════════════════════════════════════════════════ */

/**
 * Show a toast notification.
 * @param {string} message - Text to display.
 * @param {'success'|'error'|'info'} [type='info'] - Toast style.
 * @param {number} [duration=2800] - Auto-dismiss delay in ms.
 */
function showToast(message, type = 'info', duration = 2800) {
  const toast = document.getElementById('toast');
  if (!toast) return;

  toast.textContent = message;
  toast.className = `toast toast--${type} toast-visible`;

  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => {
    toast.classList.remove('toast-visible');
  }, duration);
}

/**
 * Escape HTML to prevent XSS when injecting untrusted content.
 * @param {string} str
 * @returns {string}
 */
function escapeHtml(str) {
  const div = document.createElement('div');
  div.appendChild(document.createTextNode(str));
  return div.innerHTML;
}

/**
 * Highlight occurrences of a query string inside text.
 * Returns an HTML string with <mark class="highlight"> wrapping matches.
 * @param {string} text - Raw text content.
 * @param {string} query - Search term (case-insensitive).
 * @returns {string} HTML string.
 */
function highlightText(text, query) {
  if (!query) return escapeHtml(text);
  const escaped = escapeHtml(text);
  const escapedQuery = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const regex = new RegExp(`(${escapedQuery})`, 'gi');
  return escaped.replace(regex, '<mark class="highlight">$1</mark>');
}

/**
 * Set a button to a loading state (disables it, shows spinner).
 * @param {HTMLButtonElement} btn
 * @param {string} loadingText
 */
function setButtonLoading(btn, loadingText = 'Saving…') {
  btn.dataset.originalHtml = btn.innerHTML;
  btn.innerHTML = `<span class="spinner"></span> ${loadingText}`;
  btn.disabled = true;
}

/**
 * Restore a button from its loading state.
 * @param {HTMLButtonElement} btn
 */
function restoreButton(btn) {
  if (btn.dataset.originalHtml) {
    btn.innerHTML = btn.dataset.originalHtml;
    delete btn.dataset.originalHtml;
  }
  btn.disabled = false;
}

/* ═══════════════════════════════════════════════════════════════════════════
   Search — Home screen
   ═══════════════════════════════════════════════════════════════════════════ */

(function initSearch() {
  const searchInput = document.getElementById('searchInput');
  if (!searchInput) return;  // Not on home screen

  const searchClear   = document.getElementById('searchClear');
  const resultsBar    = document.getElementById('resultsBar');
  const resultsText   = document.getElementById('resultsText');
  const clearSearchBtn = document.getElementById('clearSearchBtn');
  const noteCountBadge = document.getElementById('noteCountBadge');
  const noResultsState = document.getElementById('noResultsState');
  const emptyState     = document.getElementById('emptyState');

  let debounceTimer = null;
  let allCards = [];

  /**
   * Collect all note cards once the DOM is ready.
   * Each card stores its title and content as data attributes.
   */
  function gatherCards() {
    allCards = Array.from(document.querySelectorAll('.note-card[data-id]'));
  }

  /**
   * Perform client-side search across pre-rendered note cards.
   * Falls back to API search for highlight injection.
   * @param {string} query
   */
  function performSearch(query) {
    const q = query.trim().toLowerCase();

    if (!q) {
      // Show all cards; reset UI
      allCards.forEach(card => {
        card.hidden = false;
        resetCardHighlights(card);
      });
      if (resultsBar)    resultsBar.hidden = true;
      if (searchClear)   searchClear.hidden = true;
      if (noResultsState) noResultsState.hidden = true;
      if (emptyState && allCards.length === 0) emptyState.hidden = false;
      updateBadge(allCards.length);
      return;
    }

    if (searchClear) searchClear.hidden = false;

    // Filter cards
    let visibleCount = 0;
    allCards.forEach(card => {
      const title   = card.dataset.title   || '';
      const content = card.dataset.content || '';
      const matches = title.includes(q) || content.includes(q);
      card.hidden = !matches;
      if (matches) {
        visibleCount++;
        highlightCard(card, query.trim());
      } else {
        resetCardHighlights(card);
      }
    });

    // Update results bar
    if (resultsBar) {
      resultsBar.hidden = false;
      resultsText.textContent = `${visibleCount} result${visibleCount !== 1 ? 's' : ''} for "${query.trim()}"`;
    }

    // No-results state
    if (noResultsState) noResultsState.hidden = visibleCount > 0;
    if (emptyState)      emptyState.hidden = true;

    updateBadge(visibleCount);
  }

  /**
   * Highlight matched text inside a note card's title and preview.
   * @param {HTMLElement} card
   * @param {string} query
   */
  function highlightCard(card, query) {
    const titleEl   = card.querySelector('.note-title');
    const previewEl = card.querySelector('.note-preview');

    if (titleEl && !titleEl.dataset.original) {
      titleEl.dataset.original = titleEl.textContent;
    }
    if (previewEl && !previewEl.dataset.original) {
      previewEl.dataset.original = previewEl.textContent;
    }

    if (titleEl)   titleEl.innerHTML   = highlightText(titleEl.dataset.original   || titleEl.textContent, query);
    if (previewEl) previewEl.innerHTML = highlightText(previewEl.dataset.original || previewEl.textContent, query);
  }

  /**
   * Remove highlight marks from a card, restoring original text.
   * @param {HTMLElement} card
   */
  function resetCardHighlights(card) {
    const titleEl   = card.querySelector('.note-title');
    const previewEl = card.querySelector('.note-preview');
    if (titleEl && titleEl.dataset.original) {
      titleEl.textContent = titleEl.dataset.original;
    }
    if (previewEl && previewEl.dataset.original) {
      previewEl.textContent = previewEl.dataset.original;
    }
  }

  /** Update the note count badge. */
  function updateBadge(count) {
    if (noteCountBadge) {
      noteCountBadge.textContent = `${count} note${count !== 1 ? 's' : ''}`;
    }
  }

  // ── Event listeners ──

  searchInput.addEventListener('input', () => {
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => performSearch(searchInput.value), 220);
  });

  if (searchClear) {
    searchClear.addEventListener('click', clearSearch);
  }
  if (clearSearchBtn) {
    clearSearchBtn.addEventListener('click', clearSearch);
  }

  function clearSearch() {
    searchInput.value = '';
    searchInput.focus();
    performSearch('');
  }

  // Keyboard shortcut: '/' focuses search
  document.addEventListener('keydown', (e) => {
    if (e.key === '/' && document.activeElement.tagName !== 'INPUT' && document.activeElement.tagName !== 'TEXTAREA') {
      e.preventDefault();
      searchInput.focus();
    }
    // Escape clears search
    if (e.key === 'Escape' && document.activeElement === searchInput) {
      clearSearch();
    }
  });

  // Initialise
  gatherCards();
})();


/* ═══════════════════════════════════════════════════════════════════════════
   Delete Confirmation Modal — Home screen
   ═══════════════════════════════════════════════════════════════════════════ */

(function initDeleteModal() {
  const modal          = document.getElementById('deleteModal');
  if (!modal) return;

  const modalNoteTitle = document.getElementById('modalNoteTitle');
  const cancelBtn      = document.getElementById('cancelDeleteBtn');
  const confirmBtn     = document.getElementById('confirmDeleteBtn');

  let pendingDeleteId    = null;
  let pendingDeleteCard  = null;

  /** Open the delete confirmation modal. */
  function openModal(noteId, noteTitle, cardEl) {
    pendingDeleteId   = noteId;
    pendingDeleteCard = cardEl;
    modalNoteTitle.textContent = `"${noteTitle}"`;
    modal.hidden = false;
    modal.removeAttribute('hidden');
    // Trap focus
    cancelBtn.focus();
    document.body.style.overflow = 'hidden';
  }

  /** Close the modal without deleting. */
  function closeModal() {
    modal.hidden = true;
    modal.setAttribute('hidden', '');
    pendingDeleteId = null;
    pendingDeleteCard = null;
    document.body.style.overflow = '';
  }

  /** Call the API to delete the note, then remove the card from DOM. */
  async function deleteNote() {
    if (!pendingDeleteId) return;

    const noteId = pendingDeleteId;
    const card   = pendingDeleteCard;
    closeModal();

    try {
      setButtonLoading(confirmBtn, 'Deleting…');
      const response = await fetch(`/api/notes/${noteId}`, { method: 'DELETE' });
      const data = await response.json();

      if (data.success) {
        // Animate card removal
        if (card) {
          card.style.transition = 'opacity 0.3s ease, transform 0.3s ease, max-height 0.35s ease';
          card.style.opacity = '0';
          card.style.transform = 'scale(0.95)';
          card.style.overflow = 'hidden';
          setTimeout(() => {
            card.style.maxHeight = card.offsetHeight + 'px';
            requestAnimationFrame(() => {
              card.style.maxHeight = '0';
              card.style.marginBottom = '0';
              card.style.paddingTop = '0';
              card.style.paddingBottom = '0';
            });
            setTimeout(() => {
              card.remove();
              updateCountBadge();
              showEmptyStateIfNeeded();
            }, 380);
          }, 250);
        }
        showToast('Note deleted successfully', 'success');
      } else {
        showToast(data.error || 'Failed to delete note.', 'error');
      }
    } catch (err) {
      console.error('[Delete] Error:', err);
      showToast('Network error. Please try again.', 'error');
    } finally {
      restoreButton(confirmBtn);
    }
  }

  /** Update the note count badge in the header. */
  function updateCountBadge() {
    const badge = document.getElementById('noteCountBadge');
    const remaining = document.querySelectorAll('.note-card[data-id]').length;
    if (badge) badge.textContent = `${remaining} note${remaining !== 1 ? 's' : ''}`;
  }

  /** Show empty state if no cards remain. */
  function showEmptyStateIfNeeded() {
    const cards = document.querySelectorAll('.note-card[data-id]');
    const emptyState = document.getElementById('emptyState');
    if (cards.length === 0 && emptyState) {
      emptyState.hidden = false;
    }
  }

  // ── Attach delete button listeners ──
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('.btn-delete');
    if (!btn) return;
    e.preventDefault();
    const noteId    = parseInt(btn.dataset.id, 10);
    const noteTitle = btn.dataset.title || 'this note';
    const card      = btn.closest('.note-card');
    openModal(noteId, noteTitle, card);
  });

  // ── Modal controls ──
  cancelBtn.addEventListener('click', closeModal);
  confirmBtn.addEventListener('click', deleteNote);

  // Close on overlay click
  modal.addEventListener('click', (e) => {
    if (e.target === modal) closeModal();
  });

  // Close on Escape
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && !modal.hidden) closeModal();
  });
})();


/* ═══════════════════════════════════════════════════════════════════════════
   Add Note Form — add_note.html
   ═══════════════════════════════════════════════════════════════════════════ */

(function initAddNoteForm() {
  const form = document.getElementById('addNoteForm');
  if (!form) return;

  const titleInput   = document.getElementById('noteTitle');
  const contentInput = document.getElementById('noteContent');
  const titleCounter = document.getElementById('titleCounter');
  const titleError   = document.getElementById('titleError');
  const contentError = document.getElementById('contentError');
  const saveBtn      = document.getElementById('saveBtn');
  const discardBtn   = document.getElementById('discardBtn');

  // ── Character counter ──
  if (titleInput && titleCounter) {
    titleInput.addEventListener('input', () => {
      const len = titleInput.value.length;
      const max = parseInt(titleInput.maxLength, 10) || 200;
      titleCounter.textContent = `${len} / ${max}`;
      titleCounter.className = 'char-counter' +
        (len >= max ? ' at-limit' : len >= max * 0.85 ? ' near-limit' : '');
    });
  }

  // ── Validation ──
  function validateTitle() {
    const val = titleInput.value.trim();
    if (!val) {
      showFieldError(titleInput, titleError, 'Title is required.');
      return false;
    }
    clearFieldError(titleInput, titleError);
    return true;
  }

  function validateContent() {
    const val = contentInput.value.trim();
    if (!val) {
      showFieldError(contentInput, contentError, 'Content cannot be empty.');
      return false;
    }
    clearFieldError(contentInput, contentError);
    return true;
  }

  function showFieldError(input, errorEl, message) {
    input.closest('.form-group').classList.add('has-error');
    errorEl.textContent = message;
    errorEl.hidden = false;
  }

  function clearFieldError(input, errorEl) {
    input.closest('.form-group').classList.remove('has-error');
    errorEl.hidden = true;
  }

  titleInput.addEventListener('blur', validateTitle);
  contentInput.addEventListener('blur', validateContent);
  titleInput.addEventListener('input', () => clearFieldError(titleInput, titleError));
  contentInput.addEventListener('input', () => clearFieldError(contentInput, contentError));

  // ── Submit ──
  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const titleOk   = validateTitle();
    const contentOk = validateContent();
    if (!titleOk || !contentOk) return;

    setButtonLoading(saveBtn, 'Saving…');

    try {
      const response = await fetch('/api/notes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title:   titleInput.value.trim(),
          content: contentInput.value.trim(),
        }),
      });
      const data = await response.json();

      if (data.success) {
        showToast('Note saved!', 'success', 1500);
        setTimeout(() => { window.location.href = '/'; }, 800);
      } else {
        showToast(data.error || 'Failed to save note.', 'error');
        restoreButton(saveBtn);
      }
    } catch (err) {
      console.error('[AddNote] Error:', err);
      showToast('Network error. Please try again.', 'error');
      restoreButton(saveBtn);
    }
  });

  // ── Discard ──
  if (discardBtn) {
    discardBtn.addEventListener('click', () => {
      if (titleInput.value.trim() || contentInput.value.trim()) {
        if (confirm('Discard this note? Your changes will be lost.')) {
          window.location.href = '/';
        }
      } else {
        window.location.href = '/';
      }
    });
  }

  // Auto-resize textarea
  if (contentInput) {
    contentInput.addEventListener('input', autoResizeTextarea);
    autoResizeTextarea.call(contentInput);
  }
})();


/* ═══════════════════════════════════════════════════════════════════════════
   Edit Note Form — edit_note.html
   ═══════════════════════════════════════════════════════════════════════════ */

(function initEditNoteForm() {
  const form = document.getElementById('editNoteForm');
  if (!form) return;

  const noteId       = parseInt(form.dataset.noteId, 10);
  const titleInput   = document.getElementById('noteTitle');
  const contentInput = document.getElementById('noteContent');
  const titleCounter = document.getElementById('titleCounter');
  const titleError   = document.getElementById('titleError');
  const contentError = document.getElementById('contentError');
  const updateBtn    = document.getElementById('updateBtn');
  const updatedAt    = document.getElementById('updatedAtDisplay');

  // Track original values to detect changes
  const originalTitle   = titleInput.value;
  const originalContent = contentInput.value;

  // ── Character counter ──
  if (titleInput && titleCounter) {
    titleInput.addEventListener('input', () => {
      const len = titleInput.value.length;
      const max = parseInt(titleInput.maxLength, 10) || 200;
      titleCounter.textContent = `${len} / ${max}`;
      titleCounter.className = 'char-counter' +
        (len >= max ? ' at-limit' : len >= max * 0.85 ? ' near-limit' : '');
    });
  }

  // ── Validation ──
  function validateTitle() {
    const val = titleInput.value.trim();
    if (!val) {
      showFieldError(titleInput, titleError, 'Title is required.');
      return false;
    }
    clearFieldError(titleInput, titleError);
    return true;
  }

  function validateContent() {
    const val = contentInput.value.trim();
    if (!val) {
      showFieldError(contentInput, contentError, 'Content cannot be empty.');
      return false;
    }
    clearFieldError(contentInput, contentError);
    return true;
  }

  function showFieldError(input, errorEl, message) {
    input.closest('.form-group').classList.add('has-error');
    errorEl.textContent = message;
    errorEl.hidden = false;
  }

  function clearFieldError(input, errorEl) {
    input.closest('.form-group').classList.remove('has-error');
    errorEl.hidden = true;
  }

  titleInput.addEventListener('blur', validateTitle);
  contentInput.addEventListener('blur', validateContent);
  titleInput.addEventListener('input', () => clearFieldError(titleInput, titleError));
  contentInput.addEventListener('input', () => clearFieldError(contentInput, contentError));

  // ── Submit ──
  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const titleOk   = validateTitle();
    const contentOk = validateContent();
    if (!titleOk || !contentOk) return;

    // Skip API call if nothing changed
    if (titleInput.value.trim() === originalTitle && contentInput.value.trim() === originalContent) {
      showToast('No changes to save.', 'info');
      return;
    }

    setButtonLoading(updateBtn, 'Updating…');

    try {
      const response = await fetch(`/api/notes/${noteId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title:   titleInput.value.trim(),
          content: contentInput.value.trim(),
        }),
      });
      const data = await response.json();

      if (data.success) {
        // Update the displayed timestamp
        if (updatedAt && data.note.updated_at) {
          updatedAt.textContent = data.note.updated_at;
          updatedAt.setAttribute('datetime', data.note.updated_at);
        }
        showToast('Note updated!', 'success', 1500);
        setTimeout(() => { window.location.href = '/'; }, 800);
      } else {
        showToast(data.error || 'Failed to update note.', 'error');
        restoreButton(updateBtn);
      }
    } catch (err) {
      console.error('[EditNote] Error:', err);
      showToast('Network error. Please try again.', 'error');
      restoreButton(updateBtn);
    }
  });

  // Auto-resize textarea
  if (contentInput) {
    contentInput.addEventListener('input', autoResizeTextarea);
    autoResizeTextarea.call(contentInput);
  }
})();


/* ═══════════════════════════════════════════════════════════════════════════
   Shared utility: auto-resize textarea
   ═══════════════════════════════════════════════════════════════════════════ */

/**
 * Auto-resize a textarea to fit its content.
 * Call with `this` bound to the textarea element.
 */
function autoResizeTextarea() {
  this.style.height = 'auto';
  this.style.height = Math.max(200, this.scrollHeight) + 'px';
}
