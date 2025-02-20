/*
let user = (doc, title, p1, p2) => {
	let f1 = doc.getField('username');
	let f2 = '';
	let f3 = '';

	doc.inputF3(['Логин', p1, p2], [f1,f2,f3], 'Регистрация входа в систему', )
	.then(arr => {
		if (Object.values(arr).some(value => !value) || arr.F2 !== arr.F3)
			return doc.msg.ok('неправильно');
		doc.msg.box(arr.F1, title)
		.then( () => {
			let buf = `${doc.getField('id')}¤${arr.F1}¤${arr.F2}`;
			doc.util.serverAction(doc, 'putData?form=Profile&cmd=changeUser', buf)
			.then(tx => {
				if (tx === 'OK')
					doc.msg.ok('Успешно');
				else
					doc.msg.error(`${tx}`);
			})
			.catch(err => doc.msg.error(`${err}`));
		})
		.catch(() => {}); // не подтвердил
	})
	.catch(() => {}); // неправильно	
};
*/
// *** *** ***

window.sovaActions = window.sovaActions || {};
window.sovaActions.Profile = {
	init2: doc => {
		let ls;
		ls = doc.getField('tls').split('\n');
		doc.changeDropList('training', ls);
		ls = doc.getField('fls').split('\n');
		doc.changeDropList('fest', ls);
		ls = doc.getField('ils').split('\n');
		doc.changeDropList('invite', ls);
	},
	cmd: {
/*
		addUser: doc => {
			let title = 'Регистрация пользователя|Подтвердите регистрацию';
			user(doc, title, 'Пароль', 'Пароль еще раз');
		},
		changeUser: doc => {
			doc.inputBox(`Введите старый пароль для "${doc.getField('username')}"`, '', 'Проверка прав')
				.then(tx => {
					tx && doc.util.serverAction(doc, 'putData?form=Profile&cmd=testUser', `${doc.getField('id')}¤${tx}`)
					.then(rc => {
						if (rc === 'OK') {
							let title = 'Изменение пользователя|Подтвердите изменение';
							user(doc, title, 'Новый пароль', 'Новый пароль еще раз');
						}
						else
							doc.msg.error(`${rc}`);
					})
					.catch(err => doc.msg.error(`${err}`));
				})
				.catch(() => {}); // не ввел старый
		},
*/
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
				doc.util.xopen(`/api/new?form=v_payments&dbAlias=nv_Payment&unid=1&mode=read&profile=${doc.getField('profile')}`);
		},
		
	},
	// *** *** ***
	
	recalc: {
	},	
	hide: {
		createUser: doc => doc.getField('username'),
		changeUser: doc => !doc.getField('username'),
		st_gr: doc => !doc.getField('role').includes('студент'),
		cur_gr: doc => !doc.getField('role').includes('куратор'),
		// lec_gr: doc => !doc.getField('role').includes('преподаватель'),
	},
	validate: {
	        full_name: doc => doc.getField('full_name') ? '' : 'ФИО',
	        role: doc => doc.getField('role') ? '' : 'Роль',
	},
};
