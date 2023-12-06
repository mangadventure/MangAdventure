(function(buttons) {
  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      const xhr = new XMLHttpRequest();
      const data = new FormData();
      data.append('series', btn.dataset.series);
      xhr.open('POST', btn.dataset.target, true);
      xhr.setRequestHeader('X-CSRFToken', btn.dataset.token);
      xhr.onload = function() {
        switch (xhr.status) {
          case 201:
            if ('umami' in window)
              window.umami.track('Bookmark', {url: location.href});
            btn.className = 'mi mi-bookmark bookmark-btn';
            break;
          case 204:
            btn.className = 'mi mi-bookmark-o bookmark-btn';
            break;
          default:
            console.error(xhr.statusText);
        }
      };
      xhr.send(data);
    });
  });
})(document.querySelectorAll('.bookmark-btn'));
