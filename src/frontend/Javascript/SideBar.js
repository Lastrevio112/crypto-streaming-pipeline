class SideBar extends HTMLElement {
  // Child classes will override this value (0, 1, 2, or 3)
  activeIndex = null;

  connectedCallback() {
    this.render();
  }

  render() {
    const links = [
      { href: "index.html", icon: "📈", label: "Price Evolution" },
      { href: "dashboard2.html", icon: "📊", label: "Volume Analysis" },
      { href: "dashboard3.html", icon: "⚡", label: "Signal Analysis" },
      { href: "dashboard4.html", icon: "⚖️", label: "Coin Comparison" }
    ];

    const header = `<span class="sidebar-section-label">Dashboards:</span>`;

    this.innerHTML = header + links.map((link, index) => `
      <a href="${link.href}" class="${this.activeIndex === index ? 'active' : ''}">
        <span class="icon">${link.icon}</span>
        <span class="label">${link.label}</span>
      </a>
    `).join('');
  }
}

class SideBarPrice extends SideBar { activeIndex = 0; }
class SideBarVolume extends SideBar { activeIndex = 1; }
class SideBarSignal extends SideBar { activeIndex = 2; }
class SideBarCompare extends SideBar { activeIndex = 3; }

// Register the custom elements
customElements.define('sidebar-price', SideBarPrice);
customElements.define('sidebar-volume', SideBarVolume);
customElements.define('sidebar-signal', SideBarSignal);
customElements.define('sidebar-compare', SideBarCompare);