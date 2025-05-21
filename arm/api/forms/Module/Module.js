let setDayTimeList = (doc, clr) => {
	let scheduled = doc.getField('scheduled');
	if (scheduled) {
		let dt = doc.getControl('schedDay');
		clr && dt.setValue('');
		dt.changeDropList(`/api/well?clues=scheduled_${scheduled}_day`);
		dt = doc.getControl('schedTime');
		clr && dt.setValue('');
		dt.changeDropList(`/api/well?clues=scheduled_${scheduled}_time`);
	}
};

window.sovaActions = window.sovaActions || {};
window.sovaActions.Module = {
    init2: doc => setDayTimeList(doc),
	
	recalc: {
		SCHEDULED: doc => setDayTimeList(doc, true),
    },
	cmd: {
	}
};

// *** *** ***












