const STORAGE_KEY = "tea-konfirmation-tasks-v1";
const EVENT_DATE = new Date("2026-05-16T00:00:00");

const defaultTasks = [
  {
    title: "Book kirke og præst",
    category: "Kirke",
    due: "2025-09-01",
    notes: "Bekræft tidspunkt og prøveforløb.",
    done: false,
  },
  {
    title: "Reservér festlokale",
    category: "Fest",
    due: "2025-10-01",
    notes: "Tjek kapacitet og bordopsætning.",
    done: false,
  },
  {
    title: "Lav gæsteliste",
    category: "Planlægning",
    due: "2025-11-15",
    notes: "Indsaml adresser og kontaktinfo.",
    done: false,
  },
  {
    title: "Send invitationer",
    category: "Gæster",
    due: "2026-02-15",
    notes: "Husk svarfrist og allergier.",
    done: false,
  },
  {
    title: "Planlæg menu og drikkevarer",
    category: "Mad",
    due: "2026-03-01",
    notes: "Aftal vegetar/veganske alternativer.",
    done: false,
  },
  {
    title: "Bestil kage",
    category: "Mad",
    due: "2026-04-01",
    notes: "Smagning og tema tilpasset Tea.",
    done: false,
  },
  {
    title: "Find tøj til Tea",
    category: "Tøj",
    due: "2026-03-15",
    notes: "Konfirmationskjole, sko, tilbehør.",
    done: false,
  },
  {
    title: "Planlæg pynt og borddækning",
    category: "Dekoration",
    due: "2026-04-15",
    notes: "Farvetema, blomster, bordkort.",
    done: false,
  },
  {
    title: "Aftal fotograf",
    category: "Foto",
    due: "2026-02-28",
    notes: "Book tid til både kirke og fest.",
    done: false,
  },
  {
    title: "Lav tidsplan for dagen",
    category: "Planlægning",
    due: "2026-04-25",
    notes: "Inkludér ankomst, kirke, fest og taler.",
    done: false,
  },
  {
    title: "Koordinér taler og indslag",
    category: "Program",
    due: "2026-05-01",
    notes: "Afstem rækkefølge og teknik.",
    done: false,
  },
  {
    title: "Planlæg transport",
    category: "Logistik",
    due: "2026-04-20",
    notes: "Transport mellem kirke og festlokale.",
    done: false,
  },
  {
    title: "Afstem gaveliste",
    category: "Gaver",
    due: "2026-03-20",
    notes: "Koordinér ønsker med Tea.",
    done: false,
  },
  {
    title: "Tjek budget og betalinger",
    category: "Budget",
    due: "2026-05-05",
    notes: "Sørg for at alle leverandører er betalt.",
    done: false,
  },
];

const elements = {
  countdown: document.getElementById("countdown"),
  total: document.getElementById("total-count"),
  done: document.getElementById("done-count"),
  remaining: document.getElementById("remaining-count"),
  form: document.getElementById("task-form"),
  list: document.getElementById("task-list"),
  filters: document.querySelectorAll(".filter-button"),
  exportButton: document.getElementById("export"),
  importInput: document.getElementById("import"),
  resetButton: document.getElementById("reset"),
};

let tasks = loadTasks();
let activeFilter = "all";

function loadTasks() {
  const stored = localStorage.getItem(STORAGE_KEY);
  if (!stored) {
    return defaultTasks.map((task) => ({ ...task, id: crypto.randomUUID() }));
  }
  try {
    const parsed = JSON.parse(stored);
    return parsed.map((task) => ({
      ...task,
      id: task.id ?? crypto.randomUUID(),
    }));
  } catch (error) {
    console.warn("Kunne ikke læse gemte data", error);
    return defaultTasks.map((task) => ({ ...task, id: crypto.randomUUID() }));
  }
}

function saveTasks() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
}

function updateCountdown() {
  const now = new Date();
  const diff = EVENT_DATE - now;
  if (diff <= 0) {
    elements.countdown.textContent = "Det er i dag!";
    return;
  }
  const days = Math.floor(diff / (1000 * 60 * 60 * 24));
  const months = Math.floor(days / 30);
  const remainingDays = days % 30;
  elements.countdown.textContent = `${months} mdr · ${remainingDays} dage`;
}

function updateSummary() {
  const total = tasks.length;
  const done = tasks.filter((task) => task.done).length;
  elements.total.textContent = total;
  elements.done.textContent = done;
  elements.remaining.textContent = total - done;
}

function matchesFilter(task) {
  if (activeFilter === "done") return task.done;
  if (activeFilter === "open") return !task.done;
  return true;
}

function formatDate(dateString) {
  if (!dateString) return "Ingen deadline";
  const date = new Date(dateString);
  return date.toLocaleDateString("da-DK", {
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

function renderTasks() {
  elements.list.innerHTML = "";
  const visibleTasks = tasks.filter(matchesFilter);

  if (visibleTasks.length === 0) {
    const empty = document.createElement("p");
    empty.textContent = "Ingen opgaver i denne visning.";
    elements.list.appendChild(empty);
    updateSummary();
    return;
  }

  visibleTasks.forEach((task) => {
    const card = document.createElement("article");
    card.className = `task-card${task.done ? " done" : ""}`;

    const header = document.createElement("header");
    const title = document.createElement("h3");
    title.textContent = task.title;
    const tag = document.createElement("span");
    tag.className = "tag";
    tag.textContent = task.category || "Generelt";
    header.append(title, tag);

    const meta = document.createElement("div");
    meta.className = "task-meta";
    meta.innerHTML = `
      <span>Deadline: ${formatDate(task.due)}</span>
      <span>Status: ${task.done ? "Færdig" : "Åben"}</span>
    `;

    const notes = document.createElement("p");
    notes.textContent = task.notes || "Ingen noter endnu.";

    const actions = document.createElement("div");
    actions.className = "task-actions";

    const toggle = document.createElement("button");
    toggle.type = "button";
    toggle.textContent = task.done ? "Markér åben" : "Markér færdig";
    toggle.addEventListener("click", () => toggleTask(task.id));

    const edit = document.createElement("button");
    edit.type = "button";
    edit.textContent = "Redigér";
    edit.addEventListener("click", () => editTask(task.id));

    const remove = document.createElement("button");
    remove.type = "button";
    remove.textContent = "Slet";
    remove.addEventListener("click", () => deleteTask(task.id));

    actions.append(toggle, edit, remove);

    card.append(header, meta, notes, actions);
    elements.list.appendChild(card);
  });

  updateSummary();
}

function addTask(event) {
  event.preventDefault();
  const formData = new FormData(elements.form);
  const newTask = {
    id: crypto.randomUUID(),
    title: formData.get("title").toString().trim(),
    category: formData.get("category").toString().trim(),
    due: formData.get("due").toString(),
    notes: formData.get("notes").toString().trim(),
    done: false,
  };

  if (!newTask.title) {
    return;
  }

  tasks = [newTask, ...tasks];
  saveTasks();
  elements.form.reset();
  renderTasks();
}

function toggleTask(id) {
  tasks = tasks.map((task) =>
    task.id === id ? { ...task, done: !task.done } : task
  );
  saveTasks();
  renderTasks();
}

function editTask(id) {
  const task = tasks.find((item) => item.id === id);
  if (!task) return;
  const title = prompt("Opdater opgaven", task.title);
  if (title === null) return;
  const category = prompt("Kategori", task.category);
  if (category === null) return;
  const due = prompt("Deadline (YYYY-MM-DD)", task.due || "");
  if (due === null) return;
  const notes = prompt("Noter", task.notes || "");
  if (notes === null) return;

  tasks = tasks.map((item) =>
    item.id === id
      ? {
          ...item,
          title: title.trim(),
          category: category.trim(),
          due: due.trim(),
          notes: notes.trim(),
        }
      : item
  );
  saveTasks();
  renderTasks();
}

function deleteTask(id) {
  const confirmed = confirm("Er du sikker på at du vil slette opgaven?");
  if (!confirmed) return;
  tasks = tasks.filter((task) => task.id !== id);
  saveTasks();
  renderTasks();
}

function setFilter(filter) {
  activeFilter = filter;
  elements.filters.forEach((button) => {
    button.classList.toggle("is-active", button.dataset.filter === filter);
  });
  renderTasks();
}

function exportTasks() {
  const blob = new Blob([JSON.stringify(tasks, null, 2)], {
    type: "application/json",
  });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "konfirmation-tasks.json";
  link.click();
  URL.revokeObjectURL(url);
}

function importTasks(event) {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = () => {
    try {
      const imported = JSON.parse(reader.result);
      tasks = imported.map((task) => ({
        ...task,
        id: task.id ?? crypto.randomUUID(),
      }));
      saveTasks();
      renderTasks();
    } catch (error) {
      alert("Filen kunne ikke læses.");
    }
  };
  reader.readAsText(file);
}

function resetTasks() {
  const confirmed = confirm("Nulstil alle opgaver?");
  if (!confirmed) return;
  tasks = defaultTasks.map((task) => ({ ...task, id: crypto.randomUUID() }));
  saveTasks();
  renderTasks();
}

function init() {
  updateCountdown();
  updateSummary();
  renderTasks();
  elements.form.addEventListener("submit", addTask);
  elements.filters.forEach((button) =>
    button.addEventListener("click", () => setFilter(button.dataset.filter))
  );
  elements.exportButton.addEventListener("click", exportTasks);
  elements.importInput.addEventListener("change", importTasks);
  elements.resetButton.addEventListener("click", resetTasks);
}

init();
setInterval(updateCountdown, 1000 * 60 * 60);
