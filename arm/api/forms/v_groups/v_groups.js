window.sovaActions = window.sovaActions || {};
window.sovaActions.v_groups = {
	cmd: {
		newGroup: doc => {
			let page = {
				rsMode: 'new',
				newForm: `NVGroup`,
				dbAlias: 'nv_NVGroup',
				title: 'Новая группа',
			};
			doc.previewNew(page);
		},

		cmdEdit:(doc, pk, ctrl, shiftKey) => {
			let view = doc.getControl('mainList');
			view.rowClick(pk);
			let page = doc.util.urlKeys(view.props.previewUrl);
			page.title = 'Редактирование ' + doc.getField('leftList');
			page.unid = pk;
			page.rsMode = 'edit';
			doc.previewNew(page, ctrl, shiftKey);
		},
	},
	// *** *** ***
	recalc: {
		STATUS: (doc, selected) => doc.loadView('mainList', true),
	}
};