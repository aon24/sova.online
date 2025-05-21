window.sovaActions = window.sovaActions || {};
window.sovaActions.signup = {
	cmd: {
		proceed: doc => {
			let phone = doc.getField('phone');
			if (!phone)
				return doc.msg.ok('Регистрация только для студентов и сотрудников','Регистрация|Телефон не указан');
			
			fetch(`/api/getData?form=login&cmd=checkPhone&phone=${phone}`, {method: 'get', credentials: 'include'})
				.then( response => response.text() )
				.then( tx => {
					if (tx === 'not found')
						return doc.msg.ok('Регистрация только для студентов и сотрудников','Регистрация|Телефон не найден');
					if (tx === 'exist')
						return doc.msg.ok('Повторная регистрация не поддерживается','Регистрация|Вы уже зарегистрированы');

					
					let [email, name] = doc.util.partition(tx, '|');
					let el = document.getElementById('last_name');
					el.value = doc.getField('phone');
					
					el = document.getElementById('email');
					el.value = email || '';

					el = document.getElementById('first_name');
					el.value = name || '';

					doc.proceed = 1;
					doc.forceUpdate();
    			})
    			.catch( e => doc.msg.error(e.message));
		},
	},
	hide: {
		signup: doc => !doc.proceed,
	}
};
