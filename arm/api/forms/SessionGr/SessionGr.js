window.sovaActions = window.sovaActions || {};
window.sovaActions.SessionGr = {
	init: doc => {
		doc.videoList = JSON.parse(doc.fieldValues.VIDEOLIST || '[]');
		doc.videoList.sort((a, b) => (a.name || '') > (b.name || '') ? 1 : -1);
		doc.fieldValues.VIDEOLIST = null;
	},
	cmd: {
		setVideoGrid: doc => doc.setField('videoGrid_FD', `${doc.getField('videoList')}`), // \n${doc.getField('videoListAdd')}`),
		saved: doc => {
			if (doc.mainDoc !== doc) {
			   doc.util.mainListGr(doc, '');
			   doc.util.mainListGr(doc, '2');
            }
		},
		// ***
		forceUpdate: doc => doc.forceUpdate(),
	},
	recalc: {
		status: doc => doc.forceUpdate(),
	},
	hide: {

	},
	validate: {
		date_begin: doc => doc.getField('date_begin') ? '' : 'Дата начала',
	},
};

for (let i = 1; i <= 20; i++)
	window.sovaActions.SessionGr.hide[`hide_${i}`] = doc => !doc.getField(`hide_${i}`);
for (let i = 2; i <= 20; i++)
	window.sovaActions.SessionGr.hide[`part_${i}`] = doc => !doc.getField(`status_${i-1}`);

