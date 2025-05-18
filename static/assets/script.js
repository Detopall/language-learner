"use strict";

document.addEventListener("DOMContentLoaded", () => {
	const sessionToken = document.cookie
		.split(";")
		.find((cookie) => cookie.startsWith("sessionToken="))
		?.split("=")[1];

	if (sessionToken) {
		fetch("/dashboard", {
			headers: {
				"X-Requested-With": "XMLHttpRequest",
			},
		})
			.then((res) => res.text())
			.then((html) => {
				document.getElementById("content-container").innerHTML = html;
			})
			.catch((err) => console.error("Failed to load dashboard:", err));
	}
});
