const POINT_SIZE = 3;
const POINT_COLOR = "#ff0000";

const canvas = document.getElementById("canvas");
const run = document.getElementById("run");
const clear = document.getElementById("clear");
const animationContainer = document.getElementById("animation-container");

// Canvas height and width are guaranteed to be the same
const CANVAS_BUF_SIZE = canvas.width;

let points = [];

canvas.onclick = function (event) {
  console.log(event);

  let rect = canvas.getBoundingClientRect();
  // Internally, the canvas is always CANVAS_SIZE, so we have to rescale the
  // points accordingly
  let x = (event.clientX - rect.left) * (CANVAS_BUF_SIZE / rect.width);
  let y = (event.clientY - rect.top) * (CANVAS_BUF_SIZE / rect.height);

  console.log(x, y);
  // We want to record the points y-axis "naturally" (i.e. up means increasing)
  points.push([x, CANVAS_BUF_SIZE - y]);

  let ctx = canvas.getContext("2d");
  ctx.fillStyle = POINT_COLOR;
  ctx.fillRect(
    x - (POINT_SIZE - 1) / 2,
    y - (POINT_SIZE - 1) / 2,
    POINT_SIZE,
    POINT_SIZE
  );
};

clear.onclick = function (_event) {
  points = [];

  let ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);
};

run.onclick = function (_event) {
  let r = new XMLHttpRequest();
  r.open("POST", "/api/animate", true);
  r.setRequestHeader("Content-Type", "application/json;charset=UTF-8");

  r.onreadystatechange = function () {
    if (this.readyState !== 4 || this.status !== 200) {
      return;
    }
    let frames = JSON.parse(this.response);
    let img_id = "_anim_img";
    let slider_id = "_anim_slider";
    let loop_select_id = "_anim_loop_select";
    // This must be global
    anim = new Animation(frames, img_id, slider_id, 500.0, loop_select_id);
  };

  r.send(
    JSON.stringify({
      points: points,
      // TODO: Have input
      frames: 15,
    })
  );
};
