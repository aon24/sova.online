// Arm Student Mobile

let boxRotate = (box, deg) => {
	let x = box.tuning.rotate3Y + deg;
	box.tuning.rotate3Y = Math.round(x / 90) * 90;
	if (!(box.tuning.rotate3Y % 180))
		box.tuning.rotate3Y += 0.001;
	box.tuning.transition = 'transform 700ms ease-in-out 0ms';
	box.parentBox.tuning.persOn = 1;
	box.rebuild = 'rotate';
	box.setWrap();
	setTimeout(() => {
		box.parentBox.tuning.persOn = 0;
		box.parentBox.setWrap();
	}, 1000);
};
// *** *** ***
let getEdgesCL = doc => {};
let getEdges = (doc, shiftMonth, view) => { // view = k1k2 or 'e' or '' for all
	view = view || 'k1k2e';
	let dateZ = document.getElementById('dateZ_3');
    dateZ = (dateZ && dateZ.innerHTML) || '';
    let url = `form=arm&cmd=getEdges&view=${view}&shiftMonth=${shiftMonth || ''}&dateZ=${dateZ}`;

	let filter = doc.sovaPagesByName['arm_filter'].doc;
	for (let k in filter.register) {
		if (k.startsWith('FILTER') && k.endsWith('3')) {
			doc.setField(k, filter.getField(k)); // копируем фильтры в гл.док, чтобы mainList3 отработал
			if (filter.getField(k))
				url += `&${k}=${filter.getField(k)}`;
		}
	}

    doc.util.getJson(doc, url)
        .then( dict => {
			for(let fi in dict) {
            	doc.setField(fi, dict[fi]); // в поле json-"calendar1m"  calendar 1 month, ...
			}
			if (view.includes('e')) { // minus/plus day: view = 'k1k2'
				doc.getControl('mainList3').loadView(true);
	    	}
		})
		.catch( e => doc.msg.error(e.message) );
};

// *** *** ***

const scale_etc = [0.75, 0.9, 1, 1.1, 1.25];


window.sovaActions = window.sovaActions || {};
window.sovaActions.arm = {
    init: doc => {
		let m = parseFloat(localStorage.getItem('nvScale') || 1);
        doc.m = scale_etc.includes(m) ? m : 1;

		doc.tabNewHide('lks_Table_FD', 'hideFilter'); // Расписание/ЛК/Еще. При recalc выполнить cmd: 'hideFilter'
		
		let filters = {
			hide: true, // при закрытии не удалять, а скрывать
			dbAlias: 'dba',
			unid: 'unid',
			pageName: 'arm_filter',
			rsMode: 'new',
			noCls: true,
			fix: true,
			newForm: `arm_filter`,
			title: 'Фильтры',
			frameStyle: {width: 150, top: 0, right:0, display: 'none'}
		};
		doc.util.addChildPage(doc, filters);		
		
    },
    init2: doc => {
		doc.setField('scale_etc', scale_etc.indexOf(doc.m));
		
		doc.setField('filterAllow3', 'Y'); // for mainList3
		doc.setField('filterPlan3', 'Y'); // for mainList3
        doc.util.getJson(doc, 'form=arm&cmd=getEdges&filterAllow3=Y&filterPlan3=Y&view=k1k2e') // status=0 - show allow_s only, k1k2e = all
            .then( dict => {
				for(let fi in dict) {
                	doc.setField(fi, dict[fi]); // в поле json-"calendar1m"  calendar 1 month, ...
                }
                doc.getControl(`mainList3`).loadView(true);

                let cube = doc.rootBox.findBoxByIndex(1001);
            	cube.tuning.transition = 'transform 700ms ease-in-out 200ms';
            	cube.tuning.rotate3Y = 0.001;
            	cube.parentBox.setWrap();
            	setTimeout(() => {
					cube.parentBox.tuning.persOn = 0;
            		cube.parentBox.setWrap();
				}, 1000);
            })
            .catch( e => doc.msg.error(e) );
    },

	// *** *** ***

	hide: {
		filterBtn: doc => doc.getField('lks_Table_FD'),
		paymentsList: doc => !doc.getField('payments'),
	},

    recalc: {
		SCALE_ETC: (doc, val) => {
			doc.m = scale_etc[val];
			doc.forceUpdate();
		},

        PAYMENTS: (doc, val) => {
			if(val) {
	            doc.util.getJson(doc, 'form=arm&cmd=getTable&table=payments')
	                .then( js => {
	                    doc.setField('paymentsList', js);
	                    doc.forceUpdate();
	                })
	                .catch( e => doc.msg.error(e) );
			}
			else
				doc.forceUpdate();
        },
	},

	// *** *** ***

    cmd: {
        reportSt3: (doc, ctrl) => {
            let page = {
                newForm: 'arm_review',
                addUrl: `&nvGroup=${doc.getField('groupC')}&studentMode=3`,
                title: `Сводки по группе ${doc.getField('groupC', true)}`,
                rsMode: 'edit',
            }
            doc.previewNew(page, ctrl);
        },
		recalcDeb: (doc, view) => {
			let l,r;
			switch(view) {
				case 'k1': [l,r] = ['эскиз', 'спис']; break;
				case 'k2': [l,r] = ['спис', 'эскиз']; break;
				case 'e': [l,r] = ['2мес', '1мес']; break;
				case 'l': [l,r] = ['1мес', '2мес']; break;
			}
			doc.setField('fieldL40', l);
			doc.setField('fieldR40', r);
		},
		btnR40: doc => {
			let cube = doc.rootBox.findBoxByIndex(1001);
			boxRotate(cube, 90);
        },
		btnL40: doc => {
			let cube = doc.rootBox.findBoxByIndex(1001);
			boxRotate(cube, -90);
        },
		showFilter: doc => {
			let page = doc.mainDoc.sovaPagesByName['arm_filter'];
			page.frameStyle.display = 'block';
			page.forceUpdate();
		},
		hideFilter: doc => {
			if (doc.getField('lks_Table_FD')) {
				let page = doc.mainDoc.sovaPagesByName['arm_filter'];
				page.frameStyle.display = 'none';
				page.forceUpdate();
			}
		},

		cmdMminus3: doc => getEdges(doc, -1, 'k1k2'),
		cmdMplus3: doc => getEdges(doc, 1, 'k1k2'),

		// ***

		// for payments edit
		previewArm: (doc, url, ctrlKey, shift) => doc.previewNew(url, ctrlKey, shift),

		// *** *** ***
		
        openProfile: (doc, noProf, ctrlKey, shift) => {
			// self-profile
            if (noProf)
                return doc.msg.ok('Профайл не создан');

			let page = {title: 'Профайл', rsMode: 'edit', form: 'Profile', dbAlias: 'nv_Profile'};
			doc.previewNew(page, ctrlKey, shift);
		},
		// *** *** ***

		cmdOpenSess:(doc, par, ctrlKey, shift) => doc.previewNew(par, ctrlKey, shift), // open from k1/k2/e
		
		// *** *** ***
		cmdEdit3:(doc, pk, ctrlKey, shift) => { // open from list-view
			let page = doc.util.urlKeys(pk);
			page.title = 'Редактирование';
			page.rsMode = `edit`;
            page.form = page.form || 'SessionGr';
			page.dbAlias = 'nv_' + page.form;
			doc.previewNew(page, ctrlKey, shift);
		},
		// *** *** ***

	},
};
