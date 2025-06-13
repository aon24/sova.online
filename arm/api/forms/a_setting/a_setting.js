
// *** *** ***
const testSBF = (doc, feature, val, toHist) => {
	if (doc.box && (doc.box.tuning[feature] !== val || toHist === true))
		return doc.box;
};

const _saveWH = (box, feature, val) => {
	box.clip.toHist(box, 'old:setXYZ_rooms');
	box.tuning[feature] = val;
	let ls = [];
	let [w, h, z] = [box.tuning.is3dX, box.tuning.is3dY, box.tuning.is3dZ];
	
	for (let it of box.floatBoxes) {
		let side_0 = it.floatBoxes[0];
		let tu = side_0.tuning;
		if (!tu.changed)
			switch(tu.wall) {
				case 'far':		side_0.setBoxSize(w, z); break;
				case 'right':	side_0.setBoxSize(h, z); break;
				case 'left':	side_0.setBoxSize(h, z); break;
				case 'door':	side_0.setBoxSize(w, z); break;
				case 'top':		side_0.setBoxSize(w, h); break;
				case 'ground':	side_0.setBoxSize(w, h); break;
			}
		ls.push([tu.is3dX, tu.is3dY, tu.changed]); // запомнить высоту и ширину. Если changed=0, они возьмутся из rooms
		tu.changed = tu.x0 = tu.y0 = 0;
	}
	
	box.setWrap();
	setTimeout( () => {
		box.floatBoxes.forEach( (it, i) =>	{
			let tu = it.floatBoxes[0].tuning;
			[tu.is3dX, tu.is3dY, tu.changed] = ls[i];
		});
		box.toHistAfterRender = 'new:setXYZ_rooms';
		box.rebuild = 'parent3d';
		box.forceUpdate();
	}, 500);
};

const _setBoxSize = (box, x, y) => {
	if (!box)
		return;

	if (box.tuning.metric) {
		if ( Math.abs(x + y - box.tuning.whp) < 1 )
			return;
	}
	else if ( (x && Math.abs(x - box.rect.width) < 1) || (y && Math.abs(y - box.rect.height) < 1) )
		return;

	if (!box.parent3d) {
		box.clip.toHist(box, 'setBoxSize');
		box.setBoxSize(x, y);
		box.setWrap();
		return;
	}
	let p3 = box.parent3M || box.parent3d;
	box.clip.toHist(p3, 'setBoxSize_rooms');

	if (box.tuning.metric) { // percent
		box.tuning.whp = x || y;
		x *= box.parentBox.rect.width * 0.01;
		y *= box.parentBox.rect.height * 0.01;
	}
	box.setBoxSize(x, y);
	
	if (box.tuning.wall)
		box.tuning.changed = 1;

	p3.rebuild = 'rooms';
	p3.forceUpdate();
};

const _setLeftTop = (box, leftTop, val, noHist) => {
	if (box && box.rect[leftTop] !== val && noHist !== true) {
		box.clip.toHist(box, 'old:Move-c-0', leftTop);
		box.rect[leftTop] = val;
		box.clip.toHist(box, 'new:Move-c-0', leftTop);
		box.forceUpdate();
	}
};
		
const d3d = (doc, tu) => tu ? doc.box && doc.box.parent3d && doc.box.parent3d.tuning[tu] : doc.box && doc.box.parent3d;

// *** *** ***

const writeHist = (box, feature, val, noHist, sl, tu='tuning') => { // записывает(или нет)в историю исходное значение и устанавливает тюнинг в новое
	if (noHist !== true) {
		if (sl !== undefined)
			box.tuning[feature] = sl;
		box.clip.toHist(box, tu, feature);
	}
	box.tuning[feature] = val;
};

// *** *** ***

const scale = (fbox, val, noHist, sl, scale23) => {
	if (noHist !== true) {
		if (sl === undefined)
			fbox.clip.toHist(fbox, 'tuning', scale23);
		else {
			fbox.tuning[scale23] = sl;
			fbox.clip.toHist(fbox, 'tuning', scale23);
			fbox.tuning[scale23] = val;
			fbox.forceUpdate();
			return;
		}
	}
	
	fbox.rect.left *= fbox.tuning[scale23]/val;
	fbox.rect.top  *= fbox.tuning[scale23]/val;
	fbox.tuning[scale23] = val;

	fbox.forceUpdate();
};

// *** *** ***

const furniture = (doc, prj, mType, host) => {
	let mainDoc = doc.page.props.owner;
	let rect = doc.util.getRect('root', 70, 70);
	rect.width = Math.min(rect.width, 700);
	let rect2 = doc.util.getRect('root', 100, 100);
	rect.left = rect2.width - rect.width - 5;
	rect.top = rect2.height - rect.height - 55;
	let dbAlias = mainDoc.dbAlias; // м.б. другой журнал
	mainDoc.previewNew(`title=${mType}&dbAlias=${dbAlias}&key_project=${prj}&key_pageName=${mType}&mode=preview&form=a_design&viewKey=cases`, null, rect);
};

const startScript = doc => {
	let undo = 0;

	let interval = doc.rootBox.tuning.interval;
	window.playScript = setInterval( () => {
		if (interval !== doc.rootBox.tuning.interval) {
			setTimeout( () => {
				window.playScript && clearInterval(window.playScript);
				!doc.stopScript && startScript(doc);
				}, 1);
			return;
		}		
		
		
		if (doc.box.clip.peak >= doc.box.clip.histArr.length-1) {
			if (doc.getField('playScript') === 'play') {
				setTimeout( () => {
					window.playScript && clearInterval(window.playScript);
					doc.pageBox.tuning.playScript = '';
					doc.setField('playScript', 0);
					doc.stopScript = true;
					doc.forceUpdate();
				}, 1);
				return;
			}
			else
				undo = 1;
		}
		else if (doc.box.clip.peak === 0)
			undo = 0;
		if (!doc.rootBox.clip.cmdBusy)
			undo ? doc.box.clip.cmdUndo() : doc.box.clip.cmdRedo();
	}, interval);
};
// *** *** ***

window.sovaActions = window.sovaActions || {};
window.sovaActions.a_setting = {
	init: doc => {
		for (let i=0; i < 10; i++)
			doc.sova.hide[`SET_Table_FD_${i}`] = doc => i !== doc.getField('SET_Table_FD');
	},
	init2: doc => {
		let mainDoc = doc.page.props.owner;
		doc.setField('_page_', '1'); // _page_ === 1, означает, что это страница, а не документ и сохранять ее не надо // blocking Esc
		for (let it of ['project', 'pageName', 'pageUrl', 'title', 'pageCat', 'notes', 'closed', 'key',
			'rainbow', 'preview', 'table', 'tableSize', 'saveScript',
			'docNo_FD', 'created_FD', 'modified_FD','creator_FD', 'modifier_FD', 'published_FD',
			]) doc.setField(it, mainDoc.getField(it));

		for (let i=1; i < 10; i++) {
			doc.setField( `tabBtn_${i}`, mainDoc.getField(`tabBtn_${i}`) );
			doc.setField( `tab_${i}`, mainDoc.getField(`tab_${i}`) );
		}
		doc.page.frameStyle.top = 0;
		mainDoc.rootBox.pending = () =>	mainDoc.util.runCmd(mainDoc, 'setting');
		mainDoc.forceUpdate();

	},
    //*** *** ***

    hide: {
		// *** переключает все
		setBox: doc => doc.showSetting !== 'setBox',
		setPage: doc => doc.showSetting !== 'setPage',

		isTable: doc => !doc.box || !doc.box.tuning.table,

		// бордер
		borders: doc => !doc.box || doc.box.tuning.bb !== 2 || doc.box.type,
		borEQ: doc => !doc.box || doc.box.tuning.border !== 'borEQ',
		borNE: doc => !doc.box || doc.box.tuning.border !== 'borNE',
		borLeft: doc => !doc.box || doc.box.tuning.borderSide,
		borTop: doc => !doc.box || doc.box.tuning.borderSide !== 1,
		borRight: doc => !doc.box || doc.box.tuning.borderSide !== 2,
		borBottom: doc => !doc.box || doc.box.tuning.borderSide !== 3,
		
		//тень
		shadow: doc => !doc.box || !(doc.box.tuning.bb === 3),
		shadowOn: doc => !doc.box || !doc.box.tuning.shadow,


		// контент boxContent 1,2,3,4 - tx,jsDraft, button, field
		boxContent: doc => !doc.box || doc.box.tuning.bb !== 4,
		textStyle: doc =>  !doc.box || doc.box.tuning.bb !== 4,
		isButton: doc => !doc.box || doc.box.tuning.boxContent !== 4,
		buttonUrl: doc => !doc.box || !doc.box.tuning.buttonAction || doc.box.tuning.buttonAction !== 'url',
		buttonCmd: doc => !doc.box || !doc.box.tuning.buttonAction || doc.box.tuning.buttonAction !== 'javascript',
		isField: doc => !doc.box || doc.box.tuning.bb !== 4 || doc.box.tuning.boxContent !== 3,
		dropList: doc => !doc.box || !(doc.box.tuning.fieldType || '').startsWith('lb'),

		// бокс
		boxStyle: doc => !doc.box || doc.box.tuning.bb !== 1,

		// ширина и высота блока
		boxSizeX: doc => !doc.box || doc.box.row,
		boxSizeY: doc => !doc.box || doc.box.column,
		
		zIndex: doc => !doc.box
			|| !doc.box.parentBox
			|| !doc.box.floating
			|| !doc.box.parentBox.boxes.length,
		floatBox: doc => !doc.box || !doc.box.floating,

		translate: doc => !doc.box || doc.box.tuning.trans,
		rotate: doc => !doc.box || doc.box.tuning.trans !== 1,
		skew: doc => !doc.box || doc.box.tuning.trans !== 2,

		showAnchor: doc => !doc.box || !doc.box.tuning.anchor,


		// свойства 2д
//		bb: doc => !doc.box || doc.box.tuning.line || doc.box.tuning.mmm === 'rooms'),
		bb: doc => !doc.box || doc.box.tuning.line || (doc.box.tuning.mmm && doc.box.tuning.mmm!=='brick') || doc.box.tuning.m3key==='m3table',
		scale2d: doc => !doc.box || doc.box.parent3d || !doc.box.parentBox || doc.box.parentBox.getFloat.boxIndex !== 1000,
		// стрелка
		arrow: doc => !doc.box || !doc.box.tuning.line,
		
		
		
// *** 3d
		// скрыть, если не мебель
		tumba: doc => !doc.box || !doc.box.parent3M,
		ground: doc => !doc.box || !doc.box.parent3M || doc.box.parentBox.tuning.wall !== 'ground',
		noGround: doc => !doc.box || !doc.box.parent3M || doc.box.parentBox.tuning.wall === 'ground',

		// скрыть размеры таблицы, если выбран фасад, грань и идт
		// m3tableSize: doc => !d3d(doc) || doc.box !== doc.box.parent3d,
		
//		m3tab: doc => !doc.box || doc.box.parent3T !== doc.box.getFloat || doc.box.getFloat.tuning.wall || doc.box === doc.box.parent3d,
		m3tab: doc => !doc.box || !doc.box.parent3T || doc.box.parent3T === doc.box.parent3d,
		
		//brick_w3: doc => !d3d(doc) || doc.box.tuning.m3key === 'edge' || doc.box.tuning.m3key === 'm3empty' || doc.box.tuning.mmm,
		//m3table_w3: doc => !d3d(doc) || doc.box.tuning.m3key === 'edge' || !doc.box.tuning.mmm,
		//m3t: doc => !doc.box || doc.box.tuning.m3key !== 'm3t',

		
		// общие поля rooms
		is3d0: doc => !d3d(doc) || doc.box.parent3d.tuning.mmm !== 'rooms',
		
		// свойства rooms: ширина, длина, высота, Толщина стен
		is3d1: doc => d3d(doc, 'bb3d') !== 0 || doc.box.tuning.mmm !== 'rooms',
		
		// fixes, lineOff, insideOff
		is3d4: doc => d3d(doc, 'mmm') !== 'rooms',
		
		furniture : doc => d3d(doc, 'mmm') !== 'rooms' || doc.box.parent3d.tuning.bb3d !== 2 || doc.box.parent3M,
		
		// Показать Все стены | Только одну
		wedWall: doc => !d3d(doc) || !doc.box.parent3d.tuning.bb3d,
		walls: doc => d3d(doc, 'bb3d') !== 1 || !doc.box.tuning.wall,
		
		//одинокий bricks
		bricksOne: doc => !d3d(doc) || !(doc.box.tuning.mmm === 'brick' || (doc.box !== doc.box.parent3d && doc.box.tuning.mmm === 'm3table' && !doc.box.tuning.wall)) || doc.box.tuning.wed === 1, // покаzать пусто когда wed2
		//bricksOne: doc => !d3d(doc) || doc.box.tuning.mmm !== 'brick' || doc.box.tuning.wed === 1, // покаzать пусто когда wed2
		bricksOne2: doc => !d3d(doc) || doc.box.parent3d !== doc.box,
		bricksOne3: doc => !d3d(doc) || doc.box.parent3d === doc.box || !(doc.box.tuning.mmm === 'brick' || (doc.box.tuning.mmm === 'm3table' && !doc.box.tuning.wall)) || doc.box.tuning.wed === 1, // покаzать пусто когда wed2
		bricksOne4: doc => !d3d(doc) || doc.box.tuning.mmm !== 'brick',

		//brick_scale3d: doc => !doc.box || doc.box.tuning.mmm !== 'brick' || doc.getField('noBrickScale'),
		// bricks in the wall
		bricksM3t: doc => !d3d(doc) || !doc.box.parent3T || doc.box.tuning.m3key !== 'm3t' || doc.box.parent3T.tuning.wed === 2, // покаzать пусто когда wed2
//		bricksM3t: doc => !d3d(doc) || !doc.box.parent3T || !['m3t', 'm3table'].includes(doc.box.tuning.m3key) || doc.box.parent3T.tuning.wed === 2, // покаzать пусто когда wed2
		
		bricksEdge: doc => !doc.box || doc.box.tuning.m3key !== 'edge' || (doc.box.parent3T && !(doc.box.parent3T === doc.box.parentBox.getFloat && doc.box.parent3T.tuning.wall)),
		
		// поле фасад/грани для стены
		wall_wed: doc => d3d(doc, 'mmm') !== 'rooms' || !doc.box.parent3T || !doc.box.tuning.wall, // иначе m3table_wed

		//bricks2: doc => !d3d(doc) || doc.box.tuning.mmm === 'rooms' || doc.box.tuning.wall || doc.box.tuning.m3key === 'm3empty',

		// скрывать у кирпича ширину/высоту, если он в таблице
		m3t_is3dX: doc => !doc.box || !doc.box.column,
		m3t_is3dY: doc => !doc.box || !doc.box.row,

		// запретить менять размер ячейки при изменении размеров таблицы (пусть меняется предыдущая). Скрыть если размер в процентах
		m3t_fixed: doc => !doc.box || doc.box.tuning.metric,

		mmmNotRooms: doc => !d3d(doc) || doc.box.parent3T !== doc.box.parent3d,
		mmmNotRooms2: doc => !d3d(doc) || doc.box.tuning.mmm !== 'm3table',

		make3d: doc => !doc.box || doc.box.cells.length || doc.box.boxes.length || doc.box.tuning.boxContentQQ || doc.box.tuning.m3key === 'edge',
		winDoor: doc => !doc.box || !doc.box.tuning.wall,
		// поворот стены, сдвиг стены
		rotShift: doc => !d3d(doc) || doc.box.tuning.mmm || ['top', 'ground'].includes(doc.box.tuning.wall),
		rotGr: doc => !d3d(doc) || doc.box.tuning.mmm || doc.box.tuning.wall !== 'ground',
		// наклон потолка
		rshTop: doc => !d3d(doc) || doc.box.tuning.mmm || doc.box.tuning.wall !== 'top',
		
		// тень
		shadow3: doc => !d3d(doc) || doc.box.parent3d.tuning.mmm !== 'rooms' || !doc.box.parent3d.tuning.hide31,

		// масштаб
		hide33: doc => !d3d(doc) || !doc.box.parent3d.tuning.hide33,
		m3table_hide33: doc => !d3d(doc) || !doc.box.parent3d.tuning.hide33,
		brick_hide35: doc => !d3d(doc) || !doc.box.parent3d.tuning.hide35,



		// Размеры, наклон стен, переспектива
		perspective: doc => !d3d(doc) || !(doc.box.parent3d.tuning.mmm === 'rooms' ? doc.box.parent3d.parentBox : doc.box.parent3d).tuning['persOn'],

		copyDel3d2: doc => !doc.box || !doc.box.tuning.mmm,
		paste2d: doc => !doc.box || doc.box.clip.boxClipboard() !== '2d' || doc.box.type,
		paste3d: doc => !doc.box || doc.box.clip.boxClipboard() !== '3d' || doc.box.type || doc.box.tuning.m3key === 'm3empty',
    },
 
	//*** *** ***

	recalc: {
		SET_TABLE_FD: doc => doc.forceUpdate(),
		SCRIPTDELAY: (doc, val) => {
			let arr = [10, 500, 1000, 2000, 5000, 10000];
			doc.rootBox.clip.toHist(doc.rootBox, 'old:tuning', 'interval');
			doc.rootBox.tuning.interval = arr[val || 0];
			doc.rootBox.clip.toHist(doc.rootBox, 'new:tuning', 'interval');
			window.playScript && clearInterval(window.playScript);
			doc.pageBox.tuning.playScript && startScript(doc);
		},
		PLAYSCRIPT: (doc, val) => {
			doc.pageBox.tuning.playScript = val;
			if (val) {
				doc.stopScript = null;
				if (val === 'play')
					doc.rootBox.clip.peak = 0;
				doc.box.clip.histArr.length && startScript(doc);
			}
			else {
				doc.stopScript = true;
				window.playScript && clearInterval(window.playScript);
				doc.forceUpdate();
			}
		},
		
		KITCHEN: (doc, val) => furniture(doc, 'Мебель для кухни', val, ''),
		KITCHENS: (doc, val) => {},
		ROOM: (doc, val) => furniture(doc, 'Мебель для комнаты', val, ''),
		ROOMS: (doc, val) => {},
		
		SCREEN: (doc, val) => {
			let newRootBox = doc.pageBox.changeScreen(val);
			if (newRootBox)
				doc.setField('pagePlusDim', newRootBox.tuning.pagePlusDim || 2);
		},
		
		GRIDX: (doc, val) => {doc.rootBox.tuning.gridX = val; doc.rootBox.forceUpdate()},
		GRIDY: (doc, val) => {doc.rootBox.tuning.gridY = val; doc.rootBox.forceUpdate()},
		PHONECONTUR: (doc, val) => {doc.rootBox.tuning.phoneContur = val; doc.rootBox.forceUpdate()},
		PAGEPLUSPREVIEW: (doc, val) => {doc.rootBox.tuning.pagePlusPreview = val; doc.rootBox.forceUpdate()},
		PAGEPLUSDIM: (doc, val) => {doc.rootBox.tuning.pagePlusDim = val; doc.rootBox.forceUpdate()},

		RECTLEFT: (doc, val, noHist) => _setLeftTop(doc.box, 'left', val, noHist),
		RECTTOP: (doc, val, noHist) => _setLeftTop(doc.box, 'top', val, noHist),
		BOXSIZEX: (doc, val) =>  _setBoxSize(doc.box, val, 0),
		BOXSIZEY: (doc, val) => _setBoxSize(doc.box, 0, val),


		
		// M3TABLE_ - одинокий кирпич, одинокая таблица
		// M3T_ - кирпич в стене
		BRICK_LEFT: (doc, val, noHist, toHist, sl) =>  setBricksLeftTop(doc, 'brick_left', val, noHist, toHist, sl),
		BRICK_TOP:  (doc, val, noHist, toHist, sl) =>  setBricksLeftTop(doc, 'brick_top', val, noHist, toHist, sl),
		
		
		M3TABLE_IS3DX: (doc, val) => _setBoxSize(doc.box, val, 0),
		TUMBA_IS3DX: (doc, val) => _setBoxSize(doc.box, val, 0),
		M3T_IS3DX: (doc, val) => _setBoxSize(doc.box, val, 0),
		W_IS3DX: (doc, val) => _setBoxSize(doc.box, val, 0),
		BRICK_IS3DX: (doc, val) => _setBoxSize(doc.box, val, 0),

		
		M3TABLE_IS3DY: (doc, val) => _setBoxSize(doc.box, 0, val),
		TUMBA_IS3DY: (doc, val) => _setBoxSize(doc.box, 0, val),
		M3T_IS3DY: (doc, val) => _setBoxSize(doc.box, 0, val),
		W_IS3DY: (doc, val) => _setBoxSize(doc.box, 0, val),
		BRICK_IS3DY: (doc, val) => _setBoxSize(doc.box, 0, val),


		M3T_IS3DZ: (doc, val, noHist, toHist, sl) => setBricksM3t(doc, 'm3t_is3dZ', val, noHist, toHist, sl),
		BRICK_IS3DZ: (doc, val, noHist, toHist, sl) => setBricksM3t(doc, 'brick_is3dZ', val, noHist, toHist, sl),
		M3TABLE_IS3DZ: (doc, val, noHist, toHist, sl) => mmm3tFeature(doc, 'm3table_is3dZ', val, noHist, toHist, sl),
		TUMBA_IS3DZ: (doc, val, noHist, toHist, sl) => mmm3tFeature(doc, 'm3table_is3dZ', val, noHist, toHist, sl),
		W_IS3DZ: (doc, val, noHist, toHist, sl) => setWallTranslate(doc, 'is3dZ', val, noHist, toHist, sl),
		W_SKEWY: (doc, val, noHist, toHist, sl) => setWallTranslate(doc, 'skewY', val, noHist, toHist, sl),

		
		CM2D: (doc, val, noHist) => {
			if (val && !noHist && doc.box && doc.box.getFloat.tuning.cm2d !== val) {
				doc.box.clip.toHist(doc.box.getFloat, 'cm2d');
				doc.box.setScale(doc.box.getFloat, val);
			}
		},
		BRICK_CM: (doc, val, noHist, toHist, sl) => setBricksM3t(doc, 'brick_cm', val, noHist, toHist, sl),
		SCALE2D: (doc, val, noHist, toHist, sl) => doc.box && scale(doc.box.getFloat, val, noHist, sl, 'scale2d'),
		SCALE3D: (doc, val, noHist, toHist, sl) =>         doc.box && doc.box.parent3d && scale(doc.box.parent3d, val, noHist, sl, 'scale3d'),
		BRICK_SCALE3D: (doc, val, noHist, toHist, sl) =>   doc.box && doc.box.parent3d && scale(doc.box.parent3d, val, noHist, sl, 'scale3d'),
		M3TABLE_SCALE3D: (doc, val, noHist, toHist, sl) => doc.box && doc.box.parent3d && scale(doc.box.parent3d, val, noHist, sl, 'scale3d'),

		BRICK_WED: (doc, val, noHist, toHist, sl) => setBricksM3t(doc, 'brick_wed', val, noHist, toHist, sl),
		M3TAB_WED: (doc, val, noHist, toHist, sl) => {
					let box = doc.box;
			let p3t = box && box.parent3T;
			let tu = p3t && p3t.tuning;
			
			if ( !tu || !(tu.wed !== val || toHist === true))
				return;

			box.clip.toHist(p3t, 'tuning', 'wed');
			tu.wed = val;

			if (val === 0) { // выбрать стену
				p3t.setWrap();
				return;
			}
			if (val === 1) {  // выбрать фасад
				if (box.tuning.m3key === 'edge')
						box.parentBox.setWrap(); //выбрать фасад
				else if (box.tuning.m3key === 'm3t')
						box.setWrap(); //выбрать фасад при выбранном фасаде
				else // if (box.tuning.m3key === 'm3empty')
						p3t.forceUpdate(); //выбрать что-нибудь
				return;
			}
			
			// выбрать грань (val === 2)
			p3t.forceUpdate();
		},
		
		
		MMM_FIXED: (doc, val, noHist) => {
			if (d3d(doc) && !noHist) {
				let p3d = doc.box.parent3d.parentBox;
				if (p3d.tuning.fixed !== val) {
					p3d.clip.toHist(p3d, 'old:tuning', 'fixed');
					p3d.tuning.fixed = val;
					p3d.clip.toHist(p3d, 'new:tuning', 'fixed');
				}
			}
		},
		
		BRICK_TURNON: (doc, val) => window._turnOn(doc, val),
		M3TABLE_TURNON: (doc, val) => window._turnOn(doc, val),
		TURNON: (doc, val) => window._turnOn(doc, val),

		ARROWTYPE: (doc, val) => {
			if (!doc.box || val === (doc.box.tuning.arrowType || 0))
				return;
			let box = doc.box;

			box.clip.toHist(box, 'tuning', 'arrowType');

			let tu = box.tuning;
			let l = (tu.x1 + tu.y1)/4; // Math.max(Math.abs(tu.x1 - tu.x2), Math.abs(tu.y1 - tu.y2));
			switch(val) {
				case 4:
					tu.x2 = tu.x1 + l;
					tu.y2 = tu.y1 - l;
					break;
				case 0:
				case 2:
					if (tu.x2 === tu.x1)
						tu.x2 = tu.x1 + l;
					tu.y1 = tu.y2;
					break;
				case 1:
				case 3:
					if (tu.y1 === tu.y2)
						tu.y1 = tu.y2+l;
					tu.x1 = tu.x2;
					break;
			}
			tu.x3 = tu.x2 + 60;
			tu.y3 = tu.y1 + 60;
			tu.arrowType = val;
			box.setWrap();
		},

		WALL_WED: (doc, val, noHist, toHist) => {
			let box = doc.box;
			let p3t = box && box.parent3T;
			let tu = p3t && p3t.tuning;
			
			if ( !tu || !(tu.wed !== val || toHist === true))
				return;

			box.clip.toHist(p3t, 'tuning', 'wed');
			tu.wed = val;

			if (val === 0) { // выбрать стену
				p3t.setWrap();
				return;
			}
			if (val === 1) {  // выбрать фасад
				if (box.tuning.m3key === 'edge')
						box.parentBox.setWrap(); //выбрать фасад
				else if (box.tuning.m3key === 'm3t')
						box.setWrap(); //выбрать фасад при выбранном фасаде
				else // if (box.tuning.m3key === 'm3empty')
						p3t.forceUpdate(); //выбрать что-нибудь
				return;
			}
			
			// выбрать грань (val === 2)
			p3t.forceUpdate();
		},

		BRICKEDGE_WED: (doc, val, noHist, toHist) => {
			let p3t = doc.box && doc.box.parentBox;
			let tu = p3t && p3t.tuning;
			
			if (!tu || !(tu.wed !== val || toHist === true))
				return;

			p3t.clip.toHist(p3t, 'tuning', 'wed');
			tu.wed = val;

			if (val === 0) // выбрать фасад
				p3t.setWrap();
		},

	
	}, // end of recalc
	// ***
	
	cmd: {
		clrUrl: doc => {
			doc.box.clip.toHist(doc.box, 'tuning', 'backgroundImage');
			doc.setField('backgroundImage', '');
		},
		imgFromBuf: doc => {
			navigator.clipboard.readText()
  				.then( clipText => {
					doc.box.clip.toHist(doc.box, 'tuning', 'backgroundImage');
					doc.setField('backgroundImage', clipText);
				})
				.catch( () => {} );
		},
		openImg: (doc, path) => {
			let mainDoc = doc.page.props.owner;
			let pageName = 'Pictures';
			let page = mainDoc.sovaPagesByName[pageName];
			page && page.closePage();
			let rect = doc.util.getRect(mainDoc, 80, 80);
			rect.width = Math.min(rect.width, 1200);
			let img = {
				dbAlias: 'dba',
				unid: 'unid',
				pageName,
				title: pageName,
				rsMode: 'preview',
				min: true,
				newForm: `img&key=${path}`,
				frameStyle: rect,
				modal: 1,
			}
			doc.util.addChildPage(mainDoc, img);
		},
		winDoor: (doc, win) => {
			let mainDoc = doc.page.props.owner;
			if (!doc.mainDoc.rootBox.findWrap(doc.mainDoc.rootBox))
				return alert('Стена не выбрана');

			let page = {
				title: 'окно/дверь',
				dbAlias: mainDoc.dbAlias,
				addUrl: '&key_project=Room-templates',
				mode: 'preview',
				form: 'a_design',
			};
			mainDoc.previewNew(page);
		},

		copy3d: doc => doc.box.clip.copyItem(doc.box.parent3d),
		f_copy3d: doc => doc.box.clip.copyItem(doc.box),
		copy3d2: doc => doc.box.clip.copyItem(doc.box.parent3d),
		paste3d: doc => doc.box.clip.pasteItem(doc.box, true, 1), // true - insert float + paste item,  1 - furniture
		del3d: doc => doc.box.clip.deleteItem(doc.box.parent3d),
		f_delete3d: doc => doc.box.clip.deleteItem(doc.box),
		del3d2: doc => doc.box.clip.deleteItem(doc.box.parent3d),
		make3d: doc => {
			let p3d = doc.box.getFloat;
			p3d.clip.toHist(p3d, 'make3d_parent3d');
			p3d.clip.make3d(doc.box);
			p3d.rebuild = 'new-m3t';
			p3d.setWrap();
		},
		
		addWall: doc => {
			let oldSide_0 = doc.box; // side_0: far, left...
//			if (oldSide_0.tuning.wall === 'ground')
//				return doc.mainDoc.msg.ok('\n\nДобавьте 3d-объект в режиме "Мебель".', 'Создание стен|Добавить пол невозможно.');

			let oldSide = oldSide_0.parentBox; // создаем из side, а не из side_0
			let p3d = oldSide.parent3d;
			let shift = p3d.tuning.cm === 'mm' ? 500 : 50;
			p3d.clip.toHist(p3d, 'double_parent3d');

			let side = {rect: {...oldSide.rect}, className: oldSide.className, tuning: {...oldSide.tuning}};
			let side_0 = {rect: {...oldSide_0.rect}, className: oldSide_0.className, tuning: {...oldSide_0.tuning}};

			side_0.tuning.changed = 1;
			side_0.tuning.m3key = 'wall';
			side_0.rect.width *= 0.5;
			if (side_0.tuning.wall === 'top')
				side_0.tuning.w_shiftTop = shift;
			else {
				side_0.tuning.w_shift = shift;
				side_0.tuning.translateZ = shift;
			}

			side.boxes = [side_0];
			p3d.boxes.push(side);
			
			p3d.rebuild = 'parent3d';
			p3d.forceUpdate();
			setTimeout( () => p3d.floatBoxes.at(-1).floatBoxes[0].setWrap(), 300);
		},

		blPlus: doc => { // увеличить z-index
			let p = doc.box.parentBox;
			let i = Number(doc.getField('boxLayer'));
			if ( i < p.boxes.length - 1 ) {
				p.clip.toHist(p, 'boxLayer');
				let t = p.boxes[i+1];
				p.boxes[i+1] = p.boxes[i];
				p.boxes[i] = t;
				t = p.floatBoxes[i+1];
				p.floatBoxes[i+1] = p.floatBoxes[i];
				p.floatBoxes[i] = t;
				doc.setField('boxLayer', (i+1).toString());
				p.forceUpdate();
			}
		},
		blMinus: doc => { // уменьшить z-index
			let p = doc.box.parentBox;
			let i = Number(doc.getField('boxLayer'));
			if ( i ) {
				p.clip.toHist(p, 'boxLayer');
				let t = p.boxes[i-1];
				p.boxes[i-1] = p.boxes[i];
				p.boxes[i] = t;
				t = p.floatBoxes[i-1];
				p.floatBoxes[i-1] = p.floatBoxes[i];
				p.floatBoxes[i] = t;
				doc.setField('boxLayer', (i-1).toString() );
				p.forceUpdate();
			}
		},
		
		deleteLine: doc => doc.box.clip.deleteItem(doc.box),
				
	},

};
// *** *** ***

let recalc = window.sovaActions.a_setting.recalc;

// *** *** ***

let setBoxFeatureCheck = (doc, feature, val, noHist, toHist, sl) => { // recalc для бордюра с проверкой ширины
	let box = testSBF(doc, feature, val, toHist);
	if (!box || box.cells.length)
		return;

	let v = box.testTuning(feature, val);
	if (v) {
		if (v === true || v === val) {
			writeHist(box, feature, val, noHist, sl);
			box.forceUpdate();
		}
		else
			doc.setField(feature, v); // setFied вызовет recalc еще раз, но toHist
	}
};
// *** *** ***
// *** *** ***

let setBoxFeature = (doc, feature, val, noHist, toHist, sl) => {
	let box = testSBF(doc, feature, val, toHist);
	if (box) {
		writeHist(box, feature, val, noHist, sl);
		if (feature === 'linked')
			box.setWrap();
		else
			box.forceUpdate();
	}
};

// recalc с перериcовкой settingPage (для chb/chb3/band), setBoxFeature возвращает undefined
for (let it of recalcWithRedraw) {
	let fi = it.split('|')[0];
	recalc[fi.toUpperCase()] = (doc, val, noHist, toHist, sl) => setBoxFeature(doc, fi, val, noHist, toHist, sl) || doc.forceUpdate();
}

/*
for (let it of colorFeatures) { // recalc с частичной перериcовкой settingPage
	let fi = it.split('|')[0];
	let redraw = ['bgStyle', 'gradient'].includes(fi); // recalc  с перериcовкой settingPage (для chb/chb3)
	recalc[fi.toUpperCase()] = (doc, val, noHist, toHist, sl) => setColorFeature(doc, fi, val, noHist, toHist, sl) || (redraw && doc.forceUpdate());
}
*/

// recalc без перериcовки settingPage
for (let arr of [arrowFeatures, textFeatures, recalcOnly]) {
	for (let it of arr) {
		let fi = it.split('|')[0];
		recalc[fi.toUpperCase()] = (doc, val, noHist, toHist, sl) => setBoxFeature(doc, fi, val, noHist, toHist, sl)
	}
}

// recalc для бордюра
for (let side of ['', 'Top', 'Right', 'Bottom', 'Left']) // все, кроме borderWidth
	for (let it of [`border${side}Radius`, `border${side}RadiusMetric`, `border${side}Color`, `border${side}Style`])
		recalc[it.toUpperCase()] = (doc, param, noHist, toHist, sl) => setBoxFeature(doc, it, param, noHist, toHist, sl);

// recalc для бордюра с проверкой ширины (borderWidth)
for (let side of ['', 'Top', 'Right', 'Bottom', 'Left'])
	recalc[`border${side}Width`.toUpperCase()] = (doc, param, noHist, toHist, sl) => setBoxFeatureCheck(doc, `border${side}Width`, param, noHist, toHist, sl);

// *** 3d ***

let parent3dFeature = (doc, feature, val, noHist, toHist, sl) => { // for (let arr of mmmCommon, mmmRoomsCommon, mmmRoomsFull)
	let box = doc.box;
	let p3d = box && box.parent3d;
	let tu = p3d && p3d.tuning;

	if (!tu)
		return;

	let typeHist = 'tuning_parent3d';

	if (feature === 'rotate3X') {
		val = 90 - val;

		if (val === tu[feature] && toHist !== true)
			return;
		
		if (noHist !== true) {
			if (sl !== undefined)
				tu[feature] = 90 - sl;
			box.clip.toHist(p3d, typeHist, feature);
		}
		tu[feature] = val;
		p3d.rebuild = 'parent3d';
		p3d.forceUpdate();
		return;
	}
	
	if (val === tu[feature] && toHist !== true)
		return;
	
	if (['hide31', 'hide32', 'hide33'].includes(feature)) { // 31-Тень, 32-grid, 33-scale3d
		box.clip.toHist(p3d, 'old:tuning', feature);
		tu[feature] = val;
		box.clip.toHist(p3d, 'new:tuning', feature);
		doc.forceUpdate();
		return;
	}

	if (feature === 'bb3d') {
		box.clip.toHist(p3d, 'bb3d_parent3d', feature);
		p3d.rebuild = 'parent3d';
		tu[feature] = val;
		if (val === 0 && box !== p3d)
			p3d.setWrap();
		else {
			p3d.floatBoxes[tu.lastWall || 0].floatBoxes[0].wrap = true;
			p3d.floatBoxes[tu.lastWall || 0].floatBoxes[0].setWrap();
		}
		return;
	}
	
	if (feature === 'cm') { // tu[feature] = val присваивается внутри фукнции setScale
		box.clip.toHist(p3d, 'cm_parent3d', feature);
		p3d.setScale(p3d, val);
		p3d.rebuild = 'parent3d';
		p3d.setWrap();
		return;
	}
	
	if (['is3dX', 'is3dY', 'is3dZ'].includes(feature))
		return noHist !== true && _saveWH(p3d, feature, val);

	if (feature === 'shadowW3') {
		tu.shadow3 = val ? 'inside' : null;
		typeHist = 'shadow_parent3d';
	}

	if (noHist !== true) {
		if (sl !== undefined)
			tu[feature] = sl;
		box.clip.toHist(p3d, typeHist, feature);
	}

	tu[feature] = val;

	if (feature === 'rotate3Z') {
		p3d.rebuild = 'rotate';
		p3d.forceUpdate();
	}
	else {
		p3d.rebuild = 'parent3d';
		p3d.forceUpdate();
	}
};

// *** *** ***

let setWallLeftTop = (doc, feature, val, noHist, toHist, sl) => {
	let box = testSBF(doc, feature, val, toHist);
	if (!box || !box.tuning.wall)
		return;

	if (noHist !== true) {
		if (sl !== undefined)
			box.tuning[feature] = sl;
		box.clip.toHist(box, 'tuning_wall', feature);
	}

	box.tuning[feature] = val;
	box.tuning.changed = feature; // чтобы не обновлять wall при смене размеров parent3d
	box.rebuild = 'wall';
	box.setWrap();
};
	
let setWallTranslate = (doc, feature, val, noHist, toHist, sl) => { // тюнинг cтены: 'w_rotate', 'w_shift',
	let box = testSBF(doc, feature, val, toHist);
	if (!box || !box.tuning.wall)
		return;

	let tu = box.tuning;  // tu = side_0.tuning
	
	if (noHist !== true) {
		if (sl !== undefined) {
			tu[feature] = sl;
			if (feature === 'w_rotate' || feature === 'w_rotateGr') {
				switch (tu.wall) {
					case 'far': tu.rotate3Y = -sl; break;
					case 'door': tu.rotate3Y = sl; break;
					case 'left': tu.rotate3X = -sl; break;
					case 'right': tu.rotateY = -sl; break;
					case 'ground': tu.rotateZ = sl; break;
				}
			}
			else if (feature === 'w_shift' || feature === 'w_shiftGr')
				tu.translateZ = sl;

			else if (tu.wall === 'top' && feature === 'w_rotateTop2')
				tu.rotate3Y = sl;
		}
		box.clip.toHist(box, 'rotShift_wall', feature);
	}
	
	tu[feature] = val;
	if (feature === 'w_shiftTop') {
		box.parent3d.rebuild = 'wall';
		box.parent3d.forceUpdate();
		return;
	}

	if (feature === 'w_rotate' || feature === 'w_rotateGr') {
		switch (tu.wall) {
			case 'far': tu.rotate3Y = -val; break;
			case 'door': tu.rotate3Y = val; break;
			case 'left': tu.rotate3X = -val; break;
			case 'right': tu.rotateY = -val; break;
			case 'ground': tu.rotateZ = val; break;
		}
	}
	else if (feature === 'w_shift' || feature === 'w_shiftGr')
		tu.translateZ = val;

	else if (tu.wall === 'top' && feature === 'w_rotateTop2')
		tu.rotate3Y = val;

	box.rebuild = 'wall';
	box.forceUpdate();
};

let mmm3tFeature = (doc, feature, val, noHist, toHist, sl) => { // 'm3table_rotate3X', 'm3table_rotate3Y', 'm3table_wed' и драгие m3table_
	let box = doc.box;
	let p3d = box && (box.parent3T || box.parent3d);
	if (!p3d)
		return;

	feature = feature.split('_')[1];
	let tu = p3d.tuning;
	
	if (tu[feature] === val && toHist !== true)
		return;
	
	let typeHist = 'tuning_m3t';
	if (feature === 'cm') {
		if (p3d !== box.parent3d)
			return;
		typeHist = 'cm_parent3d';
	}

	if (noHist !== true) {
		if (sl !== undefined)
			tu[feature] = sl;
		box.clip.toHist(p3d, typeHist, feature);
	}
	
	if (feature === 'cm')
		p3d.setScale(p3d, val);
	else
		tu[feature] = val;


	if (feature === 'wed') {
		if (val === 0) // выбрать стену
			p3d.setWrap();
		else if (val === 1) {  // выбрать фасад
			if (box.tuning.m3key === 'edge')
				box.parentBox.setWrap(); //выбрать фасад
			else if (box.tuning.m3key === 'm3t')
				box.setWrap(); //выбрать фасад при выбранном фасаде
			else // if (box.tuning.m3key === 'm3empty')
				p3d.forceUpdate(); //выбрать что-нибудь
		}
		else // выбрать грань (val === 2)
			p3d.forceUpdate();
	}
	else {
		p3d.rebuild = 'm3table';
		p3d.forceUpdate();
	}
	if (feature === 'hide33')
		doc.forceUpdate();
};


let setBricksLeftTop = (doc, feature, val, noHist, toHist, sl) => {
	let box = doc.box;
	let leftTop = feature.split('_')[1];
	
	if (!box || (box.rect[leftTop] === val && toHist !== true))
		return;

	if (noHist !== true) {
		if (sl !== undefined) {
			box.clip.toHist(box, 'old:Move-c-0');
			box.toHistAfterRender = 'new:Move-c-0';
		}
	}
	if (box.tuning.insideOnly) {
		if (val < 0)
			val = 0;
		else if (leftTop === 'left' && val + box.rect.width  > box.parentBox.rect.width)
			val = box.parentBox.rect.width - box.rect.width;
		else if (leftTop === 'top'  && val + box.rect.height > box.parentBox.rect.height)
			val = box.parentBox.rect.height - box.rect.height;
	}
	box.rect[leftTop] = val;
	box.setWrap();
};
		
let setBricksM3t = (doc, feature, val, noHist, toHist, sl) => {
	let tun = feature.split('_')[1];
	let box = testSBF(doc, tun, val, toHist);

	if (box) {
		let mmm = box.parent3T || box.parent3d;
		if (noHist !== true) {
			if (sl !== undefined)
				box.tuning[tun] = sl;
			box.clip.toHist(box, feature === 'brick_cm' ? 'cm_brick': 'tuning_brick', tun);
		}

		if (feature === 'brick_cm')
			box.setScale(box, val);
		else
			box.tuning[tun] = val;
		
		if (['metric', 'fixed'].includes(tun))
			box.setWrap();
		else {
			if (mmm)
				mmm.rebuild = 1;
			else
				console.log(`gluck in setBricksM3t. BI=${box.boxIndex} ${feature}`);
			box.setWrap();
		}
	}
};



let setTumba = (doc, feature, val, noHist, toHist, sl) => {
	let box = testSBF(doc, feature, val, toHist);
	if (!box)
		return;
	
	feature = feature.split('_')[1];
	
	if (noHist !== true) {
		if (sl !== undefined)
			box.tuning[feature] = sl;
		box.clip.toHist(box, 'tuning_1', feature);
	}
	
	if (['left', 'top', 'bottom'].includes(feature)) {
		let [leftMin, leftMax] = [0, box.parentBox.rect.width-box.rect.width];
		let [topMin, topMax] = [0, box.parentBox.rect.height - box.rect.height];
		let dv = 0;
		if (box.parentBox.tuning.wall === 'ground') {
			let angle = box.tuning.rotate3Y;
			if (-45 <= angle && angle <= 45) {
				if (feature === 'top') {
					topMin = box.tuning.is3dZ;
					topMax = box.parentBox.rect.height;
					val += box.tuning.is3dZ;
					dv = box.tuning.is3dZ;
				}
			}
			if (135 < angle || angle < -135) {
				if (feature === 'top')
					topMax = box.parentBox.rect.height-box.tuning.is3dZ;
				else if (feature === 'left') {
					leftMin = box.rect.width;
					leftMax = box.parentBox.rect.width;
					val += box.rect.width;
					dv = box.rect.width;
				}
			}
			else if (box.tuning.rotate3Y > 45) {
				if (feature === 'top') {
					topMin = box.rect.width;
					topMax = box.parentBox.rect.height;
					val += box.rect.width;
					dv = box.rect.width;
				}
				else if (feature === 'left') {
					leftMin = box.tuning.is3dZ;
					leftMax = box.parentBox.rect.width;
					val += box.tuning.is3dZ;
					dv = box.tuning.is3dZ;
				}
			}
			else if (box.tuning.rotate3Y < -45) {
				if (feature === 'top')
					topMax = box.parentBox.rect.height-box.rect.width;
				else if (feature === 'left')
					leftMax = box.parentBox.rect.width-box.tuning.is3dZ;
			}
		}
		if (feature === 'left') {
			box.rect.left = val < leftMin ? leftMin : val > leftMax ? leftMax : val;
			val = box.rect.left - dv;

		}
		else if (feature === 'top') {
			box.rect.top = val < topMin ? topMin : val > topMax ? topMax : val;
			val = box.rect.top - dv;
			let bottom = val < topMin ? topMin : val > topMax ? topMax : val;
			box.tuning.bottom = bottom;
		}
		else { // bottom
			val = val < topMin ? topMin : val > topMax ? topMax : val;
			box.rect.top = topMax - val;
			let top = box.rect.top - dv;
			box.tuning.top = top;
		}
	}

	box.tuning[feature] = val;
//	box.setWrap();
	box.forceUpdate();
};

for (let arr of [mmmCommon, mmmRoomsCommon, mmmRoomsFull]) {
	for (let it of arr) {
		let fi = it.split('|')[0];
		recalc[fi.toUpperCase()] = (doc, val, noHist, toHist, sl) => parent3dFeature(doc, fi, val, noHist, toHist, sl)
	}
}

for (let it of tumba) {
	let fi = it.split('|')[0];
	recalc[fi.toUpperCase()] = (doc, param, noHist, toHist, sl) => setTumba(doc, fi, param, noHist, toHist, sl);
}

for (let it of mmmWalls) {
	let fi = it.split('|')[0];
	recalc[fi.toUpperCase()] = (doc, param, noHist, toHist, sl) => setWallTranslate(doc, fi, param, noHist, toHist, sl);
}

for (let it of ['w_left', 'w_top'])
	recalc[it.toUpperCase()] = (doc, param, noHist, sl) => setWallLeftTop(doc, it, param, noHist, sl);

for (let it of mmmM3T) {
	let fi = it.split('|')[0];
	recalc[fi.toUpperCase()] = (doc, param, noHist, toHist, sl) => mmm3tFeature(doc, fi, param, noHist, toHist, sl);
}

for (let it of bricksM3t) {
	let fi = it.split('|')[0];
	recalc[fi.toUpperCase()] = (doc, param, noHist, toHist, sl) => setBricksM3t(doc, fi, param, noHist, toHist, sl);
}


for (let it of bricks) {
	let fi = it.split('|')[0];
	recalc[fi.toUpperCase()] = (doc, param, noHist, toHist, sl) => setBricksM3t(doc, fi, param, noHist, toHist, sl);
}

// *** *** ***

let perspective = (doc, feature, val, noHist, toHist, sl) => {
	if (!d3d(doc) || !doc.box.parent3d.tuning.mmm)
		return;
	
	let p = doc.box.parent3d;
	if (p.tuning.mmm === 'rooms')
		p = p.parentBox;
	
	let tu = p.tuning;
	if (tu[feature] === val && toHist !== true)
		return;

	if (noHist !== true) {
		if (sl !== undefined)
			tu[feature] = sl;
	}

	tu[feature] = val;
	feature === 'persOn' && doc.forceUpdate();
	p.forceUpdate();
};
// *** *** ***

for (let it of ['persOn', 'perspective', 'perspectiveOriginX', 'perspectiveOriginY'])
	recalc[it.toUpperCase()] = (doc, param, noHist, toHist, sl) => perspective(doc, it, param, noHist, toHist, sl);




