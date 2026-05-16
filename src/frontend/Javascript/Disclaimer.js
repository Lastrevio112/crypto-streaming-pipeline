class Disclaimer extends HTMLElement {
  connectedCallback() {
    this.innerHTML = `
        <div class="disclaimer">
          <p>Disclaimer: All the data from this dashboard comes from the Binance and MEXC websocket APIs.</p>
          <p>Therefore, the metrics displayed here reflect only the aggregate data of those two trading platforms and may or may not be indicative of the entire market.</p>
          <p>Disclaimer 2: If you see that data is missing from a graph in an interval of one or more hours, it means there was a server outage.</p>
          <p>Remember that this is only a hobby/portofolio project, so take all the data from here with a grain of salt.</p>
        </div>
    `;
  }
}
customElements.define('custom-disclaimer', Disclaimer);