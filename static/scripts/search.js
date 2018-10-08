/* global Tablesort */

(function() {
  function getSearchParam(param) {
    var tmp = [];
    var items = location.search.substr(1).split('&');
    for(var i = 0, l = items.length; i <l; ++i) {
      tmp = items[i].split('=');
      if(tmp[0] === param)
        return decodeURIComponent(tmp[1]);
    }
    return ''
  }

  function appendInfo(row, cln, title, text) {
    var sel = 'tr:nth-child(' + row + ') .result-title';
    var fa = document.createElement('i');
    fa.className = 'fas fa-' + cln;
    fa.setAttribute('title', title);
    var div = document.createElement('div');
    div.className = 'result-info';
    div.appendChild(fa);
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
        var n = Math.floor(i / 4) + 1;
        var elem = hidden[i];
        switch(elem.className) {
          case 'result-people s-hidden':
            appendInfo(n, 'user-friends', 'Author/Artist', elem.innerHTML);
            break;
          case 'result-desc s-hidden':
            appendInfo(n, 'info-circle', 'Description', elem.innerHTML);
            break;
          case 'result-chapters s-hidden':
            appendInfo(n, 'file-alt', 'Chapters', elem.innerHTML);
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
  categ.addEventListener('click', function(evt) {
    var el = evt.target;
    if(el.tagName === 'I') el = el.parentNode;
    if(el.tagName !== 'SPAN') return;
    var state = el.children[0];
    var text = el.textContent.trim().toLowerCase();
    var values = getSearchParam('categories').split(',')
      .filter(function(e) { return (e !== '') });
    var reg = new RegExp('-?' + text.replace(
      /[-\/\\^$*+?.()|[\]{}]/g, '\\$&'));
    switch(state.className) {
      case 'far fa-circle fa-fw':
        values = regFilter(values, reg).concat(text);
        state.className = 'far fa-check-circle fa-fw';
        break;
      case 'far fa-check-circle fa-fw':
        values = regFilter(values, reg).concat('-' + text);
        state.className = 'far fa-times-circle fa-fw';
        break;
      case 'far fa-times-circle fa-fw':
        values = regFilter(values, reg);
        state.className = 'far fa-circle fa-fw';
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

