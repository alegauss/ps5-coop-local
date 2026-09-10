/* The grid (CL7).
 *
 * One module, no framework and no build step: the page is served as it sits in the
 * repository. It reads data/games.json and renders every record as a cover card.
 *
 * There is no pagination on purpose. Scrolling a long list costs less than
 * discovering the game you wanted was on page three, and the whole point of the
 * catalogue is seeing what is there.
 *
 * The filters are CL9, ordering CL10 and the detail view CL11, and each layers onto
 * one list rather than around a half-built one.
 *
 * Search (CL8) matches canonical names and every alias CL2 and CL5 folded in, so a
 * title the source spelled differently still answers to what the source said. It
 * folds case and accents, and tolerates a single-character typo -- names like
 * Guacamelee and Chaosbane invite one -- but only for queries long enough that the
 * tolerance cannot match half the catalogue. The query lives in the URL so a link
 * pasted into the group chat opens already filtered.
 *
 * The empty result is deliberately still bare: naming its cause and offering a way
 * out is CL17.
 */

const DATASET = "data/games.json";

/** Below this length a one-character tolerance matches far too much: at three
 *  characters nearly every title is one edit from the query. */
const FUZZY_MIN = 4;

const grid = document.getElementById("grid");
const status = document.getElementById("status");
const form = document.getElementById("search");
const field = document.getElementById("q");

/** Lowercase, strip accents, and reduce punctuation to spaces, so "Leao" finds
 *  "Leão" and "guacamelee" is one edit from "guacamalee" rather than two -- with
 *  the "!" still attached, the typo tolerance could never reach it. */
function fold(text) {
  return text
    .normalize("NFD")
    .replace(/\p{Diacritic}/gu, "")
    .toLowerCase()
    .replace(/[^\p{Letter}\p{Number}]+/gu, " ")
    .trim();
}

/** True when a and b differ by at most one insertion, deletion or substitution.
 *  Cheaper and clearer than a full edit-distance matrix, which is wasted when the
 *  only answer needed is "within one". */
function withinOneEdit(a, b) {
  if (a === b) return true;
  if (Math.abs(a.length - b.length) > 1) return false;

  const [shorter, longer] = a.length <= b.length ? [a, b] : [b, a];
  let i = 0;
  let j = 0;
  let slack = 1;
  while (i < shorter.length && j < longer.length) {
    if (shorter[i] === longer[j]) {
      i += 1;
      j += 1;
      continue;
    }
    if (slack === 0) return false;
    slack -= 1;
    // On equal lengths the mismatch is a substitution, so both advance;
    // otherwise it is an insertion in the longer string.
    if (shorter.length === longer.length) i += 1;
    j += 1;
  }
  return true;
}

/** Every name a game answers to, folded once at load rather than per keystroke. */
function searchKeys(game) {
  return [game.name, ...(game.aliases ?? [])].map(fold);
}

function containsQuery(game, query) {
  return game.keys.some((key) => key.includes(query));
}

function nearQuery(game, query) {
  // Each word as well as the whole title, so a typo in one word of a long name
  // still finds it without the entire title having to be within one edit.
  return game.keys.some(
    (key) =>
      withinOneEdit(key, query) ||
      key.split(" ").some((word) => withinOneEdit(word, query)),
  );
}

/** Typo tolerance is a fallback, not a widening. Run alongside the literal match
 *  it drags in neighbours -- "leao" would return the LEGO titles next to the one
 *  game actually spelled Leão -- so it only speaks when nothing matched at all. */
function search(games, query) {
  if (!query) return games;
  const found = games.filter((game) => containsQuery(game, query));
  if (found.length > 0 || query.length < FUZZY_MIN) return found;
  return games.filter((game) => nearQuery(game, query));
}

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

/** Keep the address bar in step without pushing a history entry per keystroke,
 *  which would make Back walk the query backwards one letter at a time. */
function syncUrl(query) {
  const url = new URL(window.location.href);
  if (query) url.searchParams.set("q", query);
  else url.searchParams.delete("q");
  window.history.replaceState(null, "", url);
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

  for (const game of games) game.keys = searchKeys(game);

  const apply = (raw) => {
    const query = fold(raw);
    render(search(games, query));
    syncUrl(query);
  };

  // A link arriving with ?q= opens already filtered.
  field.value = new URL(window.location.href).searchParams.get("q") ?? "";
  apply(field.value);

  field.addEventListener("input", () => apply(field.value));
  // No submit button, so Enter must not reload the page and lose the filter.
  form.addEventListener("submit", (event) => event.preventDefault());
}

main();
