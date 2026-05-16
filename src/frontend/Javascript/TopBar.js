const COINS = [
  'AAVEUSDT','ADAUSDT','ARBUSDT','ASTERUSDT','AVAXUSDT','BABYUSDT',
  'BANANAS31USDT','BIOUSDT','BNBUSDT','BTCUSDT','CHIPUSDT','DASHUSDT',
  'DOGEUSDT','ENAUSDT','ETHUSDT','EURUSDT','FDUSDUSDT','FETUSDT',
  'GIGGLEUSDT','LINKUSDT','LTCUSDT','LUNCUSDT','MEGAUSDT','ONDOUSDT',
  'OPENUSDT','ORCAUSDT','ORDIUSDT','PARTIUSDT','PAXGUSDT','PENGUUSDT',
  'PEPEUSDT','RLUSDUSDT','SOLUSDT','SUIUSDT','TAOUSDT','TONUSDT',
  'TRXUSDT','TSTUSDT','UNIUSDT','WLFIUSDT','XAUTUSDT','XRPUSDT',
  'XVGUSDT','ZECUSDT','ZENUSDT','ZKUSDT'
];

const DEFAULT_COIN = 'BTCUSDT';
const DEFAULT_COIN2 = 'ETHUSDT';

const coinOptions = COINS.map(coin =>
      `<div class="coin-option${coin === DEFAULT_COIN ? ' active' : ''}" data-value="${coin}">${coin}</div>`
    ).join('');

const coinOptions2 = COINS.map(coin =>
  `<div class="coin2-option${coin === DEFAULT_COIN2 ? ' active' : ''}" data-value="${coin}">${coin}</div>`
).join('');


const TIME_RANGE_FILTER_HTML = `
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
    </div>`

const CANDLE_SIZE_FILTER_HTML = `
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
`

const SLIDING_WINDOW_FILTER_HTML = `
      <div class="filter-group">
        <span class="filter-label">Sliding Window:</span>
          <div id="sliding-picker">
            <div id="sliding-selected">1m (5s hop) ▾</div>
            <div id="sliding-options">
              <div class="sliding-option" data-value="1s">5s (1s hop)</div>
              <div class="sliding-option active" data-value="30s">1m (5s hop)</div>
              <div class="sliding-option" data-value="1m">5m (30s hop)</div>
            </div>
          </div>
      </div>
`


class TopBar extends HTMLElement {
  connectedCallback() {
    this.innerHTML = `
      ${TIME_RANGE_FILTER_HTML}

      ${CANDLE_SIZE_FILTER_HTML}

      <div class="filter-group">
        <span class="filter-label">Coin:</span>
        <div id="coin-picker">
          <div id="coin-selected">BTCUSDT ▾</div>
          <div id="coin-options">
            ${coinOptions}
          </div>
        </div>
      </div>
    `;
  }
}
customElements.define('custom-topbar', TopBar);


class TopBar_forSlidingWindows extends HTMLElement{
  connectedCallback() {
    this.innerHTML = `
      ${TIME_RANGE_FILTER_HTML}

      ${SLIDING_WINDOW_FILTER_HTML}

      <div class="filter-group">
        <span class="filter-label">Coin:</span>
        <div id="coin-picker">
          <div id="coin-selected">BTCUSDT ▾</div>
          <div id="coin-options">
            ${coinOptions}
          </div>
        </div>
      </div>
    `;
  }
}
customElements.define('custom-topbar-sliding-windows', TopBar_forSlidingWindows);

class TopBar_forTwoCoinSelectors extends HTMLElement{
  connectedCallback() {
    this.innerHTML = `
      ${TIME_RANGE_FILTER_HTML}

      ${CANDLE_SIZE_FILTER_HTML}

      <div class="filter-group">
        <span class="filter-label">Coin 1:</span>
        <div id="coin-picker">
          <div id="coin-selected">BTCUSDT ▾</div>
          <div id="coin-options">
            ${coinOptions}
          </div>
        </div>
      </div>

      <div class="filter-group">
        <span class="filter-label">Coin 2:</span>
        <div id="coin2-picker">
          <div id="coin2-selected">ETHUSDT ▾</div>
          <div id="coin2-options">
            ${coinOptions2}
          </div>
        </div>
      </div>
    `;
  }
}
customElements.define('custom-topbar-two-coins', TopBar_forTwoCoinSelectors);

