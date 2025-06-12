window.sovaActions = window.sovaActions || {};
window.sovaActions.NVGroup = {
	cmd: {
		saved: doc => {
			if (doc.mainDoc !== doc) {
				let view = doc.page.owner.getControl('mainList') || doc.mainDoc.getControl('mainList');
				view && view.loadView(true, doc.unid);
			}
		},
	},
	recalc: {
	},	
	hide: {
	},
};
