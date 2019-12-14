/* global Tablesort */

(function(form, url) {
  const getSearchParam = param => url.searchParams.get(param) || '';

  const regFilter = (arr, reg) => arr.filter(e => !reg.test(e));

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

  function matchQuery(query) {
    if(query.matches) {
      document.querySelectorAll('td.s-hidden').forEach((elem, i) => {
        const n = Math.floor(i / 5) + 1;
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
          case 'result-date s-hidden':
            appendInfo(n, 'clock', 'Last Update', elem.innerHTML);
            break;
        }
      });
    } else {
      document.querySelectorAll('.result-info').forEach(elem => {
        elem.parentElement.removeChild(elem);
      });
    }
  }

  const query = window.matchMedia('(max-width: 690px)');
  matchQuery(query);
  query.addListener(matchQuery);

  const table = document.getElementById('result-table');
  if(table) {
    new Tablesort(table);
    table.querySelector('th').removeAttribute('data-sort-default');
  }

  const categ = document.getElementById('category-container');
  let values = getSearchParam('categories')
    .split(',').filter(e => e !== '');
  categ.addEventListener('click', evt => {
    let el = evt.target;
    if(el.tagName === 'I' || el.nodeType === 3)
      el = el.parentNode;
    if(el.className !== 'tooltip category') return;
    const state = el.children[0];
    const text = el.textContent.trim().toLowerCase();
    const reg = new RegExp('-?' + text.replace(
      /[-\/\\^$*+?.()|[\]{}]/g, '\\$&'
    ));
    switch(state.className) {
      case 'mi mi-circle':
        values = regFilter(values, reg).concat(text);
        state.className = 'mi mi-ok-circle';
        break;
      case 'mi mi-ok-circle':
        values = regFilter(values, reg).concat(`-${text}`);
        state.className = 'mi mi-x-circle';
        break;
      case 'mi mi-x-circle':
        values = regFilter(values, reg);
        state.className = 'mi mi-circle';
        break;
    }
    form.categories.value = values.join(',');
  });

  form.addEventListener('submit', evt => {
    evt.preventDefault();
    evt.stopPropagation();
    const elem = form.querySelectorAll('input');
    elem.forEach(el => {
      if(el.value) return;
      el.setAttribute('disabled', 'disabled');
    });
    form.submit();
    elem.forEach(el => el.removeAttribute('disabled'));
  });
})(document.getElementById('search-form'), new URL(location));
