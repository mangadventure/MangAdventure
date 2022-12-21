/* global tinyMCE */

window.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.tinymce').forEach(el => {
    const mce_conf = JSON.parse(el.dataset.tinymceConfig);
    if ('replace_icons' in mce_conf) {
      const old_setup = mce_conf.setup;
      mce_conf.setup = editor => {
        if (typeof old_setup === 'function') old_setup(editor);
        editor.on('init', evt => {
          evt.target.editorContainer.querySelectorAll('i').forEach(ico => {
            if (ico.className === 'mce-caret') {
              ico.className = 'mi mi-down';
            } else if (ico.className.endsWith('save')) {
              ico.className = 'mi mi-send';
              ico.nextElementSibling.innerHTML =
                mce_conf.submit_text || 'Send';
            } else {
              ico.className = ico.className
                .replace('mce-ico', 'mi')
                .replace('mce-i-', 'mi-');
            }
          });
        });
      };
    }
    if (!tinyMCE.editors[el.id]) tinyMCE.init(mce_conf);
  });
});
