(function(img, ph) {
  function changePage(change) {
    const url = img.getAttribute(`data-${change}`);
    if(url) return url;
    const diff = (change === 'next') ? 1 : -1;
    return location.pathname.replace(
      /(\d+)\/$/, (m, n) => `${Number(n) + diff}/`
    );
  }


  img.src = ph.getAttribute('data-img');
  img.alt = `Page ${ph.getAttribute('data-num')}`;
  img.className = 'chapter-page';
  img.setAttribute('data-next', ph.getAttribute('data-next') || '');
  img.setAttribute('data-prev', ph.getAttribute('data-prev') || '');
  img.addEventListener('click', () => {
    location.pathname = changePage('next');
  });
  img.addEventListener('load', () => {
    const dd = document.getElementById('dropdowns');
    const ct = document.getElementById('controls');
    ph.parentNode.replaceChild(img, ph);
    dd.removeAttribute('class');
    ct.removeAttribute('class');
    const ci = document.querySelector('.curr-page input');
    ci.addEventListener('keyup', evt => {
      if(evt.keyCode !== 13) return;
      const n = Number(ci.value);
      if(!n || !Number.isInteger(n)) return;
      if(n === Number(ci.placeholder)) return;
      if(n > Number(ci.getAttribute('data-max'))) return;
      location.pathname = location.pathname.replace(/\d+\/$/, `${n}/`);
    });
  });
  document.body.addEventListener('keyup', (evt) => {
    switch(evt.keyCode) {
      case 37: location.pathname = changePage('prev'); break;
      case 39: location.pathname = changePage('next'); break;
      default: return;
    }
  });
})(new Image(), document.getElementById('placeholder'));
