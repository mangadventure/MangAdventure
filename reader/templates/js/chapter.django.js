(function(img) {
  img.src = '{{ MEDIA_URL|urljoin:curr_page.image.url }}';
  img.alt = 'Page {{ curr_page.number }}';
  img.className = 'chapter-page';
  img.addEventListener('click', function() {
    {% if curr_page.number < all_pages.count %}
      location.pathname = location.pathname
        .replace(/[0-9]+\/$/, '{{ curr_page.number|add:1 }}/');
    {% elif next_chapter %}
      location.pathname = '{{ next_chapter.url }}';
    {% else %}
      location.pathname = '/reader/{{ curr_chapter.series.slug }}/';
    {% endif %}
  });
  img.addEventListener('load', function() {
    var ph = document.querySelector('.placeholder');
    var dd = document.getElementById('dropdowns');
    var ct = document.getElementById('controls');
    ph.parentNode.replaceChild(img, ph);
    dd.removeAttribute('style');
    ct.removeAttribute('style');
    var ci = document.querySelector('.curr-page input');
    ci.addEventListener('keyup', function(evt) {
      if(evt.keyCode !== 13) return;
      var n = Number(ci.value);
      if(!n || !Number.isInteger(n)) return;
      if(n === Number(ci.placeholder)) return;
      if(n > {{ curr_chapter.pages.count }}) return;
      location.pathname = location.pathname.replace(/[0-9]+\/$/, n);
    });
  });
})(new Image());

