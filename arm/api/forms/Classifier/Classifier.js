window.sovaActions = window.sovaActions || {};
window.sovaActions.Classifier = {
	cmd: {
		saved: doc => {
			if (doc.mainDoc !== doc) {
				let view = doc.page.owner.getControl('mainList') || doc.mainDoc.getControl('mainList');
				view && view.loadView(true, doc.unid);
			}
		},
	},
};
