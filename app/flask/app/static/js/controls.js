const Http = new XMLHttpRequest();

String.prototype.format = function() {
	a = this;
	for (k in arguments) {
		a = a.replace("{" + k + "}", arguments[k])
	}
	return a
}

var sliders = document.getElementsByClassName("slider");

const url = "http://192.168.1.31:5000/api/data"

for(const slider of sliders){
	slider.oninput = function() {
		var speed = this.value;
		var params = "id={0}&speed={1}".format(this.id - 1, speed);//Master id should be -1, other ids: 0, 1, 2, 3
		Http.open("GET", url + "/setmotorspeed" + "?" + params);
		Http.send();
	}
}

var info = document.getElementById("info");
function timeout() {
	setTimeout(function () {
		timeout();
	}, 1000/20);

	Http.open("GET", url + "/getrotation");
	Http.send()
	Http.onreadystatechange = function(){
		if(Http.readyState == 4){
			var a = JSON.parse(Http.responseText).position;
			var msg = "roll={0} pitch={1} yaw={2}".format(a[0].toFixed(5), a[1].toFixed(5), a[2].toFixed(5));
			info.innerHTML = msg;
		}
	}
}



timeout();

