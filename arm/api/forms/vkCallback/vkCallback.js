window.sovaActions = window.sovaActions || {};
window.sovaActions.vkCallback = {
    init2: doc => {
	},
	
	recalc: {
    },

	cmd: {
		logout: doc => doc.util.jsonByUrl(doc, '/api/runCmd?cmd=logout').then(() => window.location.href = '/').catch(() => {}),
		verify: doc => {
    		fetch('/api/getData?form=vkCallback&cmd=verify', {method: 'get', credentials: 'include'})
				.then( response => response.text() )
				.then( tx => doc.setField('log', tx))
    			.catch( e => doc.setField('log', e.message));
		},
	},
	
	hide: {
		err: doc => !doc.getField('err'),
		gut: doc => doc.getField('err'),
	}
};

// *** *** ***












