import "./theatre/core-only.min.js";
// We can now access Theatre.core and Theatre.studio from here
const { core } = Theatre;

function updateProgress() {
  const progressBarValue = document.getElementById("progress-value");
  const seek = window.sheet.sequence.position || 0;
  progressBarValue.style.width = (seek / window.sound.duration()) * 100 + "%";
  const time = document.getElementById("time");
  const mm = Math.floor(seek / 60)
    .toString()
    .padStart(2, "0");
  const ss = Math.floor(seek % 60)
    .toString()
    .padStart(2, "0");
  time.innerText = mm + ":" + ss;
  const subtitles = document.getElementById("audio-cc");
  const currentSubtitle = window.tourSubtitles.find(
    (s) => s[0] <= seek && seek <= s[1]
  );
  subtitles.innerText = currentSubtitle != null ? currentSubtitle[2] : "";
  if (window.tourStarted) {
    requestAnimationFrame(updateProgress);
  }
}
function playAt(position) {
  window.sheet.sequence.pause();
  window.sheet.sequence.position = position;
  window.sound.seek(window.sheet.sequence.position);
  window.sheet.sequence.play();
}

function startAudioTour(audioSlug) {
  const playButton = document.getElementById("play-button");
  playButton.classList.add("pulsate");
  const { startPos, audioFile, movements, sheetName, subtitles } =
    audioTours[getNameFromSlug(audioSlug)];

  window.tourStarted = sheetName;
  const project = core.getProject("Audio Tour Movements", {
    state: movements,
  });
  window.sheet = project.sheet(sheetName);
  window.tourSubtitles = subtitles;
  const obj = sheet.object("Map", {
    x: core.types.number(startPos.x, { range: [0, 160000] }),
    y: core.types.number(startPos.y, { range: [0, 17764] }), // you can use just a simple default value
    zoom: core.types.number(startPos.z, { range: [12.2945, 18] }),
  });

  obj.onValuesChange((obj) => {
    view.setCenter([obj.x, obj.y]);
    view.setZoom(obj.zoom);
  });

  window.sound = new Howl({
    src: [audioFile],
    html5: true,
    onend: () => {
      const [x, y] = view.getCenter();
      const z = view.getZoom();
      window.location = `/?pos=${x},${y},${z}`;
    },
    onplay: function () {
      window.sound.seek(window.sheet.sequence.position);
      document.getElementById("unmute-button").style.display = "none";
    },
    onload: function () {
      playButton.classList.remove("pulsate");
      core.onChange(sheet.sequence.pointer.playing, (playing) => {
        if (playing) {
          document.getElementById("audio-controls").classList.add("playing");
          sound.seek(sheet.sequence.position);
          window.soundId = sound.play();
        } else {
          document.getElementById("audio-controls").classList.remove("playing");
          sound.stop();
        }
        //updateProgress();
      });

      project.ready.then(() => {
        sheet.sequence.play({ iterationCount: 1, range: [0, 312] });
        requestAnimationFrame(updateProgress);
      });
    },
  });
}

const audioSlug = getUrlParam("audio");

document.getElementById("cc-button").addEventListener("click", () => {
  //if ()
  document.getElementById("audio-cc-container").style.display = "block";
});

document.getElementById("how-to-read-map").addEventListener("click", () => {
  if (document.getElementById("audio-controls").style.display === "flex") {
    playAt(0);
    return;
  }
  document.getElementById("footer-config").style.display = "none";
  document.getElementById("audio-controls").style.display = "flex";

  document.getElementById("nav-links").classList.remove("active");
  document.getElementById("audio-tours").open = false;

  startAudioTour("how-to-read-the-map");
});
document.getElementById("unmute-button").addEventListener("click", () => {
  window.sound.play();
  document.getElementById("unmute-button").style.display = "none";
});

if (audioSlug != null && audioTours[getNameFromSlug(audioSlug)]) {
  document.getElementById("footer-config").style.display = "none";
  document.getElementById("audio-controls").style.display = "flex";

  document.getElementById("unmute-button").style.display = "flex";
  document.getElementById("nav-links").classList.remove("active");
  document.getElementById("audio-tours").open = false;

  startAudioTour(audioSlug);
  // }
}

document.getElementById("play-button").addEventListener("click", () => {
  if (window.tourStarted) {
    window.sheet.sequence.play();
  } else {
    startAudioTour("how-to-read-the-map");
  }
});

document.getElementById("pause-button").addEventListener("click", () => {
  window.sheet.sequence.pause();
});

document.getElementById("close-button").addEventListener("click", () => {
  const [x, y] = view.getCenter();
  const z = view.getZoom();
  window.location = `/?pos=${x},${y},${z}`;
});

document.getElementById("progressBar").addEventListener("click", () => {
  console.log(document.getElementById("progressBar").style.width);
});
