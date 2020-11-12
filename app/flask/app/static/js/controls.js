const Http = new XMLHttpRequest();

String.prototype.format = function() {
	a = this;
	for (k in arguments) {
		a = a.replace("{" + k + "}", arguments[k])
	}
	return a
}

var slider1 = document.getElementById("slider1");
var slider2 = document.getElementById("slider2");
var slider3 = document.getElementById("slider3");
var slider4 = document.getElementById("slider4");

const url = "http://192.168.1.25:5000/api/data/setmotorspeed"
slider1.oninput = function() {
	var speed = this.value;
	var params = "id={0}&speed={1}".format(0, speed);
	Http.open("GET", url+"?"+params);
	Http.send();
}


slider2.oninput = function() {
	var speed = this.value;
	var params = "id={0}&speed={1}".format(1, speed);
	Http.open("GET", url+"?"+params);
	Http.send();
}

slider2.oninput = function() {
	var speed = this.value;
	var params = "id={0}&speed={1}".format(2, speed);
	Http.open("GET", url+"?"+params);
	Http.send();
}

slider3.oninput = function() {
	var speed = this.value;
	var params = "id={0}&speed={1}".format(3, speed);
	Http.open("GET", url+"?"+params);
	Http.send();
}

