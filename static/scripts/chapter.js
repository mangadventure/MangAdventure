(function(ph) {
  const changePage = (rel) =>
    document.querySelector(`.control[rel="${rel}"]`).href;

  const img = ph.nextElementSibling;

  if (img.complete) ph.remove();
  else img.addEventListener('load', () => ph.remove(), true);

  img.addEventListener('click', function(evt) {
    const width = this.offsetWidth;
    const coord = evt.clientX - this.getBoundingClientRect().left;
    location.href = changePage(coord < width / 2 ? 'prev' : 'next');
  });

  window.addEventListener('DOMContentLoaded', () => {
    document.getElementById('dropdowns').removeAttribute('class');
    document.getElementById('controls').removeAttribute('class');
    document.querySelector('.curr-page input')
      .addEventListener('keyup', function(evt) {
        if (evt.code !== 'Enter') return;
        const n = Number(this.value);
        if (!n || !Number.isInteger(n)) return;
        if (n === Number(this.placeholder)) return;
        if (n > Number(this.dataset.max)) return;
        if (n > 0) location.href = `../${n}/`;
      });
  });

  document.body.addEventListener('keyup', evt => {
    switch (evt.code) {
      case 'ArrowLeft':
        location.href = changePage('prev');
        break;
      case 'ArrowRight':
        location.href = changePage('next');
        break;
      default:
        return;
    }
  });
})(document.getElementById('placeholder'));
