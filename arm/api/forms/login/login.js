window.sovaActions = window.sovaActions || {};
window.sovaActions.login = {
	cmd: {
		reg: doc => {
			let page = {
				rsMode: 'new',
				newForm: 'signup',
				dbAlias: 'dba',
				title: `Регистрация`,
				frameStyle: {width: 500, maxHeight: 1000}
			};
			doc.previewNew(page);
		},
	},
	hide: {
		err: doc => !doc.getField('err_fd')
	},
};
