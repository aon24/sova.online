window.sovaActions = window.sovaActions || {};
window.sovaActions.v_landing = {
    init2: doc => {
		let key = doc.getField('key');
		doc.util.jsonByUrl(doc, `/api/getData?form=v_landing&cmd=getLeftList&key=${key}`)
			.then( prj => doc.changeDropList('leftList', prj, 0))
			.catch( () => {});				
	},
    
	// *** *** ***
	
	cmd: {
/*
		saved: doc => {
			if (doc.mainDoc !== doc) {
				let parentDoc = doc.page.owner;
				let view = parentDoc.getControl('mainList');
				view && view.loadView(true, doc.unid);
			}
		},
*/		
		cmdNew: doc => doc.util.xopen(`/api/new?form=a_design&dbAlias=draft&unid=new&mode=new&key=${doc.getField('key')}`),

		cmdView:(doc, pk, ctrlKey, shiftKey) => {
			let view = doc.getControl('mainList');
			view.rowClick(pk);
			let page = doc.util.urlKeys(view.props.previewUrl);
			page.title = 'Просмотр';
			page.unid = pk;
			page.rsMode = 'read';
			page.form = 'a_design';
			doc.previewNew(page, ctrlKey, shiftKey);
		},
		
		cmdEdit:(doc, pk, ctrlKey, shiftKey) => {
			let view = doc.getControl('mainList');
			view.rowClick(pk);
			if (ctrlKey && shiftKey) {
				let page = doc.util.urlKeys(view.props.previewUrl);
				page.title = 'Просмотр';
				page.unid = pk;
				doc.previewNew(page, ctrlKey, shiftKey);
			}
			else
				doc.util.xopen(`/api/opendoc?dbAlias=draft&unid=${pk}&form=a_design&mode=edit`)
		},
		search: doc => doc.getControl('mainList').search(doc.getField('search')),
		reset: doc => {
			doc.setField('search', '');
			doc.getControl('mainList').search('');
		},

	},

	// *** *** ***

	recalc: {
		KEY: (doc, key) => {
			doc.util.jsonByUrl(doc, `/api/getData?form=v_landing&cmd=getLeftList&key=${key}`)
				.then( prj => doc.changeDropList('leftList', prj, 0))
				.catch( () => {});				
		},
		
		LEFTLIST: doc => doc.loadView('mainList', true),
	}
};
