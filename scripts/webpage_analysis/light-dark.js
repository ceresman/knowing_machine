const mapEl = document.getElementById("map");
// Function to apply the theme
function applyTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("theme", theme);
  if (mapEl) {
    switchFooterImages(theme);
    switchAudioTourButtons(theme);
  }
  switchMenuIcon(theme);
  switchModeText(theme);
}

function switchFooterImages(theme) {
  let color = theme === "dark" ? "white" : "black";
  document
    .getElementById("zoom-in")
    .getElementsByTagName("img")[0].src = `./content/plus-${color}.svg`;
  document
    .getElementById("zoom-out")
    .getElementsByTagName("img")[0].src = `./content/minus-${color}.svg`;
  document
    .getElementById("map-preview")
    .getElementsByTagName("img")[0].src = `./content/mini-map-${
    color === "white" ? "black" : "white"
  }.png`;
}
function switchModeText(theme) {
  document.getElementById("map-bg").innerText =
    theme === "dark" ? "Light mode" : "Dark mode";
}
function switchAudioTourButtons(theme) {
  let color = theme === "dark" ? "white" : "black";
  let oppositeColor = theme === "dark" ? "black" : "white";
  document
    .getElementById("play-button") //play button
    .getElementsByTagName("img")[0].src = `./content/play-button-${color}.svg`;

  document
    .getElementById("pause-button") //play button
    .getElementsByTagName("img")[0].src = `./content/pause-button-${color}.svg`;

  document
    .getElementById("cc-button") //cc button
    .getElementsByTagName("img")[0].src = `./content/cc-${color}.svg`;
  document
    .getElementById("unmute-button") //unmute button
    .getElementsByTagName("img")[0].src = `./content/sound-mute-${color}.svg`;
  document
    .getElementById("close-button") //unmute button
    .getElementsByTagName("img")[0].src = `./content/stop-${color}.svg`;
}
function switchMenuIcon(theme) {
  let color = theme === "dark" ? "white" : "black";
  document
    .getElementById("info-icon")
    .getElementsByTagName("img")[0].src = `./content/info-icon-${color}.svg`;
}
document.addEventListener("DOMContentLoaded", () => {
  function refresh() {
    var source = tileLayer.getSource();
    source.tileCache.expireCache({});
    source.tileCache.clear();
    source.refresh();
  }
  // Event listener for the toggle button
  document.getElementById("theme-toggle").addEventListener("click", () => {
    const currentTheme = document.documentElement.getAttribute("data-theme");
    const newTheme = currentTheme === "dark" ? "light" : "dark";
    const newBgColor = newTheme === "dark" ? "black" : "white";
    document.getElementById("map-bg").innerText =
      newBgColor === "white" ? "Dark mode" : "Light mode";
    if (mapEl) {
      switchFooterImages(newTheme);
      switchAudioTourButtons(newTheme);
    }
    switchModeText(newTheme);
    switchMenuIcon(newTheme);
    mapBgColor = newBgColor;
    applyTheme(newTheme);
    if (mapEl) {
      refresh();
    }
  });
  window.addEventListener("resize", () => {
    switchAudioTourButtons(document.documentElement.getAttribute("data-theme"));
  });
  // Apply the saved theme on page load
  const savedTheme = localStorage.getItem("theme") || "dark";
  applyTheme(savedTheme);
});
