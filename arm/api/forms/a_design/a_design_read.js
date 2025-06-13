//
// aon 2022
//
// *** *** ***

let startScript2 = doc => {
	if (doc.stopScript) {
		window.playScript && clearInterval(window.playScript);
		return;		
	}
	
	let interval = doc.rootBox.tuning.interval;
	window.playScript = setInterval( () => {
		if (doc.stopScript || interval !== doc.rootBox.tuning.interval) {
			setTimeout( () => {
				window.playScript && clearInterval(window.playScript);
				!doc.stopScript && startScript2(doc);
				}, 1);
			return;
		}
		if (doc.rootBox.clip.peak >= doc.rootBox.clip.histArr.length-1) {
				setTimeout( () => {
					window.playScript && clearInterval(window.playScript);
					doc.stopScript = true;
					}, 1);
				return;
		}

		!doc.rootBox.clip.cmdBusy && doc.rootBox.clip.cmdRedo();
	}, interval === 5000 ? 4000 : interval);
};

let rotate = p3d => {
	if (p3d.tuning.mmm === 'rooms') {
		p3d.tuning.rotate3Z += 2;
		p3d.tuning.rotate3Z %= 360;
	}
	else {
		p3d.tuning.rotate3Y += 2;
		p3d.tuning.rotate3Y %= 360;
	}
	p3d.rebuild = 'rotate';
	p3d.forceUpdate();
};

window.sovaActions = window.sovaActions || {};
window.sovaActions.a_design = {
	init2: doc => {
		let findTurnOn = p3d => {
			if (p3d.tuning.turnOn) {
		
				p3d.tempRotate3Z = p3d.tuning.rotate3Z;
				p3d.tempRotate3Y = p3d.tuning.rotate3Y;
		
				setTimeout( () => {p3d.intervalHandle = setInterval(() => rotate(p3d), 150);}, 300);
			}
			
			for (let it of p3d.floatBoxes)
				findTurnOn(it);
			for (let it of p3d.cellsBoxes)
				findTurnOn(it);
		};
		findTurnOn(doc.rootBox);

		if (doc.rootBox.clip.histArr.length) {
			doc.rootBox.clip.peak = 0;
			doc.pageBox.tuning.playScript = 1;
			startScript2(doc);
		}
	},
	
	recalc: {},
	cmd: {
		close2d: doc => doc.cmdClose(),
		more: (doc, param, ctrlKey, shiftKey) => {
			let page = {
				dbAlias: 'draft',
				title: 'О системе',
				addUrl: `&page=${param}`,
				rsMode: 'read',
				pageName: `more-${param}`,
			};

			doc.previewNew(page, ctrlKey, shiftKey);
		},
		iframe: (doc, url, ctrlKey, shiftKey) => {
			let page = {
				iframeUrl: url,
				min: true, max: true, pont: true, smallCls: true,
				resize: true,
				form: 'filine',
				pageName: url,
				title: url.split('/').at(-1),
				fieldValues: {Q: 'q'}, // чтобы документ не пытался полезть за данными на сервер
				children: [
					{_teg: 'iframe',
						attributes: {
							src: url,
							width: '100%', style: {height: '100%'}
					}}],

			};
			doc.previewNew(page, ctrlKey, shiftKey);
		},
		addFurniture: (doc, boxIndex) => {
			const errExit = s => {
				alert(s);
				doc.page.closePage();
			};

			let btn = doc.rootBox.findBoxByIndex(boxIndex); // btn - button
			if (!btn)
				return errExit('Ошибка в кнопке');
			
			let mmm, named;
			for (let it of btn.parentBox.floatBoxes) { // btn.parentBox - бокс в котором и кнопка, и мебель
				if (it.parent3d === it)
					mmm = it;
			}

			if (!mmm)
				return errExit('Мебель не найдена');


			let wall = doc.mainDoc.rootBox.findWrap(doc.mainDoc.rootBox);
			if (wall && wall.parent3d) {
				if (!wall.tuning.wall) // м.б. выбрана мебель
					wall = wall.parentBox;
				if (wall && wall.tuning.wall) { // wall-выбранная стена с надписью фар,лефт итд
					let s = JSON.stringify(wall.clip.copyCell(mmm, 'ctrl-C'));
					let mmmNew = JSON.parse(s);
					wall.clip.pasteFurniture(wall, mmmNew);
					return;
				}
			}
			return errExit('стена не выбрана');
		},
		
		// *** *** ***
		
		addWall: (doc, boxIndex) => {
			// кнопка "Вставить"
			// команда "winBal(Окно-балкон)". Ее нет ни питоне ни js, она создана в документе с формой a_designer
			// boxIndex === boxIndex кнопки. задается при формировании кнопки в boxTools.getContent()

			const errExit = i => {
				alert(`Стена не выбрана. Code ${i}`);
				doc.page.closePage();
			};

			let btn = doc.rootBox.findBoxByIndex(boxIndex); // btn - button
			if (!btn)
				return errExit(boxIndex);

			let mmm;
			for (let it of btn.parentBox.floatBoxes) // btn.parentBox - блок в котором и кнопка, и 3д
				if (it.tuning.mmm)
					mmm = it;

			if (!mmm)
				return errExit(2);


			let wall = doc.mainDoc.rootBox.findWrap(doc.mainDoc.rootBox);
			if ( !(wall && wall.parent3d && wall.tuning.wall) ) // wall-выбранная стена с надписью фар
				return errExit(3);

			wall.clip.toHist(wall, 'old:addM3t_wall');
			
			let s = JSON.stringify(wall.clip.copyCell(mmm, 'ctrl-C'));
			let wallNew = JSON.parse(s); // wallNew таблица из кирпичей

			wall.clip.delArrCells(wall); // убрать грани или всю таблицу для сложной стены

			for (let it in mmm.tuning)
				if (!it.includes('rotate') && it !== 'mmm' && !it.startsWith('is3d') && !it.startsWith('origin'))
					wall.tuning[it] = mmm.tuning[it];

			if (mmm.tuning.boxContent === 1) { // 1 - просто текст
				let div = mmm.refs.plainText;
				if (div)
					wall.content[0] = div.innerHTML;
			}			

			let m = wall.parent3d.tuning.cm === mmm.tuning.cm ? 1 : mmm.tuning.cm ==='mm' ? 10 : 0.1;
			wall.rect.width *= m;
			wall.rect.height *= m;
			
			let _x = wall.rect.width > wallNew.rect.width ? wall.rect.width : wallNew.rect.width;
			let _y = wall.rect.height > wallNew.rect.height ? wall.rect.height : wallNew.rect.height;

			_x /= m;
			_y /= m;

			wall.rect.width = wallNew.rect.width;
			wall.rect.height = wallNew.rect.height;
			
			wall.type = wallNew.type;
			wall.cells = wallNew.cells || [];
			wall.boxes = wallNew.boxes || [];
			wall.tuning.m3key = wall.type ? 'm3table' : 'wall'; // чтобы отличать в refreshRoom()
			wall.tuning.wed = 0;
			wall.tuning.changed = 1;
			
			wall.tuning.cm = mmm.tuning.cm;
			wall.setScale(wall, wall.parent3d.tuning.cm, true);
			delete wall.tuning.cm;
			
			if (!wall.pending)
				wall.pending = () => {
					wall.setBoxSize(_x, _y);
					wall.rebuild = 'wall';
					wall.pending = () => wall.clip.toHist(wall, 'new:addM3t_wall');
					wall.setWrap();
				};
			doc.page.closePage();
		},
	}
};













