let _reviewBody;

let startJob = doc => {
    let url = 'form=arm_review&cmd=startJob';
    for (fi of ['filter', 'dt1', 'dt2', 'jobName', 'nvGroup'])
        url += `&${fi}=${doc.getField(fi)}`;

    let student = doc.getField('studentMode') === '3' ? 'student3' : 'student';
    url += `&student=${doc.getField(student)}`;

    doc.util.getJson(doc, url)
        .then(js => {
            _reviewBody = [js[0]['children'][1]]; // js=[_div(children=[toolbar, body])]
            doc.setField('result', js)
        })
        .catch();
};

// ***

window.sovaActions = window.sovaActions || {};
window.sovaActions.arm_review = {
	init2: doc => {
        if (doc.getField('studentMode') === '1') {
            doc.util.getJson(doc, `form=arm_review&cmd=getStudentList&nvGroup=${doc.getField('nvGroup')}`)
                .then(js => {
                    doc.changeDropList('student', js)
                })
                .catch();
        }
    },
	
    hide: {
		group: doc => doc.getField('studentMode'),
        student: doc => doc.getField('studentMode') !== '1',
        student3: doc => doc.getField('studentMode') != '3',
	},
 
	//*** *** ***

	recalc: {
        JOBNAME: doc => doc.getField('filter') && startJob(doc),
        FILTER: doc => {
            if (doc.getField('studentMode') === '1') {
                doc.getField('student') && startJob(doc);
            }
            else if (doc.getField('studentMode') === '3') {
                startJob(doc);
            }
            else {
                doc.getField('jobName') && startJob(doc);
            }
        }
	},
	
	// ***
	
	cmd: {

		openMax: doc => {
			let w = window.innerWidth; // doc.mainDoc.m;
			let h = window.innerHeight; // doc.mainDoc.m;
			let review = {
				dbAlias: 'dba',
				unid: 'unid',
				pageName: 'arm_review',
				rsMode: 'new',
				noCls: true,
				fix: true,
				newForm: 'arm_max',
				title: `Сводка по группе ${doc.getField('nvGroup')}`,
				frameStyle: {width: w, height: h}
//				frameStyle: {width: '100dvw', height: '100dvh', top: 0, left:0}
			};
			doc.util.addChildPage(doc, review);
		}
	} // end of cmd
};
// *** *** ***

