// Only replace the introductory map once a real prediction image is loaded.
(async () => {
  try {
    const response = await fetch('assets/snow/latest.json', {cache: 'no-cache'});
    if (!response.ok) return;
    const data = await response.json();
    const image = new Image();
    image.alt = `Modeled North Cascades snow depth for ${data.target_date}, in meters`;
    image.src = `assets/snow/latest.png?v=${encodeURIComponent(data.generated_at)}`;
    await image.decode();
    const link = document.querySelector('.lead-map > a');
    link.href = image.src;
    link.replaceChildren(image);
    const caption = document.querySelector('.lead-map figcaption');
    caption.replaceChildren();
    const text = document.createElement('span');
    text.textContent = `North Cascades · Modeled snow depth · ${data.target_date}`;
    const methods = document.createElement('a');
    methods.href = '#snow-map';
    methods.textContent = 'About this map ↗';
    caption.append(text, methods);
    document.querySelector('#snow-status').textContent = `Latest prediction: ${data.target_date}. Snow-off reference: ${data.snow_off_date}.`;
  } catch (error) {
    // Keep the existing cartography visible when no successful map is available.
    console.info('Snow map is not available yet.');
  }
})();
