class MessageLog {
  constructor() {
    this.sidebar  = document.getElementById('messagelog');
    this.dashboard = document.getElementById('dashboard');
    this.toggleBtn = document.getElementById('feed-toggle-btn');
    this.closeBtn  = document.getElementById('messagelog-close');
    this.feed      = document.getElementById('message-feed');
    this.isOpen    = false;
    this.autoScroll = true;

    this.toggleBtn.addEventListener('click', () => this.toggle());
    this.closeBtn.addEventListener('click',  () => this.close());

    // Pause auto-scroll when user manually scrolls up
    this.feed.addEventListener('scroll', () => {
      const { scrollTop, scrollHeight, clientHeight } = this.feed;
      this.autoScroll = scrollHeight - scrollTop - clientHeight < 40;
    });
  }

  open() {
    this.isOpen = true;
    this.sidebar.classList.add('open');
    this.dashboard.classList.add('feed-open');
    this.toggleBtn.classList.add('active');
  }

  close() {
    this.isOpen = false;
    this.sidebar.classList.remove('open');
    this.dashboard.classList.remove('feed-open');
    this.toggleBtn.classList.remove('active');
  }

  toggle() {
    this.isOpen ? this.close() : this.open();
  }

  // Call this to inject a message from your WebSocket handler
  // topic: string (e.g. 'trades', 'prices')
  // body:  string (the message content to display)
  addMessage(topic, body) {
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