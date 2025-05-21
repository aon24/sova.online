window.sovaActions = window.sovaActions || {};
window.sovaActions.SessionGr = {
	init: doc => {
		doc.videoList = JSON.parse(doc.getField('VIDEOLIST_FD') || '[]');
		doc.videoList.sort((a, b) => (a.name || '') > (b.name || '') ? 1 : -1);
		for (let i=0; i < 10; i++)
			doc.sova.hide[`SST_Table_FD_${i}`] = doc => i !== doc.getField('SST_Table_FD');
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
		SST_TABLE_FD: doc => doc.forceUpdate(),
		status: doc => doc.forceUpdate(),
	},
	hide: {
		job1: doc => !doc.getField('job1'),
		job2: doc => !doc.getField('job2'),
		job3: doc => !doc.getField('job3'),
		job4: doc => !doc.getField('job4'),
		job5: doc => !doc.getField('job5'),
		video: doc => !doc.getField('videoList_FD'),
	},
	validate: {
		date_begin: doc => doc.getField('date_begin') ? '' : 'Дата начала',
	},
};

for (let i = 1; i <= 20; i++)
	window.sovaActions.SessionGr.hide[`hide_${i}`] = doc => !doc.getField(`hide_${i}`);
for (let i = 2; i <= 20; i++)
	window.sovaActions.SessionGr.hide[`part_${i}`] = doc => !doc.getField(`status_${i-1}`);

