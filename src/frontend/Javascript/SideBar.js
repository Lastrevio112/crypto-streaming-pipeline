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

    const gitHubRepoLink = "https://github.com/Lastrevio112/crypto-streaming-pipeline";

    const header = `<span class="sidebar-section-label">Dashboards:</span>`;

    // Wrapping dashboard links together
    const navLinks = links.map((link, index) => `
      <a href="${link.href}" class="${this.activeIndex === index ? 'active' : ''}">
        <span class="icon">${link.icon}</span>
        <span class="label">${link.label}</span>
      </a>
    `).join('');

    // Adding the GitHub link at the bottom using an SVG for perfect scaling and transparency
    const githubLink = `
      <a href=${gitHubRepoLink} target="_blank" class="github-link">
        <svg class="icon github-icon" viewBox="0 0 16 16" version="1.1" aria-hidden="true">
          <path fill="currentColor" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path>
        </svg>
        <span class="label">GitHub Repository</span>
      </a>
    `;

    // Combine them into the innerHTML
    this.innerHTML = `<div class="sidebar-nav">${header + navLinks}</div>` + githubLink;
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