window.sovaActions = window.sovaActions || {};
window.sovaActions.v_payments = {
	cmd: {
		search: doc => {
			let view = doc.getControl('mainList');
			let target = doc.getField('search');
			view.search(target);
		},
		cmdEdit:(doc, pk, ctrlKey, shiftKey) => {
			let view = doc.getControl('mainList');
			view.rowClick(pk);
			let page = doc.util.urlKeys(view.props.previewUrl);
			page.title = 'Редактирование ' + doc.getField('leftList');
			page.unid = pk;
			page.rsMode = 'edit';
			doc.previewNew(page, ctrlKey, shiftKey);
		},
		search: doc => doc.getControl('mainList').search(doc.getField('search')),
		reset: doc => {
			doc.setField('search', '');
			doc.getControl('mainList').search('');
		},
		// *** *** ***

	},
	recalc: {
		STATUS: doc => doc.loadView('mainList', true),
	}
};
