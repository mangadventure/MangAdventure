(function() {
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

  var form = document.getElementById('search-form');
  var elem = form.elements;
  form.addEventListener('submit', function(evt) {
    evt.preventDefault();
    evt.stopPropagation();
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

