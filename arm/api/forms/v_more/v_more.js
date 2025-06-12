window.sovaActions = window.sovaActions || {};
window.sovaActions.v_more = {
    init2: doc => {
		let key = doc.getField('key');
		doc.util.jsonByUrl(doc, `/api/getData?form=v_more&cmd=getLeftList&key=${key}`)
			.then( prj => doc.changeDropList('leftList', prj, 0))
			.catch( () => {});				
	},
    
	// *** *** ***
	
	cmd: {
		cmdNewCopy: (doc, param, ctrlKey) => {
			let pKeys = doc.util.urlKeys(param);
			let page = {
				rsMode: 'new',
				newForm: `${pKeys.form}&sourceDoc=${pKeys.pk}`,
				dbAlias: 'draft',
				title: pKeys.title || 'Создание страницы',
			};
			doc.previewNew(page, ctrlKey);
		},
		cmdNew: (doc, p) => doc.util.xopen(`/api/new?dbAlias=draft&form=${p}&project=${doc.getField('leftList')}&key=${doc.getField('key')}`),

		cmdView: (doc, param, ctrlKey, shiftKey) => {
			let pKeys = doc.util.urlKeys(param);
			let view = doc.getControl('mainList');
			let page = doc.util.urlKeys(view.props.previewUrl);
			view.rowClick(pKeys.pk);
			page.title = pKeys.title || 'Просмотр';
			page.unid = pKeys.pk;
			page.rsMode = 'read';
			//page.form = 'a_design';
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
				doc.util.xopen(`/api/opendoc?dbAlias=draft&unid=${pk}&mode=edit`)
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
			doc.util.jsonByUrl(doc, `/api/getData?form=v_more&cmd=getLeftList&key=${key}`)
				.then( prj => doc.changeDropList('leftList', prj, 0))
				.catch( () => {});				
		},
		
		LEFTLIST: doc => doc.loadView('mainList', true),
	}
};
