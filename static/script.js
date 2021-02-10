function dotify(str) {
	let dots = '';
	for (let i = 0; i < str.length; i++) {
		dots += '•';
	}
	return dots;
}

function showOrHide(elem) {
	if (elem.previousElementSibling.innerHTML.replace(/•/gi, "").length === 0) {
		elem.previousElementSibling.innerHTML = elem.previousElementSibling['data-password'];
		elem.innerHTML = '<i class="fas fa-eye-slash"></i>'
	} else {
		elem.previousElementSibling.innerHTML = dotify(elem.previousElementSibling['data-password']);
		elem.innerHTML = '<i class="fas fa-eye"></i>'
	}
}

function copy(elem) {
	let text = elem.previousElementSibling.previousElementSibling['data-password'];
	elem.childNodes[1].style.display = 'block';
	let copy =  document.createElement('TEXTAREA');
	copy.innerHTML = text;
	document.body.appendChild(copy);
	copy.select();
	document.execCommand("copy");
	document.body.removeChild(copy);
	setTimeout(function(){ elem.childNodes[1].style.display = 'none'; }, 1000);
}

function randint(min, max) {
  return Math.floor(Math.random() * (max - min) ) + min;
}

function randomPassword(elem) {
	let password = ''
	for (let i = 0; i < 30; i++) {
		password += String.fromCharCode(randint(65,122))
	}
	console.log(password);
	elem.previousElementSibling['value'] = password;
}

let passwords = document.querySelectorAll(".password");

passwords.forEach(function(password) {
	password['data-password'] = password.innerHTML
	password.innerHTML = dotify(password.innerHTML);
});