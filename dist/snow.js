(async () => {
  try {
    const response = await fetch('assets/snow/latest.json', {cache:'no-cache'});
    if (!response.ok) return;
    const d = await response.json();
    const image = new Image();
    image.src = `assets/snow/latest.png?v=${encodeURIComponent(d.generated_at)}`;
    image.alt = `deep-snow predicted snow depth in the North Cascades for ${d.target_date}, in metres`;
    await image.decode();
    const figure = document.querySelector('.lead-map');
    function el(tag, cls, text) {
      const node = document.createElement(tag); node.className = cls;
      if (text) node.textContent = text; return node;
    }
    let historical = null;
    let showingHistorical = false;
    function show(d, image) {
    const link = el('a',''); link.href = image.src; link.append(image);
    const caption = el('figcaption','');
    const methods = el('a','', 'About this map ↗'); methods.href = '#snow-map';
    if (d.presentation_version !== 2) {
      caption.append(el('span','',`North Cascades · deep-snow predicted snow depth · ${d.target_date}`), methods);
      figure.replaceChildren(link, caption); return;
    }
    image.width = d.width; image.height = d.height;
    const heading = el('div','snow-heading');
    const date = el('time','',d.target_date); date.dateTime = d.target_date;
    heading.append(el('span','','North Cascades snow depth'),date);
    const frame = el('div','snow-frame');
    const scale = el('span','snow-scale',`${(d.scale_metres || 20000)/1000} km`); scale.style.width = `${d.scale_fraction*100}%`;
    frame.append(link,scale,el('span','snow-north','N ↑'));
    const legend = el('div','snow-legend');
    legend.setAttribute('aria-label','Snow depth in metres: 0 to 5 or more; grey means no data');
    const ramp = el('div','snow-ramp');
    const gradient = el('div','snow-gradient'); gradient.style.background = `linear-gradient(to right, ${d.legend_colors.join(',')})`;
    const ticks = el('div','snow-ticks');
    for (const t of ['0','1','2','3','4','5+ m']) ticks.append(el('span','',t));
    ramp.append(gradient,ticks); legend.append(el('span','','deep-snow predicted snow depth'),ramp);
    const actions = el('div','snow-actions');
    actions.append(methods);
    if (historical) {
      const toggle = el('button','snow-toggle', showingHistorical ? 'See latest snow depth' : 'See previous April 1 snow depth');
      toggle.type = 'button';
      toggle.setAttribute('aria-pressed', String(showingHistorical));
      toggle.addEventListener('click', () => {
        showingHistorical = !showingHistorical;
        const next = showingHistorical ? historical : {d: latestData, image: latestImage};
        show(next.d, next.image);
        figure.querySelector('.snow-toggle').focus({preventScroll:true});
      });
      actions.append(toggle);
    }
    caption.append(legend,actions);
    figure.classList.add('snow-figure'); figure.replaceChildren(heading,frame,caption);
    }
    const latestData = d, latestImage = image;
    show(d, image);
    try {
      const archive = await fetch('assets/snow/april-2026/latest.json', {cache:'no-cache'});
      if (!archive.ok) return;
      const historicData = await archive.json();
      if (historicData.target_date !== '2026-04-01' || historicData.presentation_version !== 2) return;
      const historicImage = new Image();
      historicImage.src = `assets/snow/april-2026/latest.png?v=${encodeURIComponent(historicData.generated_at)}`;
      historicImage.alt = `deep-snow predicted snow depth in the North Cascades for ${historicData.target_date}, in metres`;
      await historicImage.decode();
      historical = {d: historicData, image: historicImage};
      show(d, image);
    } catch { console.info('April 1 map not yet available; retaining latest map.'); }
  } catch { console.info('Snow map unavailable; retaining cartography.'); }
})();
