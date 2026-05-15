class MessageLog {
  constructor() {
    this.sidebar  = document.getElementById('messagelog');
    this.dashboard = document.getElementById('dashboard');
    this.closeBtn  = document.getElementById('messagelog-close');
    this.feed      = document.getElementById('message-feed');
    
    // These will be assigned inside initEventListeners()
    this.toggleBtn = null; 
    this.isOpen    = false;
    this.autoScroll = true;

    // Handle close button click (which is static in HTML)
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

    // Wait for custom elements to mount, then bind the dynamic toggle button
    window.addEventListener('DOMContentLoaded', () => {
      this.initEventListeners();
    });
  }

  initEventListeners() {
    this.toggleBtn = document.getElementById('feed-toggle-btn');
    if (this.toggleBtn) {
      this.toggleBtn.addEventListener('click', () => this.toggle());
    } else {
      console.warn("Feed toggle button not found in DOM yet. Retrying shortly...");
      // Fail-safe fallback if DOMContentLoaded fires too early for custom component parsing
      setTimeout(() => {
        this.toggleBtn = document.getElementById('feed-toggle-btn');
        if (this.toggleBtn) this.toggleBtn.addEventListener('click', () => this.toggle());
      }, 200);
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