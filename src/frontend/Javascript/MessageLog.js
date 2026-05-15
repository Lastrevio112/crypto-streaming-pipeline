class MessageLog {
  constructor() {
    this.sidebar  = document.getElementById('messagelog');
    this.dashboard = document.getElementById('dashboard');
    this.closeBtn  = document.getElementById('messagelog-close');
    this.feed      = document.getElementById('message-feed');
    
    this.toggleBtn = null; 
    this.isOpen    = false;
    this.autoScroll = true;

    // Handle close button click (statically present in HTML)
    if (this.closeBtn) {
      this.closeBtn.addEventListener('click', () => this.close());
    }

    // Pause auto-scroll when user manually scrolls up
    if (this.feed) {
      this.feed.addEventListener('scroll', () => {
        const { scrollTop, scrollHeight, clientHeight } = this.feed;
        this.autoScroll = scrollHeight - scrollTop - clientHeight < 40;
      });
    }

    // Watch the DOM dynamically to capture the button whenever it drops in
    this.observeTopbarInjections();
  }

  observeTopbarInjections() {
    // 1. Try to find it immediately (in case it already processed)
    this.bindToggleButton();

    if (this.toggleBtn) return;

    // 2. Otherwise, watch #topbar for when the Custom Elements complete render
    const topbarContainer = document.getElementById('topbar');
    if (!topbarContainer) return;

    const observer = new MutationObserver((mutations, obs) => {
      this.bindToggleButton();
      if (this.toggleBtn) {
        obs.disconnect(); // Stop watching once found and bound
      }
    });

    observer.observe(topbarContainer, {
      childList: true,
      subtree: true
    });
  }

  bindToggleButton() {
    this.toggleBtn = document.getElementById('feed-toggle-btn');
    if (this.toggleBtn && !this.toggleBtn.dataset.bound) {
      this.toggleBtn.addEventListener('click', () => this.toggle());
      this.toggleBtn.dataset.bound = "true"; // Flag to prevent double binding

      // If the sidebar happens to already be open, sync button UI state
      if (this.isOpen) {
        this.toggleBtn.classList.add('active');
      }
    }
  }

  open() {
    this.isOpen = true;
    if (this.sidebar) this.sidebar.classList.add('open');
    if (this.dashboard) this.dashboard.classList.add('feed-open');
    if (this.toggleBtn) this.toggleBtn.classList.add('active');
  }

  close() {
    this.isOpen = false;
    if (this.sidebar) this.sidebar.classList.remove('open');
    if (this.dashboard) this.dashboard.classList.remove('feed-open');
    if (this.toggleBtn) this.toggleBtn.classList.remove('active');
  }

  toggle() {
    this.isOpen ? this.close() : this.open();
  }

  addMessage(topic, body) {
    if (!this.feed) return;

    const now = new Date();
    const time = now.toLocaleTimeString('en-GB', { hour12: false });

    const topicClass = `topic-${topic.toLowerCase().replace(/[^a-z0-9]/g, '-')}` ;
    const knownTopics = ['trades', 'prices'];
    const badgeClass  = knownTopics.includes(topic.toLowerCase())
      ? topicClass
      : 'topic-default';

    const el = document.createElement('div');
    el.className = 'feed-message';
    el.innerHTML = `
      <div class="feed-message-meta">
        <span class="feed-topic-badge ${badgeClass}">${topic}</span>
        <span class="feed-message-time">${time}</span>
      </div>
      <div class="feed-message-body">${this.escapeHtml(body)}</div>
    `;

    this.feed.appendChild(el);

    if (this.autoScroll) {
      this.feed.scrollTop = this.feed.scrollHeight;
    }
  }

  escapeHtml(str) {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }
}

const messageLog = new MessageLog();