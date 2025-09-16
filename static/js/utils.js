// utils.js
window.$u = {
  onReady(fn){ if (document.readyState !== 'loading') fn(); else document.addEventListener('DOMContentLoaded', fn); },
  qs(sel, root=document){ return root.querySelector(sel); },
  qsa(sel, root=document){ return Array.from(root.querySelectorAll(sel)); },

  getCookie(name){
    const m = document.cookie.match(new RegExp('(^|;)\\s*' + name + '=([^;]+)'));
    return m ? decodeURIComponent(m.pop()) : null;
  },

  csrfHeaders(extra={}) {
    return Object.assign({
      'X-CSRFToken': $u.getCookie('csrftoken')
    }, extra);
  },

  async csrfFetch(url, options={}) {
    const opts = Object.assign({ method:'POST' }, options);
    opts.headers = $u.csrfHeaders(Object.assign({'Content-Type':'application/json'}, opts.headers||{}));
    return fetch(url, opts);
  },

  initSemanticBasics(){
    $('.ui.message .close').on('click', function(){ $(this).closest('.message').transition('fade'); });
    $('.ui.dropdown.simple').dropdown({ on:'click' });
    $('.ui.dropdown.category').dropdown({ on:'hover' });
    $('#mobile-menu-toggle').on('click', function(){
      $('.ui.sidebar').sidebar('setting','transition','overlay').sidebar('toggle');
    });
  },

  bindSortSelectors(){
    $u.qsa('.sort-selector').forEach(sel=>{
      sel.addEventListener('change', async function(){
        const body = { sort: this.value };
        const slug = this.dataset.slug;
        if (slug) body.slug = slug;
        const url = this.dataset.url;
        if (!url) return;
        await $u.csrfFetch(url, { body: JSON.stringify(body) });
        location.reload();
      });
    });
  },

  delegate(root, selector, event, handler){
    root.addEventListener(event, e=>{
      const t = e.target.closest(selector);
      if (t && root.contains(t)) handler(e, t);
    });
  }
};