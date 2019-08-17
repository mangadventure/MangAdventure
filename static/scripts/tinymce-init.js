/* global tinyMCE */

window.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.tinymce').forEach(function(el) {
    var mce_conf = JSON.parse(el.getAttribute('data-tinymce-config'));
    if('replace_icons' in mce_conf) {
      var old_setup = mce_conf.setup;
      mce_conf.setup = function(editor) {
        if(typeof old_setup === 'function') old_setup(editor);
        editor.on('init', function(evt) {
          evt.target.editorContainer.querySelectorAll('i')
            .forEach(function(ico) {
              if(ico.className === 'mce-caret') {
                ico.className = 'mi mi-down';
              } else if(ico.className.endsWith('save')) {
                ico.className = 'mi mi-send';
                ico.nextElementSibling.innerHTML =
                  mce_conf.submit_text || 'Send';
              } else {
                ico.className = ico.className
                  .replace('mce-ico', 'mi')
                  .replace(/mce-i-(\w+)/, 'mi-$1');
              }
            });
        });
      };
    }
    if(!tinyMCE.editors[el.id]) tinyMCE.init(mce_conf);
  });
});
