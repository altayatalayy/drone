import * as THREE from '/static/js/three.module1.js';
import { OBJLoader } from '/static/js/OBJLoader.js';

let scene, camera, renderer, loader, model;
var controls;

let object;
function loadModel() {
	//const material = new THREE.MeshBasicMaterial( {color: 0x00ff00} );
	object.traverse(function (child){if(child.isMesh) child.material.color.setHex(0xffffff)});
	var box = new THREE.Box3().setFromObject(object);
	var center = new THREE.Vector3();
	let radius = box.getBoundingSphere(center).radius;
	let scale = 300/radius;

	object.scale.multiplyScalar(scale);
	object.position.sub(center)
	scene.add( object );
	object.rotation.set(0, 0, -3.14/4);
	var model_axis =  new THREE.AxesHelper(200);
	model_axis.rotation.set(0, 0, 3.14/4)
	object.add(model_axis);
}

function init(){
	const container = document.getElementById( 'canvas' );
	var h = container.clientHeight;
	var w = container.clientWidth;
	scene = new THREE.Scene();
	camera = new THREE.PerspectiveCamera(75, w/h, 0.1, 5000);
	renderer = new THREE.WebGLRenderer({antialias: true});
	var ambientLight = new THREE.AmbientLight( 0xffffff, 0.6 );
	scene.add( ambientLight );

	const manager = new THREE.LoadingManager( loadModel );
	manager.onProgress = function ( item, loaded, total ) {
		console.log( item, loaded, total );
	};
	loader = new OBJLoader(manager);


	renderer.setSize(w, h);
	//document.body.appendChild( container );
	container.appendChild( renderer.domElement );
	var plane = new THREE.GridHelper(500, 10);
	plane.rotation.set(3.14/2, 0, 0);
    scene.add(plane);
	loader.load('/static/models/Drone_assembly1_v1.obj', function( obj ){ object=obj});
	//model = new THREE.Mesh(object, material);

	camera.position.set(0,0,390);
	camera.lookAt(scene.position);
	//controls = new THREE.OrbitControls(camera, renderer.domElement);
}

const Http = new XMLHttpRequest();

function animate(){
	setTimeout( function() {
		requestAnimationFrame(animate);
	}, 1000 / 10 );

	var x, y, z;
	const url = "http://192.168.1.25:5000/api/data/getrotation"
	//const url = "http://127.0.0.1:5000/api/data/getrotation"
	Http.open("GET", url)
	Http.send()
	Http.onreadystatechange = function(){
		if(Http.readyState == 4){
			var a = JSON.parse(Http.responseText).position;
			x = a[0];
			y = a[1];
			z = a[2];
			object.rotation.set(x, y, z - 3.14/4);
		}
	}
	
	renderer.render(scene, camera);
}

function onWindowResize(){
	const container = document.getElementById( 'canvas' );
	var h = container.clientHeight;
	var w = container.clientWidth;
	camera.aspect = w / h;
	camera.updateProjectionMatrix();
	renderer.setSize(w, h);
}

window.addEventListener('resize', onWindowResize, false);

init();
animate();
