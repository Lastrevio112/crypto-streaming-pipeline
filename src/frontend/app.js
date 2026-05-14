const selected = document.getElementById('time-selected');
const options = document.getElementById('time-options');

selected.addEventListener('click', function() {
  options.classList.toggle('open');
});

document.querySelectorAll('.time-option').forEach(function(option) {
  option.addEventListener('click', function() {
    const from = this.dataset.value;
    const label = this.textContent;

    selected.textContent = label + ' ▾';

    document.querySelectorAll('.time-option').forEach(o => o.classList.remove('active'));
    this.classList.add('active');

    options.classList.remove('open');

    const iframe = document.querySelector('iframe');
    const url = new URL(iframe.src);
    url.searchParams.set('from', from);
    url.searchParams.set('to', 'now');
    url.searchParams.set('kiosk', 'true');
    iframe.src = url.toString();
  });
});

document.addEventListener('click', function(e) {
  if (!document.getElementById('time-picker').contains(e.target)) {
    options.classList.remove('open');
  }
});