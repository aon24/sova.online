if ('serviceWorker' in navigator)
  navigator.serviceWorker.register('/static/home/sw.js')
   .then(
	r => console.log('gut:', r),
	r => console.log('err:', r)
  );