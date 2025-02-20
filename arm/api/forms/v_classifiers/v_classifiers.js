window.sovaActions = window.sovaActions || {};
window.sovaActions.v_classifiers = {
    //init2: doc => doc.changeDropList('upList'),
    
	// *** *** ***
	
	cmd: {
		cmdNew: doc => {
			let page = {
				rsMode: 'new',
				newForm: 'Classifier',
				dbAlias: 'nv_Classifier',
				unid: 'new',
				title: 'Новый справочник',
			};
			doc.previewNew(page);
		},

		cmdEdit:(doc, pk, ctrlKey, shiftKey) => {
			let view = doc.getControl('mainList');
			view.rowClick(pk);
			let page = doc.util.urlKeys(view.props.previewUrl);
			page.title = 'Редактирование';
			page.unid = pk;
			page.rsMode = 'edit';
			doc.previewNew(page, ctrlKey, shiftKey);
		},
		search: doc => doc.getControl('mainList').search(doc.getField('search')),
		reset: doc => {
			doc.setField('search', '');
			doc.getControl('mainList').search('');
		},

	},

	// *** *** ***

	recalc: {
		STATUS: doc => doc.loadView('mainList', true),
		CATEGORY: doc => doc.loadView('mainList', true),
	}
};
