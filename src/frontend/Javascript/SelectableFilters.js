// Helper to convert strings like 'now-4h' or '30m' into raw minutes
const timeToMinutes = (str) => {
  const num = parseInt(str.replace(/\D/g, ''));
  if (str.includes('h')) return num * 60;
  if (str.includes('d')) return num * 1440;
  if (str.includes('s')) return num / 60;
  return num; // default to minutes
};

// Global State management to track current selections
const FilterState = {
  currentTimeRange: 'now-15m',
  currentCandleSize: '30s',
  currentCoin: 'BTCUSDT',
  currentCoin2: 'ETHUSDT',
  currentSlidingWindow: '1m (5s hop)'
};


// Function to validate the candle size selection based on the current value of the time selection.
// We implement this to make sure that for large time selection, we don't select very small candle sizes that will make the app slow (ex: 24h time with 1s candle is a horrible combination).
const validateCandleSize = (timeRange, candleSize) => {
  const timeMins = timeToMinutes(timeRange);
  const candleMins = timeToMinutes(candleSize);

  // 7 days (10080m) -> 30m candle
  if (timeMins >= 10080 && candleMins < 30) 
    return false;

  // 2 days (2880m) -> 5m candle
  if (timeMins >= 2880 && candleMins < 5) 
    return false;

  // 24h (1440m) -> 1m candle
  if (timeMins >= 1440 && candleMins < 1) 
    return false;

  // 12h (720m) -> 5m candle
  if (timeMins >= 720 && candleMins < 5)
    return false;

  // 4h (240m) -> 1m candle
  if (timeMins >= 240 && candleMins < 1)
    return false;

  // 30m -> 30s (0.5m) candle
  if (timeMins >= 30 && candleMins < 0.5) 
    return false;

  return true;
}

const validateSlidingWindow = (timeRange, slidingWindowSize) => {
  const timeMins = timeToMinutes(timeRange);
  const windowSeconds = { '1s': 5, '30s': 60, '1m': 300 }[slidingWindowSize] ?? 0;

  console.log("timeMins: ", timeMins, "windowSeconds: ", windowSeconds)

  // 12h (720m) -> 5m sliding window
  if (timeMins >= 720 && windowSeconds < 300){
    //console.log("rule 1")
    return false;
  }

  // 30m -> 1m sliding window
  if (timeMins >= 60 && windowSeconds < 60){
    //console.log("rule 2")
    return false;
  }
      
  return true;
}



class SelectableFilter {
  constructor(config) {
    // Select elements based on the IDs/Classes passed in
    this.selectedEl = document.getElementById(config.selectedId);
    this.optionsContainer = document.getElementById(config.optionsId);
    this.optionClassName = config.optionClassName;
    this.pickerEl = document.getElementById(config.pickerId);
    this.errorPopup = this.createErrorPopup();

    this.init();
  }

  init() {
    if (!this.selectedEl) return;

    // Toggle dropdown
    this.selectedEl.addEventListener('click', () => {
      this.optionsContainer.classList.toggle('open');
    });

    // Handle option selection
    this.optionsContainer.querySelectorAll(`.${this.optionClassName}`).forEach(option => {
      option.addEventListener('click', (e) => {
        const value = option.dataset.value;
        const label = option.textContent;

        const isValid = this.updateLogic(value); // subclasses return true/false if the attempted selection is valid
        if (isValid) 
          this.updateUI(option, label);
      });
    });

    // Close when clicking outside
    document.addEventListener('click', (e) => {
      if (this.pickerEl && !this.pickerEl.contains(e.target)) {
        this.optionsContainer.classList.remove('open');
      }
    });
  }

  createErrorPopup() {
    // Inject keyframe animation once
    const popup = document.createElement('div');
    popup.id = 'candle-error-popup';
    popup.innerHTML = `
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
        <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
      </svg>
      <span>Candle size too small for this time range</span>
    `;
    document.body.appendChild(popup);
    return popup;
  }

  updateUI(selectedOption, label) {
    this.selectedEl.textContent = label + ' ▾';
    
    // Remove active class from siblings and add to current
    this.optionsContainer.querySelectorAll(`.${this.optionClassName}`)
      .forEach(o => o.classList.remove('active'));
    selectedOption.classList.add('active');
    
    // Close menu
    this.optionsContainer.classList.remove('open');
  }

  // Placeholder to be overwritten by child classes
  updateLogic(value) {
    console.warn("updateLogic() not implemented for this filter.");
  }
}



class TimeSelector extends SelectableFilter {
  constructor() {
    super({
      selectedId: 'time-selected',
      optionsId: 'time-options',
      optionClassName: 'time-option',
      pickerId: 'time-picker'
    });
  }

  // Overriding the parent logic to update IFrame URL based on time selection:
  updateLogic(value) {
    const hasCandlePicker = !!document.getElementById('candlesize-selected');
    const hasSlidingPicker = !!document.getElementById('sliding-selected');

    const isValid = hasCandlePicker
      ? validateCandleSize(value, FilterState.currentCandleSize)
      : validateSlidingWindow(value, FilterState.currentSlidingWindow);

    if (!isValid) {
      this.errorPopup.classList.add('visible');
      return false;
    }

    // If valid, hide popup and update iframes
    this.errorPopup.classList.remove('visible');
    FilterState.currentTimeRange = value; 

    document.querySelectorAll('iframe').forEach(iframe => {
      const url = new URL(iframe.src);
      url.searchParams.set('from', value);
      url.searchParams.set('to', 'now');
      url.searchParams.set('kiosk', 'true');
      iframe.src = url.toString();
    });

    return true;
  }
}


class CandleSizeSelector extends SelectableFilter {
  constructor() {
    super({
      selectedId: 'candlesize-selected',
      optionsId: 'candlesize-options',
      optionClassName: 'candlesize-option',
      pickerId: 'candlesize-picker'
    });
  }

  updateLogic(value) {
    if (!validateCandleSize(FilterState.currentTimeRange, value)) {
      this.errorPopup.classList.add('visible');
      return false; // Stop the update
    }

    // If valid, hide popup and update iframes
    this.errorPopup.classList.remove('visible');
    FilterState.currentCandleSize = value;

    document.querySelectorAll('iframe').forEach(iframe => {
      const url = new URL(iframe.src);
      url.searchParams.set('var-candle_interval', value);
      iframe.src = url.toString();
    });

    return true;
  }
}


class CoinSelector extends SelectableFilter {
  constructor() {
    super({
      selectedId: 'coin-selected',
      optionsId: 'coin-options',
      optionClassName: 'coin-option',
      pickerId: 'coin-picker'
    });

    // Scroll to active coin when dropdown opens
    this.selectedEl.addEventListener('click', () => {
      const active = this.optionsContainer.querySelector('.coin-option.active');
      if (active) active.scrollIntoView({ block: 'center' });
    });
  }

  updateLogic(value) {
    FilterState.currentCoin = value;

    document.querySelectorAll('iframe').forEach(iframe => {
      const url = new URL(iframe.src);
      url.searchParams.set('var-coin_symbol', value);
      iframe.src = url.toString();
    });

    return true;
  }
}


class Coin2Selector extends SelectableFilter {
  constructor() {
    super({
      selectedId: 'coin2-selected',
      optionsId: 'coin2-options',
      optionClassName: 'coin2-option',
      pickerId: 'coin2-picker'
    });

    this.selectedEl.addEventListener('click', () => {
      const active = this.optionsContainer.querySelector('.coin2-option.active');
      if (active) active.scrollIntoView({ block: 'center' });
    });
  }

  updateLogic(value) {
    FilterState.currentCoin2 = value;
    document.querySelectorAll('iframe').forEach(iframe => {
      const url = new URL(iframe.src);
      url.searchParams.set('var-coin_symbol_2', value);
      iframe.src = url.toString();
    });
    return true;
  }
}


class SlidingWindowFilter extends SelectableFilter{
  constructor() {
    super({
      selectedId: 'sliding-selected',
      optionsId: 'sliding-options',
      optionClassName: 'sliding-option',
      pickerId: 'sliding-picker'
    });

    this.selectedEl.addEventListener('click', () => {
      const active = this.optionsContainer.querySelector('.sliding-option.active');
      if (active) active.scrollIntoView({ block: 'center' });
    });
  }

  updateLogic(value) {
    if (!validateSlidingWindow(FilterState.currentTimeRange, value)) {
      this.errorPopup.classList.add('visible');
      return false; // Stop the update
    }

    // If valid, hide popup and update iframes
    this.errorPopup.classList.remove('visible');
    FilterState.currentSlidingWindow = value;

    const grafanaValueMap = {
      '1s':  'analytics_5s_sliding',
      '30s': 'analytics_1m_sliding',
      '1m':  'analytics_5m_sliding',
    };

    const grafanaValue = grafanaValueMap[value] ?? value;

    document.querySelectorAll('iframe').forEach(iframe => {
      const url = new URL(iframe.src);
      url.searchParams.set('var-sliding_window', grafanaValue);
      iframe.src = url.toString();
    });

    return true;
  }
}


// Initialize each class:
if (document.getElementById('time-selected'))       new TimeSelector();
if (document.getElementById('candlesize-selected')) new CandleSizeSelector();
if (document.getElementById('coin-selected'))       new CoinSelector();
if (document.getElementById('coin2-selected'))      new Coin2Selector();
if (document.getElementById('sliding-selected'))    new SlidingWindowFilter();