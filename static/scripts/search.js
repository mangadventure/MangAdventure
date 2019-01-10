/* global Tablesort */

(function() {
  function getSearchParam(param) {
    var tmp = [];
    var items = location.search.substr(1).split('&');
    for(var i = 0, l = items.length; i < l; ++i) {
      tmp = items[i].split('=');
      if(tmp[0] === param)
        return decodeURIComponent(tmp[1]);
    }
    return ''
  }

  function appendInfo(row, cln, title, text) {
    var sel = 'tr:nth-child(' + row + ') .result-title';
    var mi = document.createElement('i');
    mi.className = 'mi mi-' + cln;
    mi.setAttribute('title', title);
    var div = document.createElement('div');
    div.className = 'result-info';
    div.appendChild(mi);
    div.innerHTML += text;
    document.querySelector(sel).appendChild(div);
  }

  function regFilter(arr, reg) {
    return arr.filter(function(e) { return !reg.test(e) });
  }

  function matchQuery(query) {
    if(query.matches) {
      var hidden = document.querySelectorAll('td.s-hidden');
      for(var i = 0, l = hidden.length; i < l; ++i) {
        var n = Math.floor(i / 5) + 1;
        var elem = hidden[i];
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
      }
    } else {
      var info = document.querySelectorAll('.result-info');
      for(var j = 0, s = info.length; j < s; ++j) {
        info[j].parentElement.removeChild(info[j]);
      }
    }
  }

  var query = window.matchMedia('(max-width: 690px)');
  matchQuery(query);
  query.addListener(matchQuery);

  var table = document.getElementById('result-table');
  if(table) {
    new Tablesort(table);
    table.querySelector('th').removeAttribute('data-sort-default');
  }

  var categ = document.getElementById('category-container');
  var values = getSearchParam('categories').split(',')
    .filter(function(e) { return (e !== '') });
  categ.addEventListener('click', function(evt) {
    var el = evt.target || evt.srcElement;
    if(el.tagName === 'I' || el.nodeType === 3)
      el = el.parentNode;
    if(el.className !== 'tooltip category') return;
    var state = el.children[0];
    var text = el.textContent.trim().toLowerCase();
    var reg = new RegExp('-?' + text.replace(
      /[-\/\\^$*+?.()|[\]{}]/g, '\\$&'));
    switch(state.className) {
      case 'mi mi-circle':
        values = regFilter(values, reg).concat(text);
        state.className = 'mi mi-ok-circle';
        break;
      case 'mi mi-ok-circle':
        values = regFilter(values, reg).concat('-' + text);
        state.className = 'mi mi-x-circle';
        break;
      case 'mi mi-x-circle':
        values = regFilter(values, reg);
        state.className = 'mi mi-circle';
        break;
    }
    form.categories.value = values.join(',');
  });

  var form = document.getElementById('search-form');
  form.addEventListener('submit', function(evt) {
    evt.preventDefault();
    evt.stopPropagation();
    var elem = form.elements;
    var l = elem.length;
    for(var i = 0; i < l; ++i) {
      if(!elem[i].value)
        elem[i].setAttribute('disabled', 'disabled');
    }
    form.submit();
    for(var j = 0; j < l; ++j) {
      elem[j].removeAttribute('disabled');
    }
  });
})();

