(function(query) {
  function appendInfo(row, cln, title, text) {
    const sel = `tr:nth-child(${row}) .result-title`;
    const mi = document.createElement('i');
    mi.className = `mi mi-${cln}`;
    mi.setAttribute('title', title);
    const div = document.createElement('div');
    div.className = 'result-info';
    div.appendChild(mi);
    div.innerHTML += text;
    document.querySelector(sel).appendChild(div);
  }

  function matchQuery(q) {
    if(q.matches) {
      document.querySelectorAll('td.s-hidden').forEach((elem, i) => {
        const n = (i / 6 >> 0) + 1;
        switch(elem.className) {
          case 'result-people s-hidden':
            appendInfo(n, 'people', 'Author/Artist', elem.innerHTML);
            break;
          case 'result-desc s-hidden':
            appendInfo(n, 'info', 'Description', elem.innerHTML);
            break;
          case 'result-categories s-hidden':
            appendInfo(n, 'tags', 'Categories', elem.innerHTML);
            break;
          case 'result-chapters s-hidden':
            appendInfo(n, 'pages', 'Chapters', elem.innerHTML);
            break;
          case 'result-views s-hidden':
            appendInfo(n, 'eye', 'Total Views', elem.innerHTML);
            break;
          case 'result-date s-hidden':
            appendInfo(n, 'clock', 'Last Update', elem.innerHTML);
            break;
        }
      });
    } else {
      document.querySelectorAll('.result-info').forEach(el => el.remove());
    }
  }

  function initialize() {
    const url = new URL(window.location);
    const form = document.getElementById('search-form');
    const table = document.getElementById('result-table');

    if(table && window.Tablesort) {
      new window.Tablesort(table);
      table.querySelector('th').removeAttribute('data-sort-default');
    }

    matchQuery(query);

    form['categories[]'].forEach(c => {c.indeterminate = true});
    (url.searchParams.get('categories') || '').split(',')
      .filter(e => e !== '').forEach(c => {
        c = c.trim().toLowerCase();
        const val = c[0] === '-' ? c.slice(1) : c;
        const input = Array.from(form['categories[]']).find(e => e.value === val);
        input.indeterminate = false;
        input.checked = c[0] !== '-';
      });
    form.elements[5].lastChild.addEventListener('click', evt => {
      let el = evt.target;
      if(el.tagName === 'I' || el.nodeType === 3)
        el = el.parentNode;
      if(el.className !== 'tooltip category') return;
      const [state, input] = el.children;
      switch(state.className) {
        case 'mi mi-circle':
          state.className = 'mi mi-ok-circle';
          input.indeterminate = false;
          input.checked = true;
          break;
        case 'mi mi-ok-circle':
          state.className = 'mi mi-x-circle';
          input.indeterminate = false;
          input.checked = false;
          break;
        case 'mi mi-x-circle':
          state.className = 'mi mi-circle';
          input.indeterminate = true;
          input.checked = false;
          break;
      }
    });

    form.addEventListener('submit', evt => {
      evt.preventDefault();
      evt.stopPropagation();
      form.categories.value = Array.from(form['categories[]'])
        .reduce((acc, cur) => {
          if(cur.indeterminate) return acc;
          if(acc !== '') acc += ',';
          if(!cur.checked) acc += '-';
          return acc + cur.value;
        }, '');
      Array.from(form.elements).slice(0, 5).concat(form.categories)
        .forEach(el => {el.disabled = !el.value});
      const search = form.action + '?' +
        new URLSearchParams(new FormData(form)).toString();
      const xhr = new XMLHttpRequest();
      xhr.open(form.method, search, true);
      xhr.onload = function() {
        if(this.status !== 200) {
          document.open();
          document.write(this.responseText);
          document.close();
          return;
        }
        const dom = new DOMParser()
          .parseFromString(this.responseText, 'text/html');
        document.getElementById('search').innerHTML =
          dom.getElementById('search').innerHTML;
        document.head.querySelector('meta[name="totalResults"]').outerHTML =
          dom.head.querySelector('meta[name="totalResults"]').outerHTML;
        document.head.querySelector('meta[name="url"]').outerHTML =
          dom.head.querySelector('meta[name="url"]').outerHTML;
        document.head.querySelector('meta[property="og:url"]').outerHTML =
          dom.head.querySelector('meta[property="og:url"]').outerHTML;
        history.replaceState({name: 'search'}, document.title, search);
        initialize();
      };
      xhr.onerror = function() {console.error(this.statusText)};
      xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
      xhr.send(null);
    });
  }

  window.addEventListener('load', initialize);
  query.addEventListener('change', matchQuery);
})(window.matchMedia('(max-width: 690px)'));
