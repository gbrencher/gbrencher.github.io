// Keep the existing cartography feature until a complete snow map is available.
(async () => {
  try {
    const response = await fetch('assets/snow/latest.json', {cache: 'no-cache'});
    if (!response.ok) return;
    const data = await response.json();
    const image = new Image();
    image.src = `assets/snow/latest.png?v=${encodeURIComponent(data.generated_at)}`;
    await image.decode();
    image.alt = `Predicted snow depth in the North Cascades for ${data.target_date}`;
    image.width = image.naturalWidth;
    image.height = image.naturalHeight;
    const feature = document.querySelector('.lead-map');
    const link = feature.querySelector('a');
    link.href = image.src;
    link.replaceChildren(image);
    const caption = feature.querySelector('figcaption');
    caption.replaceChildren();
    const label = document.createElement('span');
    const age = (Date.now() - Date.parse(data.generated_at)) / 86400000;
    label.textContent = `North Cascades · Snow depth estimate for ${data.target_date}${age > 2 ? ' · Last available update' : ''}. Satellite acquisition dates vary.`;
    const source = document.createElement('a');
    source.href = 'https://github.com/geo-smart/deep-snow';
    source.textContent = 'deep-snow ↗';
    caption.append(label, source);
  } catch (error) {
    console.info('Snow map unavailable; showing cartography.');
  }
})();
