window.sovaActions = window.sovaActions || {};
window.sovaActions.v_profiles = {
	cmd: {
		cmdNewPay: (doc, pk) => {
			let view = doc.getControl('mainList');
			view.rowClick(pk);
			let page = {
				rsMode: `new`,
				newForm: `Payment&profile=${pk}`,
				dbAlias: 'nv_Payment',
				unid: 'new',
				title: 'Новый платеж',
			};
			doc.previewNew(page);
		},
		cmdNew: doc => {
			let page = {
				rsMode: 'new',
				newForm: `Profile`,
				dbAlias: 'nv_Profile',
				unid: 'new',
				title: 'Новый пользователь',
			};
			doc.previewNew(page);
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
		LEFTLIST: doc => doc.loadView('mainList', true),
	}
};
