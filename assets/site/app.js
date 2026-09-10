/* The grid (CL7).
 *
 * One module, no framework and no build step: the page is served as it sits in the
 * repository. It reads data/games.json and renders every record as a cover card.
 *
 * There is no pagination on purpose. Scrolling a long list costs less than
 * discovering the game you wanted was on page three, and the whole point of the
 * catalogue is seeing what is there.
 *
 * The detail view (CL11) is a native <dialog> positioned as a side panel, so the
 * grid stays behind it and Escape, the focus trap and the inert background come
 * from the platform instead of from this file getting them subtly wrong. It is
 * where the source list's parenthetical finally surfaces: that Call of Duty is
 * local co-op only in Zombies, and WRC Generations only in split screen, is the
 * fact that decides the purchase, and nothing else in the interface keeps it.
 *
 * Ordering (CL10) defaults to alphabetical, because it is the order a person can
 * predict, and it ignores a leading article so The Quarry sorts under Q instead of
 * half the catalogue piling up under T.
 *
 * The filters (CL9) are players, genre and screen, combinable and each reversible.
 * Player count reads as "at least this many": the question the catalogue exists to
 * answer is what four of us can play tonight, and an exact match would hide an
 * eight-player game from that search. A game whose value is unknown is excluded
 * while that filter is on rather than assumed to qualify -- CL3 left 58 blanks and
 * a blank is not a claim.
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

/** Players, as "at least this many". 5 is the open-ended top of the range. */
const PLAYER_STEPS = [2, 3, 4, 5];

/** Dropped from the front of a title before it is sorted. Portuguese articles are
 *  here too: the source list is Brazilian and CL5 left translated titles behind. */
const LEADING_ARTICLE = /^(the|a|an|o|os|as|um|uma)\s+/i;

/** Names sort by the reader's rules, not by code point: "Ãlvaro" belongs with A. */
const COLLATOR = new Intl.Collator(undefined, { sensitivity: "base", numeric: true });

const grid = document.getElementById("grid");
const status = document.getElementById("status");
const form = document.getElementById("search");
const field = document.getElementById("q");
const panel = document.getElementById("filters");
const toggle = document.getElementById("filters-toggle");
const clear = document.getElementById("clear");
const sortField = document.getElementById("sort");
const counter = document.getElementById("count");
const detail = document.getElementById("detail");
const detailArt = document.getElementById("detail-art");
const detailTitle = document.getElementById("detail-title");
const detailFacts = document.getElementById("detail-facts");
const detailNote = document.getElementById("detail-note");
const detailClose = document.getElementById("detail-close");

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

/** One radio chip. A real input, so a group is arrow-key navigable and reaches a
 *  screen reader as a group, without this file reimplementing either. */
function chip(group, value, label, checked) {
  const wrap = document.createElement("label");
  wrap.className = "chip";

  const input = document.createElement("input");
  input.type = "radio";
  input.name = group;
  input.value = value;
  input.checked = checked;

  const text = document.createElement("span");
  text.textContent = label;

  wrap.append(input, text);
  return wrap;
}

function fillChips(node, group, options, active) {
  node.replaceChildren(
    chip(group, "", "Any", !active),
    ...options.map(([value, label]) => chip(group, value, label, active === value)),
  );
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

function passesFilters(game, state) {
  // An unknown value never satisfies a filter. CL3 and CL4 left blanks on purpose,
  // and treating one as a match would put a game on screen on the strength of a
  // fact nobody established.
  if (state.players && !(game.max_players >= Number(state.players))) return false;
  if (state.genre && game.genre !== state.genre) return false;
  if (state.screen && game.screen !== state.screen) return false;
  return true;
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

function sortKey(name) {
  return name.replace(LEADING_ARTICLE, "");
}

/** Descending on a number, with unknowns always last rather than sorted as zero:
 *  CL3 and CL4 left blanks, and a blank is not a low score. Ties fall back to the
 *  alphabetical order, so a re-sort is stable and predictable rather than
 *  whatever order the previous filter happened to leave behind. */
function byDescending(field) {
  return (a, b) => {
    const x = a[field];
    const y = b[field];
    if (x == null && y == null) return COLLATOR.compare(a.sortName, b.sortName);
    if (x == null) return 1;
    if (y == null) return -1;
    return y - x || COLLATOR.compare(a.sortName, b.sortName);
  };
}

const ORDERS = {
  name: (a, b) => COLLATOR.compare(a.sortName, b.sortName),
  year: byDescending("year"),
  players: byDescending("max_players"),
};

function select(games, state) {
  const chosen = search(games, state.q).filter((game) => passesFilters(game, state));
  return chosen.sort(ORDERS[state.sort] ?? ORDERS.name);
}

/** Build one card. Kept as DOM calls rather than innerHTML so a game whose title
 *  contains markup characters cannot become markup. */
function card(game) {
  const item = document.createElement("li");
  item.className = "card";

  // A button, not a click handler on the li: the panel has to open from the
  // keyboard too, and a button is already in the tab order and announces itself.
  const open = document.createElement("button");
  open.type = "button";
  open.className = "card__open";
  open.addEventListener("click", () => openDetail(game));

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

  open.append(art, name);
  item.append(open);
  return item;
}

const SCREEN_PROSE = {
  split: "split screen",
  shared: "one shared screen",
  pass: "pass the controller",
};

const SCOPE_PROSE = {
  campaign: "the full campaign",
  side: "side modes only",
  versus: "versus only",
};

/** Rows are added only where the value is known. An "unknown" row would fill the
 *  panel with the fact that nobody has checked, which is not what the reader came
 *  for -- the absence of the row already says it. */
function facts(game) {
  const rows = [
    ["Players", game.max_players ? `up to ${game.max_players} on one console` : null],
    ["Screen", SCREEN_PROSE[game.screen] ?? null],
    ["Co-op covers", SCOPE_PROSE[game.scope] ?? null],
    ["Genre", game.genre ? game.genre.replace(/-/g, " ") : null],
    ["Released", game.year ? String(game.year) : null],
    ["Publisher", game.publisher ?? null],
    ["Also known as", game.aliases?.length ? game.aliases.join(", ") : null],
  ];

  const list = document.createDocumentFragment();
  for (const [label, value] of rows) {
    if (!value) continue;
    const dt = document.createElement("dt");
    dt.textContent = label;
    const dd = document.createElement("dd");
    dd.textContent = value;
    list.append(dt, dd);
  }
  return list;
}

function openDetail(game) {
  detailArt.src = game.cover;
  detailTitle.textContent = game.name;
  detailFacts.replaceChildren(facts(game));

  if (game.source_note) {
    const lead = document.createElement("em");
    lead.textContent = "The list says";
    // Quoted rather than rewritten: the note is the source's own words, often in
    // Portuguese, and paraphrasing it would quietly restate somebody else's claim.
    const body = document.createTextNode(`\u201c${game.source_note}\u201d`);
    detailNote.replaceChildren(lead, body);
    detailNote.hidden = false;
  } else {
    detailNote.hidden = true;
  }

  detail.showModal();
}

function render(games) {
  const fragment = document.createDocumentFragment();
  for (const game of games) fragment.append(card(game));
  grid.replaceChildren(fragment);
  grid.hidden = false;
  status.hidden = true;
}

/** The cheapest possible feedback that the interaction landed, and the thing that
 *  gives a newcomer the scale of the catalogue (CL12). It says "of 184" only while
 *  something is narrowing the list, so the unfiltered page states one number
 *  rather than the same number twice. */
function showCount(shown, total) {
  // The noun agrees with whichever number it follows: "1 game" unfiltered, but
  // "1 of 184 games", because there it is the total being counted.
  if (shown === total) {
    counter.textContent = `${total} ${total === 1 ? "game" : "games"}`;
    return;
  }
  counter.textContent = `${shown} of ${total} ${total === 1 ? "game" : "games"}`;
}

/** Keep the address bar in step without pushing a history entry per keystroke,
 *  which would make Back walk the query backwards one letter at a time. */
function syncUrl(state) {
  const url = new URL(window.location.href);
  for (const key of ["q", "players", "genre", "screen", "sort"]) {
    // "name" is the default order, so it is left out rather than pinned into
    // every link the user copies.
    if (state[key] && !(key === "sort" && state[key] === "name")) {
      url.searchParams.set(key, state[key]);
    }
    else url.searchParams.delete(key);
  }
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

  for (const game of games) {
    game.keys = searchKeys(game);
    game.sortName = sortKey(game.name);
  }

  const params = new URL(window.location.href).searchParams;
  const state = {
    q: fold(params.get("q") ?? ""),
    players: params.get("players") ?? "",
    genre: params.get("genre") ?? "",
    screen: params.get("screen") ?? "",
    sort: ORDERS[params.get("sort")] ? params.get("sort") : "name",
  };

  // Offered from what the data actually holds, so a genre nobody has assigned
  // never appears as a filter that can only return nothing.
  const present = (key) =>
    [...new Set(games.map((game) => game[key]).filter(Boolean))].sort();

  const draw = () => {
    fillChips(
      document.getElementById("chips-players"),
      "players",
      PLAYER_STEPS.map((n) => [String(n), n === 5 ? "5+" : `${n}+`]),
      state.players,
    );
    fillChips(
      document.getElementById("chips-genre"),
      "genre",
      present("genre").map((g) => [g, g.replace(/-/g, " ")]),
      state.genre,
    );
    fillChips(
      document.getElementById("chips-screen"),
      "screen",
      present("screen").map((s) => [s, s]),
      state.screen,
    );
  };

  const apply = () => {
    const shown = select(games, state);
    render(shown);
    showCount(shown.length, games.length);
    syncUrl(state);
    const active = ["players", "genre", "screen"].filter((k) => state[k]).length;
    clear.hidden = active === 0 && !state.q;
    toggle.textContent = active ? `Filters (${active})` : "Filters";
  };

  field.value = params.get("q") ?? "";
  sortField.value = state.sort;
  draw();
  apply();

  field.addEventListener("input", () => {
    state.q = fold(field.value);
    apply();
  });
  // No submit button, so Enter must not reload the page and lose the filter.
  form.addEventListener("submit", (event) => event.preventDefault());

  panel.addEventListener("change", (event) => {
    const input = event.target;
    if (!(input instanceof HTMLInputElement)) return;
    state[input.name] = input.value;
    apply();
  });

  sortField.addEventListener("change", () => {
    state.sort = sortField.value;
    apply();
  });

  clear.addEventListener("click", () => {
    state.q = "";
    state.players = state.genre = state.screen = "";
    field.value = "";
    draw();
    apply();
  });

  // Collapsed by default only where the media query hides the panel; on desktop
  // the attribute is never set, so the filters stay visible at all times.
  // "/" jumps to search, the convention this kind of page has taught people to
  // expect. Ignored while a field already has focus, or the shortcut would make
  // the character impossible to type into the search box it just opened.
  document.addEventListener("keydown", (event) => {
    if (event.key !== "/" || event.ctrlKey || event.metaKey || event.altKey) return;
    const active = document.activeElement;
    const typing =
      active instanceof HTMLInputElement ||
      active instanceof HTMLTextAreaElement ||
      active instanceof HTMLSelectElement ||
      active?.isContentEditable;
    if (typing) return;
    event.preventDefault();
    field.focus();
    field.select();
  });

  detailClose.addEventListener("click", () => detail.close());
  // Clicking the backdrop closes it. The dialog element is the full-height panel,
  // so anything outside its box is backdrop.
  detail.addEventListener("click", (event) => {
    const box = detail.getBoundingClientRect();
    const outside =
      event.clientX < box.left ||
      event.clientX > box.right ||
      event.clientY < box.top ||
      event.clientY > box.bottom;
    if (outside) detail.close();
  });

  const phone = window.matchMedia("(max-width: 640px)");
  const collapse = () => {
    panel.hidden = phone.matches;
    toggle.setAttribute("aria-expanded", String(!phone.matches));
  };
  collapse();
  phone.addEventListener("change", collapse);
  toggle.addEventListener("click", () => {
    panel.hidden = !panel.hidden;
    toggle.setAttribute("aria-expanded", String(!panel.hidden));
    // The sheet covers the thumb's half of the screen, so it has to be
    // dismissable without hunting for the button that opened it.
    if (!panel.hidden) panel.querySelector("input")?.focus();
  });

  // Escape closes the sheet, matching the detail panel rather than being the one
  // overlay on the page that traps you.
  document.addEventListener("keydown", (event) => {
    if (event.key !== "Escape" || panel.hidden || !phone.matches) return;
    panel.hidden = true;
    toggle.setAttribute("aria-expanded", "false");
    toggle.focus();
  });
}

main();
