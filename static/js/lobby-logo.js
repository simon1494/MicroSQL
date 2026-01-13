/**
    A JavaScript implementation of the gif found here: http://gif.flrn.nl/post/106259683043
*/
window.requestAnimFrame = (function(){
  return window.requestAnimationFrame ||
    window.webkitRequestAnimationFrame ||
    window.mozRequestAnimationFrame ||
    function(callback){
      window.setTimeout(callback, 1000 / 60);
    };
})();

var rad = function(deg) {
  return deg * (Math.PI / 180);
};

var SCALE = 1.2;
var SLOW  = 1 / 6;

var InterruptedRing = function(ctx, x, y, radius, interruptions, sizeOfInterruption, color, velocity) {
  this.x = x;
  this.y = y;
  this.r = radius;
  this.i = interruptions;
  this.d = sizeOfInterruption;
  this.v = velocity;
  this.s = color;
  this.c = ctx;
  this.o = Math.floor(Math.random() * 360) * (velocity < 0 ? -1 : 1);
  this.l = Math.floor((360 - (interruptions * sizeOfInterruption)) / interruptions);
};

InterruptedRing.prototype.step = function() {
  this.o = ((this.o + this.v * SLOW) % 360);
};

InterruptedRing.prototype.render = function() {
  var p = 0;
  while (p < 360) {
    this.c.beginPath();
    this.c.arc(
      this.x,
      this.y,
      this.r * SCALE,
      rad(p + this.o),
      rad(p + this.o + this.l),
      false
    );
    this.c.lineWidth = 5 * SCALE;
    this.c.strokeStyle = this.s;
    this.c.stroke();
    this.c.closePath();

    p += (this.d + this.l);
  }
};

$(function() {
  var canvas = document.getElementById('animation');
  var context = canvas.getContext('2d');

  canvas.width  = 400 * SCALE;
  canvas.height = 400 * SCALE;

  var cx = 200 * SCALE;
  var cy = 200 * SCALE;

  var rings = [
    new InterruptedRing(context, cx, cy, 8,   1, 60, '#d53933', -2),
    new InterruptedRing(context, cx, cy, 17,  4, 30, '#1d909a', 1),
    new InterruptedRing(context, cx, cy, 26,  2, 15, '#e59c10', -1.5),

    new InterruptedRing(context, cx, cy, 35,  2, 10, '#d53933', 1.5),
    new InterruptedRing(context, cx, cy, 44,  4, 10, '#1d909a', -0.5),
    new InterruptedRing(context, cx, cy, 53,  2, 8,  '#e59c10', -1),

    new InterruptedRing(context, cx, cy, 62,  2, 6,  '#d53933', -1.6),
    new InterruptedRing(context, cx, cy, 71,  4, 6,  '#1d909a', -0.60),
    new InterruptedRing(context, cx, cy, 80,  2, 6,  '#e59c10', 1.1),

    new InterruptedRing(context, cx, cy, 89,  2, 6,  '#d53933', 1.05),
    new InterruptedRing(context, cx, cy, 98,  5, 6,  '#1d909a', -0.50),
    new InterruptedRing(context, cx, cy, 107, 3, 5,  '#e59c10', 0.9),

    new InterruptedRing(context, cx, cy, 116, 2, 5,  '#d53933', -0.9),
    new InterruptedRing(context, cx, cy, 125, 4, 5,  '#1d909a', 0.60),
    new InterruptedRing(context, cx, cy, 134, 6, 5,  '#e59c10', -0.40),
  ];

  var anim = function() {
    requestAnimFrame(anim);
    context.clearRect(0, 0, canvas.width, canvas.height);
    for (var i in rings) rings[i].step();
    for (var i in rings) rings[i].render();
  };

  anim();
});
