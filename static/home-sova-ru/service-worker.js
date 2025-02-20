if ('serviceWorker' in navigator)
  navigator.serviceWorker.register('https://sova-online.ru/static/home/sw.js')
   .then(
	r => console.log('gut:', r),
	r => console.log('err:', r)
  );