/* global tinyMCE */

(function() {
  function initTinyMCE(el) {
    var mce_conf = JSON.parse(el.getAttribute('data-tinymce-config'));
    var funcs = [
      'color_picker_callback',
      'file_browser_callback',
      'file_picker_callback',
      'images_dataimg_filter',
      'images_upload_handler',
      'paste_postprocess',
      'paste_preprocess',
      'setup',
      'urlconverter_callback'
    ];
    funcs.forEach(function(fn) {
      if(mce_conf[fn]) {
        mce_conf[fn] = mce_conf[fn].includes('(') ?
          eval(`(${mce_conf[fn]})`) : window[mce_conf[fn]];
      }
    });

    if('elements' in mce_conf && mce_conf.mode == 'exact')
      mce_conf.elements = el.id;
    if(!tinyMCE.editors[el.id]) tinyMCE.init(mce_conf);
  }

  window.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.tinymce').forEach(initTinyMCE);
    document.body.addEventListener('click', function(evt) {
      var row = evt.target.parentNode;
      if(row && row.className.includes('add-row')) {
        setTimeout(function() {
          document.querySelectorAll('.tinymce').forEach(initTinyMCE);
        }, 0);
      }
    }, true);
  });
})();
