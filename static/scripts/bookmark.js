(function(){
    function getCookie(cookie) {
      var c_name = cookie + "=";
      var cookies = decodeURIComponent(document.cookie).split(';');
      for(var i = 0; i < cookies.length; i++) {
        cookies[i] = cookies[i].trim();
        if(cookies[i].indexOf(c_name) === 0) {
		      return cookies[i].substring(c_name.length, cookies[i].length);
        }
      }
      return null;
    }

    function jsonToPost(obj) {
      var post = [];
      for(var key in obj) {
        if(obj.hasOwnProperty(key)) {
          post.push(key + "=" + obj[key]);
        }
      }
      return encodeURI(post.join("&"));
    }

    var buttons = document.querySelectorAll('.bookmark-btn');
    buttons.forEach(function(btn) {
      btn.addEventListener('click', function() {
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/user/bookmark/', true);
        xhr.setRequestHeader('Content-Type',
          'application/x-www-form-urlencoded; charset=UTF-8');
        xhr.onload = function () {
          if(xhr.status === 200) {
            btn.classList.toggle("mi-bookmark-o");
            btn.classList.toggle("mi-bookmark");
          }
        };
        var data = {
          'csrfmiddlewaretoken': getCookie('csrftoken'),
          'slug': this.getAttribute('data-series'),
        };
        xhr.send(jsonToPost(data));
      })
    });
})();
