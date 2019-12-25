(function(buttons) {
  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      const xhr = new XMLHttpRequest();
      xhr.open('POST', btn.getAttribute('data-target'), true);
      xhr.setRequestHeader('Content-Type',
        'application/x-www-form-urlencoded; charset=UTF-8');
      xhr.setRequestHeader('X-CSRFToken',
        document.querySelector('meta[name="csrf-token"]').content);
      xhr.onload = function() {
        switch(xhr.status) {
          case 201: btn.className = 'mi mi-bookmark bookmark-btn'; break;
          case 204: btn.className = 'mi mi-bookmark-o bookmark-btn'; break;
          default: console.error(xhr.statusText);
        }
      };
      xhr.send(`series=${btn.getAttribute('data-series')}`);
    });
  });
})(document.querySelectorAll('.bookmark-btn'));
