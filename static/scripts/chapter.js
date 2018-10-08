(function(img, ph) {
  function changePage(change) {
    var url = img.getAttribute('data-' + change);
    if(url) return url;
    var diff = (change === 'next') ? 1 : -1;
    return location.pathname.replace(/(\d+)\/$/,
      function(m, n) { return (Number(n) + diff) + '/' });
  }


  img.src = ph.getAttribute('data-img');
  img.alt = 'Page ' + ph.getAttribute('data-num');
  img.className = 'chapter-page';
  img.setAttribute('data-next', ph.getAttribute('data-next') || '');
  img.setAttribute('data-prev', ph.getAttribute('data-prev') || '');
  img.addEventListener('click', function() {
    location.pathname = changePage('next');
  });
  img.addEventListener('load', function() {
    var dd = document.getElementById('dropdowns');
    var ct = document.getElementById('controls');
    ph.parentNode.replaceChild(img, ph);
    dd.removeAttribute('class');
    ct.removeAttribute('class');
    var ci = document.querySelector('.curr-page input');
    ci.addEventListener('keyup', function(evt) {
      if(evt.keyCode !== 13) return;
      var n = Number(ci.value);
      if(!n || !Number.isInteger(n)) return;
      if(n === Number(ci.placeholder)) return;
      if(n > Number(ci.getAttribute('data-max'))) return;
      location.pathname = location.pathname.replace(/\d+\/$/, n + '/');
    });
  });
  document.body.addEventListener('keyup', function(evt) {
    switch(evt.keyCode) {
      case 37:
        location.pathname = changePage('prev');
        break;
      case 39:
        location.pathname = changePage('prev');
        break;
      default:
        return;
    }
  });
})(new Image(), document.getElementById('placeholder'));

