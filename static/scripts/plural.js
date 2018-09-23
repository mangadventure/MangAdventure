function pluralize(element, colon=true) {
  var selector = element + (colon ? ' .colon' : '');
  document.querySelector(selector).innerHTML += 's';
}

