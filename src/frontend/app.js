document.getElementById('time-picker').addEventListener('change', function() {
  const from = this.value;
  const iframe = document.querySelector('iframe');
  const url = new URL(iframe.src);
  url.searchParams.set('from', from);
  url.searchParams.set('to', 'now');
  url.searchParams.set('kiosk', 'true');
  iframe.src = url.toString();
});