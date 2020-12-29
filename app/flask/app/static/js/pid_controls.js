
const Http = new XMLHttpRequest();

String.prototype.format = function() {
	a = this;
	for (k in arguments) {
		a = a.replace("{" + k + "}", arguments[k])
	}
	return a
}

var swt = document.getElementById("switch");

const url = "http://127.0.0.1:5000/api/data"

swt.onclick = function() {
	var state = this.checked ? 1 : 0;
	var params = "state={0}".format(state);//Master id should be -1, other ids: 0, 1, 2, 3
	Http.open("GET", url + "/setcontroller" + "?" + params);
	Http.send();
}
