class TopBar extends HTMLElement {
  connectedCallback() {
    this.innerHTML = `
      <div class="filter-group">
      <span class="filter-label">Time Range:</span>
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
      </div>

      <div class="filter-group">
      <span class="filter-label">Candle Size:</span>
        <div id="candlesize-picker">
          <div id="candlesize-selected">30s ▾</div>
          <div id="candlesize-options">
            <div class="candlesize-option" data-value="1s">1 second</div>
            <div class="candlesize-option active" data-value="30s">30 seconds</div>
            <div class="candlesize-option" data-value="1m">1 minute</div>
            <div class="candlesize-option" data-value="5m">5 minutes</div>
            <div class="candlesize-option" data-value="30m">30 minutes</div>
            <div class="candlesize-option" data-value="1h">1 hour</div>
            <div class="candlesize-option" data-value="4h">4 hours</div>
            <div class="candlesize-option" data-value="24h">24 hours</div>
          </div>
        </div>
      </div>
    `;
  }
}
customElements.define('custom-topbar', TopBar);