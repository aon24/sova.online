window.sovaActions = window.sovaActions || {};
window.sovaActions.arm_filter = {
	init2: doc => {
        doc.setField('_page_', '1');
        if (!doc.mainDoc.getField('studentOnly')) {
            let dropList = JSON.parse(doc.getField('sheduleList'));
            doc.changeDropList('scheduleChoosing', dropList, 0);
        }
    },
	
    hide: {
        filterEvent3: doc => !doc.getField('showEvent3'),
        filterEventCL: doc => !doc.getField('showEventCL'),
        filterSt: doc => !doc.mainDoc.getField('studentOnly'),
        filterCL: doc => doc.mainDoc.getField('studentOnly'),
	},
 
	//*** *** ***

	recalc: {
        SHOWEVENT3: doc => doc.forceUpdate(), // show/hide event3
        
		FILTERALLOW3: doc => getEdges(doc.mainDoc),
		FILTEREVENT3: doc => getEdges(doc.mainDoc),
		FILTERWAS3: doc => getEdges(doc.mainDoc),
		FILTERPAYMENT3: doc => getEdges(doc.mainDoc),
		FILTEREC3: doc => getEdges(doc.mainDoc),
		FILTERFEEDBACK3: doc => getEdges(doc.mainDoc),
        FILTERPLAN3: doc => getEdges(doc.mainDoc),

        SHOWEVENTCL: doc => doc.forceUpdate(), // show/hide eventCL
        FILTERALLOWCL: doc => getEdgesCL(doc.mainDoc), // don't use
        FILTEREVENTCL: doc => getEdgesCL(doc.mainDoc),
        FILTERPLANCL: doc => getEdgesCL(doc.mainDoc),
        
        SCHEDULECHOOSING: doc => getEdgesCL(doc.mainDoc), // val: 'Полное|All','Куратор|C', 'Преподаватель|L', 'Сотрудник|S'

	}, // end of recalc
	
	// ***
	
	cmd: {
		hideFilter: doc => {
			doc.page.frameStyle.display = 'none';
			doc.page.forceUpdate();
		},
	} // end of cmd
};
// *** *** ***

