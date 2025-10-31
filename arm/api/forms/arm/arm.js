let Util;

let showPersonLK = (doc, v, pk, role) => {
    let url = `cmd=newForm&form=arm&showLK=${pk}`;
    Util.getJson(doc, url)
        .then( jsn => {
            doc.setDocProps(jsn);
            return jsn && jsn.urlForm ? Util.jsonByUrl(doc, jsn.urlForm) : null;
        })
        .then( page => {
            doc.register = {};
            page.attributes.focus = role;
            doc.init2 = false;
            doc.fieldValues[role] = v;
            doc.fieldValues['SHOWLK_ID'] = pk;
            doc.loadForm(page);
         })
        .catch( () => {} );
};
// *** *** ***

let changeStatus = (doc, n) => {
    let status = doc.getField(`status${n}`);
    let url = `form=arm&cmd=changeStatus&lk=${n}&status=${status}&showLK_id=${doc.getField('SHOWLK_ID')}`;
    Util.getJson(doc, url)
        .then( jsn => {
            if (n === '') {
                doc.changeDropList('leftList', jsn[0], 0); // список групп
                doc.changeDropList('upList', jsn[1], 0); // кнопки групп
            }
            else {
                doc.changeDropList(`leftList${n}`, jsn, 0); // список групп
            }
            // Util.mainList(doc, n)
        })
        .catch( e => doc.msg.error(e.message) );
};
let getEdgesCL = () => null;
let getEdges = () => null;

// *** *** ***

const scale_etc = [0.75, 0.9, 1, 1.1, 1.25];


window.sovaActions = window.sovaActions || {};
window.sovaActions.arm = {
    init: doc => {
		Util = doc.util;
		let m = parseFloat(localStorage.getItem('nvScale') || 1);
	        doc.m = scale_etc.includes(m) ? m : 1;

		for (let it of ['eMovePl_etc', 'eSavePl_etc', 'noIcons_etc']) {
			doc[it] = localStorage.getItem(it);
		}
		doc.tabNewHide('lk2_Table_FD'); // Расписание-ЛК
		doc.tabNewHide('lks_Table_FD'); // Расписание-ЛК-Контакты (student)
		doc.tabNewHide('LK_Table_FD', 'officeShitChanged'); //  Офис-куратор-препод-сотруд(студент)

		doc.setField('filterAllow3', 'Y'); // for mainList3
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
		// doc.util.addChildPage(doc, filters);	
    },
    init2: doc => {
		doc.setField('scale_etc', scale_etc.indexOf(doc.m));

		// curator *** *** ***
		if (doc.getControl('leftList')) {
            let jsn = JSON.parse(doc.getField('curatorGroups') || '[[],[]]');
            doc.changeDropList('leftList', jsn[0], 0); // список групп
            doc.changeDropList('upList', jsn[1], 0); // кнопки групп
        }

		// lector *** *** ***
		if (doc.getControl('leftList2')) {
            let lectorGroups = JSON.parse(doc.getField('lectorGroups') || '[]');
			doc.changeDropList('leftList2', lectorGroups);
        }

		// student or employee *** *** ***
		if (doc.getControl('mainList3')) {
			Util.mainList(doc, 3); // getEdges(doc, null, 'k1');
        }
    },

	// *** *** ***

	hide: {
		paymentsList: doc => !doc.getField('payments'),

        active: doc => doc.getField('changeView') !== 'l',
        active2: doc => doc.getField('changeView2') !== 'l',
        active3: doc => doc.getField('changeView3') !== 'l', // list

		mainList: doc => doc.getField('changeView') !== 'l',
		showCL: doc => doc.getField('changeView') === 'l',

		mainList2: doc => doc.getField('changeView2') !== 'l',
		showCL2: doc => doc.getField('changeView2') === 'l',

		mainList3: doc => doc.getField('changeView3') !== 'l',
		showCL3: doc => doc.getField('changeView3') === 'l',
	},

    recalc: {
        PAYMENTS: (doc, val) => {
			let showLK_id = doc.getField('showLK_id');
			if(val) {
	            doc.util.getJson(doc, `form=arm&cmd=getTable&table=payments&showLK_id=${showLK_id}`)
	                .then( js => {
	                    doc.setField('paymentsList', js);
	                    doc.forceUpdate();
	                })
	                .catch( e => doc.msg.error(e) );
			}
			else
				doc.forceUpdate();
        },

		SCALE_ETC: (doc, val) => {
			doc.m = scale_etc[val];
			doc.forceUpdate();
		},

        SHOWTUTOR: (doc, v, pk) => showPersonLK(doc, v, pk, 'SHOWTUTOR'),
        SHOWSTUDENT: (doc, v, pk) => showPersonLK(doc, v, pk, 'SHOWSTUDENT'),

        STATUS: doc => changeStatus(doc, ''),
        STATUS2: doc => changeStatus(doc, '2'),

		CHANGEVIEW: doc => Util.mainList(doc),
		CHANGEVIEW2: doc => Util.mainList(doc, 2),

        CHANGEVIEW3: doc => Util.mainList(doc, 3), //getEdges(doc),


		UPLIST: (doc, par, ctrlKey) => {
			// открывает окно "список сессий"
			let [grn, grId] = par.partition();
            let page = Util.urlKeys(par);
            page.newForm = 'v_lk_curator';
            page.title = grn;
            page.unid = grId;
            page.addUrl = `&group=${grn}`;
			doc.previewNew(page, ctrlKey);
		},

		LEFTLIST: doc => Util.mainList(doc) || doc.forceUpdate(),
		LEFTLIST2: doc => Util.mainList(doc, 2) || doc.forceUpdate(),
	},

	// *** *** ***

    cmd: {
		reportGr: (doc, ctrl) => {
            let page = {
				newForm: 'arm_review',
				addUrl: `&nvGroup=${doc.getField('leftList')}`,
				title: `Сводки по группе ${doc.getField('leftList', true)}`,
				rsMode: 'edit',
			}
            doc.previewNew(page, ctrl);
		},
		
		officeShitChanged: (doc, ind) => {
			// console.log('officeShitChanged', ind);
		},
/*
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
*/
		
        addFeedback: doc => {
			doc.inputBox('Отзывы модерируюся', '', 'Отзыв', '', ['Отправить|FV'])
				.then( buf => {
					let body = JSON.stringify(['form=a_more&cmd=addFeedback', buf]);
                    buf && doc.util.getJson(doc, body, true)
						.then( res => {
							doc.msg.ok('Он будет опуликован в течении 24 часов.', 'Отзыв отправлен|Спасибо за отзыв.')
						})
		            	.catch(() => doc.msg.error('Отзывы могут отправлять только зарегистрированные пользователи'));
				})
				.catch({});
		},

        newProfile: (doc, par, ctrlKey) => {
            let page = {
                rsMode: 'new',
				newForm: `Profile`,
				dbAlias: 'nv_Profile',
				title: 'Новый пользователь',
			};
            page.addUrl = '';
            for (let it of ['role', 'info', 'invite']) {
                if (doc.getField(it))
                    page.addUrl += `&${it}=${doc.getField(it)}`;
            }
			doc.previewNew(page, ctrlKey);
        },
        deleteSessionGr: (doc, par) => {
            let [pk, tx] = par.partition('|');
            doc.cmdDel2(tx, pk, 'nv_SessionGr');
        },
        editSessionGr: (doc, par, ctrl) => {
            let [unid, title] = par.partition('|');
            let page = {unid, title, rsMode: 'edit', dbAlias: 'nv_SessionGr'};
            doc.previewNew(page, ctrl);
        },
		dayX: (doc, url, ctrlKey) => doc.previewNew(`newForm=v_lk_curator2&${url}`, ctrlKey),

        selectGr: doc => doc.msg.ok('Выберите группу'),
        manyEvent: doc => doc.msg.ok('Несколько событий в день.\nДоступ к событиям из эскизов или списка.'),

		cmdMminus: doc => Util.mainList(doc, '', -1),
		cmdMplus: doc => Util.mainList(doc, '', 1),
        cmdMminus2: doc => Util.mainList(doc, 2, -1),
		cmdMplus2: doc => Util.mainList(doc, 2, 1),
        cmdMminus3: doc => Util.mainList(doc, 3, -1),
		cmdMplus3: doc => Util.mainList(doc, 3, 1),

        addSessionGr: (doc, p, ctrlKey) => {
            let [nvgroup, date_begin, nve] = p.split('|'); // nve: sess-lection-trening-practic-cl
			let url = `form=arm&cmd=getSessTemplList&nve=${nve}`;
			doc.util.getJson(doc, url)
				.then( jsn => {
					let items = jsn || [];
					doc.msg.list(items, 'Выберите нужное')
						.then(it => {
							if (!it) {
								Util.mainList(doc, '', '');
								return;
							}
							let tmplId = it.partition()[1];
							let page = {
								rsMode: 'new',
								newForm: 'SessionGr',
								addUrl: `&tmplId=${tmplId}&nvgroup=${nvgroup}&date_begin=${date_begin}`,
								dbAlias: 'nv_SessionGr',
								title: 'Добавить в расписание группы',
							};
							doc.previewNew(page, ctrlKey);
						})
						.catch( () => Util.mainList(doc, '', '') );
				})
				.catch( () => {});
		},

		// ***

		openSSt:(doc, par, ctrlKey) => {
			let page = Util.urlKeys(par);
			page.rsMode = 'edit';
			doc.previewNew(page, ctrlKey);
		},
		// *** *** ***
        openProfile: (doc, noProf, ctrlKey, shift) => {
			// self-profile
            if (noProf)
                return doc.msg.ok('Профайл не создан');

			let page = {title: 'Профайл', rsMode: 'edit', form: 'Profile', dbAlias: 'nv_Profile'};
			doc.previewNew(page, ctrlKey, shift);
		},
		// *** *** ***
        openProfile2: (doc, unid, ctrlKey, shift) => {
			// office-mode(non-self-profile)
            if (!unid)
                return doc.msg.ok('Профайл не создан');

			let page = {title: 'Профайл', unid: unid, rsMode: 'edit', form: 'Profile', dbAlias: 'nv_Profile'};
			doc.previewNew(page, ctrlKey, shift);
		},
		// *** *** ***
		//openProgramm: (doc, i, ctrlKey) => {
			// let page = {title: 'Программа', rsMode: 'preview', form: 'Course', dbAlias: 'nv_Course', unid:`${i+1}`};
			// doc.previewNew(page, ctrlKey);
		//},
		// *** *** ***
		cmdEdit:(doc, pk, ctrlKey, shift) => {
			let view = doc.getControl('mainList');
			let page = Util.urlKeys(view.props.previewUrl);
			let grTitle = doc.part(doc.getField('leftList') || '')[0];
			page.title = 'Редактирование ' + grTitle;
			page.addUrl = `&grTitle=${grTitle}`;
			page.rsMode = 'edit';
			page.unid = pk;
			doc.previewNew(page, ctrlKey, shift);
		},
        cmdEdit12:(doc, pk, ctrlKey, shift) => { // для лектора в лк
			let view = doc.getControl('mainList2');
			let page = Util.urlKeys(view.props.previewUrl);
			let grTitle = doc.part(doc.getField('leftList') || '')[0];
			page.title = 'Редактирование ' + grTitle;
			page.addUrl = `&grTitle=${grTitle}`;
			page.rsMode = 'read';
			page.unid = pk;
			doc.previewNew(page, ctrlKey, shift);
		},

		// *** *** ***
		cmdOpenSess:(doc, par, ctrlKey, shift) => doc.previewNew(par, ctrlKey, shift),
		cmdEdit2:(doc, pk, ctrlKey, shift) => {
			let view = doc.getControl('mainList2');
			let page = Util.urlKeys(view.props.previewUrl);
			let grTitle = doc.part(doc.getField('leftList2') || '')[0];
			page.title = 'Редактирование шаблона';
			page.addUrl = `&grTitle=${grTitle}`;
			page.rsMode = `edit`;
			page.unid = pk;
			doc.previewNew(page, ctrlKey, shift);
		},
		// *** *** ***
		cmdEdit3:(doc, pk, ctrlKey, shift) => {
			let page = Util.urlKeys(pk);
			page.title = 'Редактирование';
			page.rsMode = `edit`;
            page.form = page.form || 'SessionGr';
			page.dbAlias = 'nv_' + page.form;
			doc.previewNew(page, ctrlKey, shift);
		},
		// *** *** ***

		exit: doc => window.close(),

		previewArm: (doc, url, ctrlKey, shift) => doc.previewNew(url, ctrlKey, shift),

		open: (doc, url, ctrl) => {
			if (ctrl)
				window.open(url);
			else
				window.location = url;
		},
	},
};
