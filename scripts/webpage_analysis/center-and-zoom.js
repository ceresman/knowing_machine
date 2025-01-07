function debounce(func, delay) {
  let debounceTimer;
  return function () {
    const context = this;
    const args = arguments;
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => func.apply(context, args), delay);
  };
}

function getCenterAndZoomFromUrlAnchor() {
  const [x, y, z] = window.location.hash.substring(1).split(",");
  return { x, y, z };
}

function getUrlParam(paramKey) {
  const params = new URLSearchParams(window.location.search);
  return params.get(paramKey);
}
const capitalize = (s) => (s && s[0].toUpperCase() + s.slice(1)) || "";
function getNameFromSlug(slug) {
  const name = slug.toLowerCase().replaceAll("-", " ");
  return capitalize(name);
}

function getCenterAndZoomFromUrlParams() {
  const position = getUrlParam("pos");
  const audioSlug = getUrlParam("audio");
  if (audioSlug != null && audioTours[getNameFromSlug(audioSlug)]) {
    const { startPos } = audioTours[getNameFromSlug(audioSlug)];
    const { x, y, z } = startPos;
    return { x, y, z };
  }
  const topicSlug = getUrlParam("topic");
  if (topicSlug != null && topics[getNameFromSlug(topicSlug)]) {
    const [x, y, z] = topics[getNameFromSlug(topicSlug)].pos
      .split("%2C")
      .map((n) => +n);
    updateUrlParameters({ center: [x, y], zoom: z });
    return { x, y, z };
  }
  if (position != null) {
    const [x, y, z] = position.split(",").map((n) => +n);
    return { x, y, z };
  }
  return { ...defaultPos };
}

const updateUrlParameters = debounce(function ({ center, zoom }) {
  const url = new URL(window.location);

  // Set or replace the parameter
  const posParamValue = `${center[0].toFixed(2)},${center[1].toFixed(
    2
  )},${zoom.toFixed(4)}`;
  url.searchParams.set("pos", posParamValue);
  url.searchParams.delete("topic");
  url.searchParams.delete("audio");

  // Update the URL in the address bar without reloading the page
  window.history.replaceState({}, "", url);
}, 400);

function getCenterAndZoom() {
  const defaultCenter = [defaultPos.x, defaultPos.y];
  const defaultZoom = defaultPos.z;
  const { x, y, z } = getCenterAndZoomFromUrlParams();
  const center =
    x != "" &&
    x != null &&
    x > 0 &&
    x < 160980 &&
    y != "" &&
    y != null &&
    y > 0 &&
    y < 17764
      ? [x, y]
      : defaultCenter;
  const zoom = z != "" && z != null && z > 12 && z < 18 ? z : defaultZoom;
  return { center, zoom };
}

function flyTo({ view, center }) {
  const duration = 2000;
  const zoom = view.getZoom();
  let parts = 2;
  let called = false;
  function callback(complete) {
    --parts;
    if (called) {
      return;
    }
    if (parts === 0 || !complete) {
      called = true;
      done(complete);
    }
  }
  view.animate(
    {
      center: center,
      duration: duration,
    },
    callback
  );
  view.animate(
    {
      zoom: zoom - 1,
      duration: duration / 2,
    },
    {
      zoom: zoom,
      duration: duration / 2,
    },
    callback
  );
}
