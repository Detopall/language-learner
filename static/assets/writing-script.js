"use strict";

function initCanvas() {
	const canvas = document.getElementById("canvas");
	if (!canvas) {
		console.warn("Canvas not found.");
		return;
	}

	const ctx = canvas.getContext("2d");

	// Set up drawing styles
	ctx.strokeStyle = "white";
	ctx.lineWidth = 25;
	ctx.lineJoin = "round";
	ctx.lineCap = "round";

	let isDrawing = false;

	function getOffset(event) {
		if (event.touches) {
			const rect = canvas.getBoundingClientRect();
			return {
				x: event.touches[0].clientX - rect.left,
				y: event.touches[0].clientY - rect.top,
			};
		}
		return { x: event.offsetX, y: event.offsetY };
	}

	// Remove previous listeners if any (optional safety)
	canvas.replaceWith(canvas.cloneNode(true));
	const freshCanvas = document.getElementById("canvas");
	const freshCtx = freshCanvas.getContext("2d");

	freshCtx.strokeStyle = "white";
	freshCtx.lineWidth = 25;
	freshCtx.lineJoin = "round";
	freshCtx.lineCap = "round";

	let freshIsDrawing = false;

	freshCanvas.addEventListener("mousedown", (e) => {
		freshIsDrawing = true;
		const { x, y } = getOffset(e);
		freshCtx.beginPath();
		freshCtx.moveTo(x, y);
	});
	freshCanvas.addEventListener("mousemove", (e) => {
		if (!freshIsDrawing) return;
		const { x, y } = getOffset(e);
		freshCtx.lineTo(x, y);
		freshCtx.stroke();
	});
	freshCanvas.addEventListener("mouseup", () => {
		freshIsDrawing = false;
		freshCtx.closePath();
	});
	freshCanvas.addEventListener("mouseleave", () => {
		freshIsDrawing = false;
		freshCtx.closePath();
	});

	freshCanvas.addEventListener("touchstart", (e) => {
		freshIsDrawing = true;
		const { x, y } = getOffset(e);
		freshCtx.beginPath();
		freshCtx.moveTo(x, y);
	});
	freshCanvas.addEventListener(
		"touchmove",
		(e) => {
			if (!freshIsDrawing) return;
			const { x, y } = getOffset(e);
			freshCtx.lineTo(x, y);
			freshCtx.stroke();
			e.preventDefault();
		},
		{ passive: false }
	);
	freshCanvas.addEventListener("touchend", () => {
		freshIsDrawing = false;
		freshCtx.closePath();
	});
	freshCanvas.addEventListener("touchcancel", () => {
		freshIsDrawing = false;
		freshCtx.closePath();
	});
}

// Run once on page load
window.addEventListener("DOMContentLoaded", initCanvas);

// Re-run after HTMX swaps in new canvas
document.body.addEventListener("htmx:afterSwap", (evt) => {
	if (evt.detail.target.id === "canvas-container") {
		console.log("Canvas container swapped — reinitializing canvas");
		initCanvas();
	}
});

window.prepareCanvasData = () => {
	const canvas = document.getElementById("canvas");
	const dataUrl = canvas.toDataURL("image/png");
	const base64Data = dataUrl.split(",")[1];
	console.log(base64Data);
	document.getElementById("canvas-data").value = base64Data;
};
