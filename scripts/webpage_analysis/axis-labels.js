const periods = {
  1500: [1624, 1624],
  1600: [1624, 2356],
  1700: [2356, 3811],
  1800: [3811, 5271],
  1850: [5271, 6706],
  1900: [6706, 8175],
  1925: [8175, 9650],
  1950: [9650, 11120],
  1975: [11120, 12600],
  2000: [12600, 14065],
  2012: [14065, 15533],
  2025: [15533, 17000],
};

function getLegendRangesInMapRange(legendRanges, mapRange) {
  const [mapRangeStart, mapRangeEnd] = mapRange;
  const result = {};

  for (const [legendRange, [start, end]] of Object.entries(legendRanges)) {
    if (end < mapRangeStart) {
      // legendRange ends before the range starts, skip it
      continue;
    }

    if (start > mapRangeEnd) {
      // legendRange starts after the range ends,
      // stop checking further as legendRanges are sorted
      break;
    }

    const rangeStart = Math.max(start, mapRangeStart);
    const rangeEnd = Math.min(end, mapRangeEnd);

    if (rangeStart < rangeEnd) {
      result[legendRange] = [rangeStart, rangeEnd];
    }
  }

  return result;
}

function getVisibleLegendRanges(legendRanges, mapRange) {
  const [mapRangeStart, mapRangeEnd] = mapRange;
  const result = {};

  for (const [legendRange, [start, end]] of Object.entries(legendRanges)) {
    if (end < mapRangeStart) {
      // legendRange ends before the range starts, skip it
      continue;
    }

    if (start > mapRangeEnd) {
      // legendRange starts after the range ends,
      // stop checking further as legendRanges are sorted
      break;
    }

    const rangeStart = Math.max(start, mapRangeStart);
    const rangeEnd = Math.min(end, mapRangeEnd);

    if (rangeStart < rangeEnd) {
      result[legendRange] = [start, end];
    }
  }

  return result;
}

function renderTopicLabels(view, map) {
  const [xStart, yStart, xEnd, yEnd] = view
    .calculateExtent(map.getSize())
    .map((n) => n.toFixed(2));
  const container = document.getElementById("map-topics");
  const { width } = container.getBoundingClientRect();
  const mapPxWidth = (width * 160980) / (xEnd - xStart);
  function convertMapLenghtUnitsToPx(len) {
    return (len * mapPxWidth) / 160980;
  }
  container.style.width = mapPxWidth;
  container.innerHTML = Object.entries(topics)
    .map(([topic, { range }], i) => {
      const isPartialLeftView = range[0] < xStart && range[1] > xStart;
      return `<div
        style='display: inline-block; position: ${
          isPartialLeftView ? "sticky;" : "absolute;"
        } text-align: left; overflow: hidden; text-overflow: ellipsis; left: ${
        convertMapLenghtUnitsToPx(range[0] - xStart) + "px;"
      } padding-left: 5px; font-size: 13px; width: ${
        isPartialLeftView
          ? "calc(" +
            convertMapLenghtUnitsToPx(range[1] - xStart) +
            "px - 5px);"
          : "calc(" +
            convertMapLenghtUnitsToPx(range[1] - range[0]) +
            "px - 5px);"
      } border-left: ${
        isPartialLeftView ? "0" : "1px"
      } solid var(--text-color); ${
        Object.values(topics)[i + 1] &&
        Object.values(topics)[i + 1].range[0] === range[1]
          ? ""
          : "" //"border-right: 1px solid var(--text-color);"
      }  cursor: default; white-space: nowrap;' title="${topic}">
        ${topic}
        </div>`;
    })
    .join("");
  //container.style.transform = `translateX(-${5}%)`;
  //   container.innerHTML = Object.keys(legendRangesInMapRange)
  //     .map((legendRange, i) => {
  //       return `<div
  //         style='overflow: clip;min-width: 0; max-height:30px; padding-left: 5px;${
  //           i === 0 ? "" : ""
  //         }border-left: 1px solid var(--text-color);justify-self: start; color: var(--text-color); background-color: var{--background-color}'>
  //         ${legendRange}
  //         </div>`;
  //     })
  //     .join("");
}
function renderPeriodLabels(view, map) {
  const [xStart, yStart, xEnd, yEnd] = view
    .calculateExtent(map.getSize())
    .map((n) => n.toFixed(2));
  const legendRangesInMapRange = getLegendRangesInMapRange(periods, [
    yStart,
    yEnd,
  ]);
  const container = document.getElementById("map-periods");
  container.style.display = "grid";
  container.style.justifyContent = "end";
  container.style.gridTemplateColumns = "10px";
  const gridTemplateRows = Object.values(legendRangesInMapRange)
    .map(([start, end]) => (end - start) / (yEnd - yStart) + "fr")
    .reverse()
    .join(" ");
  container.style.gridTemplateRows = gridTemplateRows;
  container.innerHTML = Object.entries(legendRangesInMapRange)
    .map(([legendKey, legendRange]) => {
      const indexInPeriods = Object.keys(periods).indexOf(legendKey);
      const periodRange = periods[legendKey];
      return `<div
        style='1px solid var(--text-color); width: 10px;position: relative;font-size: 10px; font-face: Arial; font-weight: 400; line-height: 11.5px;'>
            ${
              periodRange[1] > legendRange[1]
                ? ""
                : `<div style="position:absolute; left: -30px; top:-5px">${legendKey}</div>`
            }
            ${
              indexInPeriods === 1 && periodRange[0] == legendRange[0]
                ? '<div style="position:absolute; left: -30px; bottom:-5px">1500</div>'
                : ""
            }
        </div>`;
    })
    .reverse()
    .join("");
  const yLastPeriod = Object.values(periods).reverse()[0][1];
  if (yEnd > yLastPeriod) {
    container.style.gridTemplateRows = `${
      (yEnd - yLastPeriod) / (yEnd - yStart)
    }fr ${gridTemplateRows}`;
    container.innerHTML = `<div></div>` + container.innerHTML;
  }
}

function centerMapBasedOnPreviewViewport(view, lengths) {
  const {
    xExtent,
    yExtent,
    previewWidth,
    previewHeight,
    borderWidthInPx,
    previewViewportWidth,
    previewViewportHeight,
    newPreviewViewportLeft,
    newPreviewViewportTop,
  } = lengths;
  const newPreviewViewportBottom =
    previewHeight -
    (previewViewportHeight + 2 * borderWidthInPx + newPreviewViewportTop);
  const xCenter =
    ((newPreviewViewportLeft + previewViewportWidth / 2 + borderWidthInPx) *
      xExtent) /
    previewWidth;
  const yCenter =
    ((newPreviewViewportBottom + previewViewportHeight / 2 + borderWidthInPx) *
      yExtent) /
    previewHeight;
  view.setCenter([xCenter, yCenter]);
}

function setMapPreviewNavigation(view, lengths) {
  const parent = document.getElementById("map-preview");
  const child = document.getElementById("map-preview-viewport");

  // Dragging functionality
  let isDragging = false;
  let offsetX, offsetY;

  child.addEventListener("mousedown", function (e) {
    isDragging = true;
    offsetX = e.clientX - child.offsetLeft;
    offsetY = e.clientY - child.offsetTop;
    document.addEventListener("mousemove", onMouseMove);
    document.addEventListener("mouseup", onMouseUp);
  });

  function onMouseMove(e) {
    if (!isDragging) return;
    let x = e.clientX - offsetX;
    let y = e.clientY - offsetY;

    // Ensure the child stays within the parent's boundaries
    x = Math.max(0, Math.min(parent.clientWidth - child.clientWidth, x));
    y = Math.max(0, Math.min(parent.clientHeight - child.clientHeight, y));

    child.style.left = x + "px";
    child.style.top = y + "px";
    centerMapBasedOnPreviewViewport(view, {
      ...lengths,
      newPreviewViewportLeft: x,
      newPreviewViewportTop: y,
    });
  }

  function onMouseUp() {
    isDragging = false;
    document.removeEventListener("mousemove", onMouseMove);
    document.removeEventListener("mouseup", onMouseUp);
    updateUrlParameters({
      center: view.getCenter(),
      zoom: view.getZoom(),
    });
  }
}

function renderMapPreviewPosition(view, map) {
  const [xExtent, yExtent] = [160980, 17450];
  const [xStart, yStart, xEnd, yEnd] = view
    .calculateExtent(map.getSize())
    .map((n) => n.toFixed(2));
  const container = document.getElementById("map-preview");

  const { width: previewWidth, height: previewHeight } =
    container.getBoundingClientRect();
  container.style.position = "relative";
  const borderWidthInPx = 2;
  const previewViewportLeft = (previewWidth * xStart) / xExtent;
  const previewViewportBottom = (previewHeight * yStart) / yExtent;
  const previewViewportWidth =
    (previewWidth * (xEnd - xStart)) / xExtent - 2 * borderWidthInPx;
  const previewViewportHeight =
    (previewHeight * (yEnd - yStart)) / yExtent - borderWidthInPx;

  container.innerHTML = `
    <img src="content/mini-map-${mapBgColor}.png" tabindex="0" style='
        user-select: none;
        -webkit-user-select: none; /* Safari */
        -moz-user-select: none; /* Firefox */
        -ms-user-select: none; /* IE/Edge */'/>
    <div id='map-preview-viewport' tabindex="0"
        style='position: absolute; left: ${
          previewViewportLeft + "px;"
        } bottom: ${previewViewportBottom + "px;"} width: ${
    previewViewportWidth + "px;"
  } height: ${previewViewportHeight + "px;"} border: ${
    borderWidthInPx + "px"
  } solid var(--text-color);'></div>`;
  setMapPreviewNavigation(view, {
    xExtent,
    yExtent,
    previewWidth,
    previewHeight,
    borderWidthInPx,
    previewViewportLeft,
    previewViewportBottom,
    previewViewportWidth,
    previewViewportHeight,
  });
}
function renderLabels(view, map) {
  renderTopicLabels(view, map);
  renderPeriodLabels(view, map);
}
