window.sovaActions = window.sovaActions || {};
window.sovaActions.Profile = {
	init: doc => {
		doc.tabNewHide('PR_Table_FD', null); // При recalc не выполнять cmd
	},
	init2: doc => {
		let ls;
		ls = doc.getField('tls_fd').split('\n');
		doc.changeDropList('training', ls);
		ls = doc.getField('fls_fd').split('\n');
		doc.changeDropList('fest', ls);
		ls = doc.getField('ils_fd').split('\n');
		doc.changeDropList('invite', ls);
	},
	cmd: {
		saved: doc => {
			if (doc.mainDoc !== doc) {
				let view = doc.page.owner.getControl('mainList') || doc.mainDoc.getControl('mainList');
				view && view.loadView(true, doc.unid);
			}
		},
		forceUpdate: doc => doc.forceUpdate(),

		payList: (doc, p, ctrl, shiftKey) => {
			if (!ctrl) {
				let page = {
					newForm: 'v_payments',
					unid: '1',
					dbAlias: 'nv_Payment',
					title: 'Платежи',
					addUrl: `&profile=${doc.getField('id')}`
				};
				doc.previewNew(page, ctrl, shiftKey);
			}
			else
				doc.util.xopen(`/api/new?form=v_payments&dbAlias=nv_Payment&mode=read&profile=${doc.getField('profile')}`);
		},
		
	},
	// *** *** ***
	
	recalc: {
		PR_TABLE_FD: doc => doc.forceUpdate(),
	},	
	hide: {
		cur_gr: doc => !doc.getField('role').includes('куратор'),
	},
	validate: {
	        full_name: doc => doc.getField('full_name') ? '' : 'ФИО',
	        role: doc => doc.getField('role') ? '' : 'Роль',
	},
};


	
	
	
