document.querySelectorAll('.day-map').forEach(link=>{
  link.addEventListener('click',()=>{
    const day=link.dataset.day;
    document.getElementById('map-selection').textContent=day==='园内'?'当前显示迪士尼园内主线。':'当前显示D'+day+'路线；地图内可继续切换日期。';
    document.getElementById('map').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});
  });
});
