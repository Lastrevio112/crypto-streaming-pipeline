class SelectableFilter {
  constructor(config) {
    // Select elements based on the IDs/Classes passed in
    this.selectedEl = document.getElementById(config.selectedId);
    this.optionsContainer = document.getElementById(config.optionsId);
    this.optionClassName = config.optionClassName;
    this.pickerEl = document.getElementById(config.pickerId);

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

        this.updateUI(option, label);
        this.updateLogic(value); // This is what the child class will override
      });
    });

    // Close when clicking outside
    document.addEventListener('click', (e) => {
      if (this.pickerEl && !this.pickerEl.contains(e.target)) {
        this.optionsContainer.classList.remove('open');
      }
    });
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

  // Overriding the parent logic to handle iframe URL updates
  updateLogic(value) {
    document.querySelectorAll('iframe').forEach(iframe => {
      const url = new URL(iframe.src);
      url.searchParams.set('from', value);
      url.searchParams.set('to', 'now');
      url.searchParams.set('kiosk', 'true');
      iframe.src = url.toString();
    });
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
    document.querySelectorAll('iframe').forEach(iframe => {
      const url = new URL(iframe.src);
      url.searchParams.set('var-candle_interval', value);
      iframe.src = url.toString();
    });
  }
}


// Initialize each class:
new TimeSelector();
new CandleSizeSelector();