// Crosshair and tooltip for the server-rendered line chart.
document.querySelectorAll("figure.chart").forEach((figure) => {
  const points = JSON.parse(figure.dataset.points);
  const svg = figure.querySelector("svg");
  const cursor = svg.querySelector(".cursor");
  const dot = svg.querySelector(".dot");
  const tooltip = figure.querySelector(".tooltip");
  const width = svg.viewBox.baseVal.width;

  const show = (event) => {
    const box = svg.getBoundingClientRect();
    const x = ((event.clientX - box.left) / box.width) * width;
    const point = points.reduce((a, b) => (Math.abs(b.x - x) < Math.abs(a.x - x) ? b : a));
    cursor.setAttribute("x1", point.x);
    cursor.setAttribute("x2", point.x);
    dot.setAttribute("cx", point.x);
    dot.setAttribute("cy", point.y);
    tooltip.textContent = `${point.d} · ${point.v}`;
    const left = (point.x / width) * box.width;
    tooltip.style.left = `${Math.min(Math.max(left, 70), box.width - 70)}px`;
    cursor.hidden = dot.hidden = tooltip.hidden = false;
  };
  const hide = () => {
    cursor.hidden = dot.hidden = tooltip.hidden = true;
  };
  svg.addEventListener("pointermove", show);
  svg.addEventListener("pointerdown", show);
  svg.addEventListener("pointerleave", hide);
});
