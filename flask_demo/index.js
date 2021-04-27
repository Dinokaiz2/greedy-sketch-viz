const POINT_SIZE = 3;
const RED = "#ff0000";
const BLUE = "#0000ff";

let points = [];

document.getElementById("canvas").onclick = (event) => {
  let rect = canvas.getBoundingClientRect();
  let x = event.clientX - rect.left;
  let y = event.clientY - rect.top;

  points.push([x, y]);

  drawPoint(x, y, RED);
};

document.getElementById("run").onclick = (_event) => {
  let r = new XMLHttpRequest();
  r.open("POST", "/api/points", true);
  r.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  r.onreadystatechange = function () {
    if (this.readyState != 4 || this.status != 200) {
      return;
    }
    let points = JSON.parse(this.response);
    console.log("Success: " + this.responseText);
    for ([x, y] of points) {
      drawPoint(x, y, BLUE);
    }
  };
  r.send(JSON.stringify(points));
};

function drawPoint(x, y, color) {
  let ctx = document.getElementById("canvas").getContext("2d");

  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.arc(x, y, POINT_SIZE, 0, Math.PI * 2, true);
  ctx.fill();

  // ctx.font = "30px Arial";
  // ctx.fillText("Hello World", 10, 50);
}
