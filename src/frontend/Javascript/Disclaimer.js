class Disclaimer extends HTMLElement {
  connectedCallback() {
    this.innerHTML = `
        <div class="disclaimer">
          <p>Disclaimer: All the data from this dashboard comes from the Binance and MEXC websocket APIs.</p>
          <p>Therefore, the metrics displayed here reflect only the aggregate data of those two trading platforms and may or may not be indicative of the entire market.</p>
        </div>
    `;
  }
}
customElements.define('custom-disclaimer', Disclaimer);