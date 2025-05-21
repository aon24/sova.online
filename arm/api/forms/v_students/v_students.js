window.sovaActions = window.sovaActions || {};
window.sovaActions.v_students = {
	// *** *** ***
	
	cmd: {
		cmdNew: doc => {
			let page = {
				rsMode: 'new',
				newForm: `Profile`,
				dbAlias: 'nv_Profile',
				title: 'Новый пользователь',
				addUrl: `&group=${doc.getField('leftList')}`,
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
		// *** *** ***

	},
	recalc: {
		UPLIST: doc => doc.loadView('mainList', true),
		LEFTLIST: doc => doc.loadView('mainList', true),

	}
};
