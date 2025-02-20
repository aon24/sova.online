window.sovaActions = window.sovaActions || {};
window.sovaActions.ilog = {
    recalc: {
        CAT: doc => doc.changeDropList('SUBCAT'),
		LOG_0_6: (doc, num) => doc.changeDropList('SUBCAT', `${doc.getField('CAT')}&log=${num}`),
        SUBCAT: (doc, label) => { 
        	let keys = `form=ilog&key=${doc.getField('cat')}|${label}`;
		    fetch(`/api/get/getData?${keys}`, {method: 'get', credentials: 'include'})
		        .then( response => response.text() )
		        .then( txt => doc.setField('msg', txt) )
		        .catch( err => doc.setField('msg', err.message) );        
        }
    }
};

// *** *** ***













