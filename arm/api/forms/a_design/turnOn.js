window._turnOn = (doc, val, box) => {
	val = val || 0;
	if (!box) {
		box = doc.box && doc.box.parent3d;
		if (!box || (box.turnOn || 0) === val)
			return;
		box.clip.toHist(box, 'tuning', 'turnOn');
	}
	else if ((box.turnOn || 0) === val)
		return;

	box.tuning.turnOn = box.turnOn = val;
	if (val) {
		box.tempRotate3Z = box.tuning.rotate3Z;
		box.tempRotate3Y = box.tuning.rotate3Y;

		box.interval = setInterval(() => {
			let d = 1;
			if (box.tuning.turnOn) {
				if (box.tuning.mmm === 'rooms') {
					box.tuning.rotate3Z += d;
					box.tuning.rotate3Z %= 360;
				}
				else {
					box.tuning.rotate3Y += d;
					box.tuning.rotate3Y %= 360;
				}
				box.rebuild = 'rotate';
				box.forceUpdate();
			}
			else
				clearInterval(box.interval);
		}, 70);
	}
	else {
		if (box.tuning.mmm === 'rooms') {
			box.tuning.rotate3Z = box.tempRotate3Z;
			doc.setField('rotate3Z', box.tempRotate3Z);
		}
		else if (box.tuning.mmm === 'brick') {
			box.tuning.rotate3Y = box.tempRotate3Y;
			doc.setField('brick_rotate3Y', box.tempRotate3Y);
		}
		else {
			box.tuning.rotate3Y = box.tempRotate3Y;
			doc.setField('m3table_rotate3Y', box.tempRotate3Y);
		}
		
		setTimeout( () => {
			box.rebuild = 'rotate';
			box.forceUpdate();
		}, 1);
	}
};
