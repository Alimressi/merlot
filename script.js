/* Merlot Wine&Dine : поведение страницы.
   Тексты и языки статические: каждая версия лежит по своему адресу
   и собирается через build.py, скрипту это не нужно.
   Без JavaScript страница читается целиком. */
(function () {
  'use strict';

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---- заглушка вместо ненайденной картинки ---- */
  function markMissing(img) {
    var host = img.closest('.shot');
    if (host) host.classList.add('is-missing');
    img.style.display = 'none';
  }
  document.querySelectorAll('.shot img').forEach(function (img) {
    img.addEventListener('error', function () { markMissing(img); });
    if (img.complete && img.naturalWidth === 0) markMissing(img);
  });

  /* ---- появление блоков при прокрутке (без обработчиков scroll) ---- */
  var reveals = document.querySelectorAll('.reveal');

  if (reduce || !('IntersectionObserver' in window)) {
    reveals.forEach(function (el) { el.classList.add('in'); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry, i) {
        if (!entry.isIntersecting) return;
        var el = entry.target;
        el.style.transitionDelay = Math.min(i * 50, 220) + 'ms';
        el.classList.add('in');
        io.unobserve(el);
      });
    }, { rootMargin: '0px 0px -6% 0px', threshold: 0.06 });
    reveals.forEach(function (el) { io.observe(el); });

    /* подстраховка: скрытая вкладка или медленная отрисовка
       не должны оставить блок невидимым */
    window.setTimeout(function () {
      reveals.forEach(function (el) { el.classList.add('in'); });
    }, 2500);
  }

  /* ---- меню на телефоне ---- */
  var nav = document.getElementById('nav');
  var burger = document.getElementById('burger');
  var mobilenav = document.getElementById('mobilenav');

  function setNav(open) {
    nav.classList.toggle('is-open', open);
    mobilenav.classList.toggle('is-open', open);
    burger.setAttribute('aria-expanded', String(open));
    mobilenav.hidden = !open;
    document.body.classList.toggle('is-locked', open);
    burger.querySelector('i').className = open ? 'ph-light ph-x' : 'ph-light ph-list';
  }

  if (burger) {
    burger.addEventListener('click', function () {
      setNav(burger.getAttribute('aria-expanded') !== 'true');
    });
    mobilenav.querySelectorAll('a').forEach(function (a) {
      a.addEventListener('click', function () { setNav(false); });
    });
    window.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.classList.contains('is-open')) setNav(false);
    });
    window.matchMedia('(min-width: 1081px)').addEventListener('change', function (e) {
      if (e.matches && nav.classList.contains('is-open')) setNav(false);
    });
  }

  /* ---- карта включается по нажатию, иначе свайп по ней не листает страницу ---- */
  var mapGuard = document.getElementById('mapGuard');
  var mapBox = document.getElementById('map');
  if (mapGuard && mapBox) {
    mapGuard.addEventListener('click', function () {
      mapBox.classList.add('is-live');
    });
  }

  /* ---- нижняя панель звонка: появляется, когда уходит первый экран,
         и прячется у блока контактов, где такая же кнопка уже есть ---- */
  var callbar = document.getElementById('callbar');
  var heroActions = document.querySelector('.hero__actions');
  var visitActions = document.querySelector('.visit__actions');

  if (callbar && heroActions && 'IntersectionObserver' in window) {
    var heroPassed = false;
    var visitShown = false;

    function syncBar() {
      var on = heroPassed && !visitShown;
      callbar.classList.toggle('is-on', on);
      callbar.setAttribute('aria-hidden', String(!on));
      callbar.querySelectorAll('a').forEach(function (a) {
        a.tabIndex = on ? 0 : -1;
      });
    }

    new IntersectionObserver(function (entries) {
      heroPassed = !entries[0].isIntersecting && entries[0].boundingClientRect.top < 0;
      syncBar();
    }, { threshold: 0 }).observe(heroActions);

    if (visitActions) {
      new IntersectionObserver(function (entries) {
        visitShown = entries[0].isIntersecting;
        syncBar();
      }, { threshold: 0.4 }).observe(visitActions);
    }
  }
})();
