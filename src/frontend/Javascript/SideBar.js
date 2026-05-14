class SideBar extends HTMLElement {
  connectedCallback() {
    this.innerHTML = `
        <a href="index.html" class="active"><span class="icon">📈</span><span class="label">Price Evolution</span></a>
        <a href="dashboard2.html"><span class="icon">📊</span><span class="label">Volume Analysis</span></a>
        <a href="dashboard3.html"><span class="icon">⚡</span><span class="label">Singal Analysis</span></a>
        <a href="dashboard4.html"><span class="icon">⚖️</span><span class="label">Coin Comparison</span></a>
    `;
  }
}
customElements.define('custom-sidebar', SideBar);