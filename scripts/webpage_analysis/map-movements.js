// Function to parse and animate the map
function animateMap(audioFile, movements, map) {
  const audio = new Audio(audioFile);
  let isCancelled = false;

  const cancelAnimation = () => {
    audio.pause();
    audio.currentTime = 0;
    isCancelled = true;
  };

  const parseMovement = async (movement) => {
    if (movement.length === 1) {
      if (typeof movement[0] === "number") {
        // It's a wait time
        console.log("wait", movement[0]);
        return new Promise((resolve) => setTimeout(resolve, movement[0]));
      } else {
        // jump without animating
        const [coords] = movement;
        const [x, y, zoom] = coords.split("%2C").map(parseFloat);
        return new Promise((resolve) => {
          map.getView().setCenter([x, y]);
          map.getView().setZoom(zoom);
          resolve();
        });
      }
    } else {
      // It's an animation
      const [coords, duration] = movement;
      const [x, y, zoom] = coords.split("%2C").map(parseFloat);
      console.log(coords, duration);
      return new Promise((resolve) => {
        map.getView().animate(
          {
            center: [x, y],
            zoom: zoom,
            duration: duration,
          },
          resolve
        );
      });
    }
  };
  const runAnimations = async () => {
    for (const movement of movements) {
      if (isCancelled) {
        console.log("cancelled");
        break;
      }
      await parseMovement(movement);
    }
  };

  // Play audio file
  // audio.play();
  // Run the animations
  //runAnimations();
  map.on("pointerdrag", cancelAnimation);
  map.on("pointerdown", cancelAnimation);
  //   map.on("movestart", cancelAnimation);
  //   map.on("moveend", cancelAnimation);

  // Return the cancel function to be called externally if needed
  return cancelAnimation;
}
