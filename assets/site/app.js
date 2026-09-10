/* The grid (CL7).
 *
 * One module, no framework and no build step: the page is served as it sits in the
 * repository. It reads data/games.json and renders every record as a cover card.
 *
 * There is no pagination on purpose. Scrolling a long list costs less than
 * discovering the game you wanted was on page three, and the whole point of the
 * catalogue is seeing what is there.
 *
 * Search is CL8, the filters CL9, ordering CL10 and the detail view CL11. This
 * module stays a renderer so those can layer on top of one list rather than
 * around a half-built one.
 */

const DATASET = "data/games.json";

const grid = document.getElementById("grid");
const status = document.getElementById("status");

/** Build one card. Kept as DOM calls rather than innerHTML so a game whose title
 *  contains markup characters cannot become markup. */
function card(game) {
  const item = document.createElement("li");
  item.className = "card";

  const art = document.createElement("img");
  art.className = "card__art";
  art.src = game.cover;
  // The name is carried by the caption right below, so repeating it here would
  // make a screen reader read every title twice.
  art.alt = "";
  art.width = 200;
  art.height = 300;
  // CL18 owns loading strategy; this is the one-line version that stops 184
  // covers from competing with the first paint.
  art.loading = "lazy";
  art.decoding = "async";

  const name = document.createElement("span");
  name.className = "card__name";
  name.textContent = game.name;

  item.append(art, name);
  return item;
}

function render(games) {
  const fragment = document.createDocumentFragment();
  for (const game of games) fragment.append(card(game));
  grid.replaceChildren(fragment);
  grid.hidden = false;
  status.hidden = true;
}

function fail(message) {
  status.textContent = message;
  status.hidden = false;
  grid.hidden = true;
}

async function main() {
  let payload;
  try {
    const response = await fetch(DATASET);
    if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
    payload = await response.json();
  } catch (error) {
    // A file:// open is the likely cause and the error alone does not say so.
    fail(
      "Could not load the catalogue. Serve this folder over HTTP " +
        "(python3 -m http.server) rather than opening the file directly.",
    );
    console.error(error);
    return;
  }

  const games = payload?.games;
  if (!Array.isArray(games) || games.length === 0) {
    fail("The catalogue loaded but holds no games.");
    return;
  }
  render(games);
}

main();
