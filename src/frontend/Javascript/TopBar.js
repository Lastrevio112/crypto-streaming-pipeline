class TopBar extends HTMLElement {
  connectedCallback() {
    this.innerHTML = `
      <div id="time-picker">
        <div id="time-selected">Last 15 minutes ▾</div>
        <div id="time-options">
          <div class="time-option" data-value="now-5m">Last 5 minutes</div>
          <div class="time-option active" data-value="now-15m">Last 15 minutes</div>
          <div class="time-option" data-value="now-30m">Last 30 minutes</div>
          <div class="time-option" data-value="now-1h">Last 1 hour</div>
          <div class="time-option" data-value="now-4h">Last 4 hours</div>
          <div class="time-option" data-value="now-12h">Last 12 hours</div>
          <div class="time-option" data-value="now-24h">Last 24 hours</div>
          <div class="time-option" data-value="now-2d">Last 2 days</div>
          <div class="time-option" data-value="now-7d">Last 7 days</div>
          <div class="time-option" data-value="now-14d">Last 14 days</div>
        </div>
      </div>
    `;
  }
}
customElements.define('custom-topbar', TopBar);