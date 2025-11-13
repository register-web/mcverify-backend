const tg = window.Telegram?.WebApp;
tg?.ready();
tg?.expand?.();

const rawBase = document.body.dataset.apiBase || "https://mcverify.up.railway.app/api";
const API_BASE = rawBase.replace(/\/$/, "");
const endpoints = {
  register: `${API_BASE}/register`,
  setPassword: `${API_BASE}/set_password`,
  changeName: `${API_BASE}/change_name`,
};

const ui = {
  cards: {
    loading: document.getElementById("loading-card"),
    success: document.getElementById("success-card"),
    error: document.getElementById("error-card"),
    profile: document.getElementById("profile-card"),
  },
  loadingText: document.getElementById("loading-text"),
  successTitle: document.getElementById("success-title"),
  successDescription: document.getElementById("success-description"),
  bindButton: document.getElementById("bind-button"),
  successBack: document.getElementById("success-back"),
  errorText: document.getElementById("error-text"),
  retryButton: document.getElementById("retry-button"),
  profileStatus: document.getElementById("profile-status"),
  playerName: document.getElementById("player-name"),
  playerTelegram: document.getElementById("player-telegram"),
  playerIp: document.getElementById("player-ip"),
  playerLastCheck: document.getElementById("player-last-check"),
  playerVerified: document.getElementById("player-verified"),
  setPassword: document.getElementById("set-password"),
  changeName: document.getElementById("change-name"),
};

const state = createStateController(ui);
const telegramData = serializeTelegramData(tg?.initDataUnsafe ?? {});
const urlParams = new URLSearchParams(window.location.search);
const inviteCode = urlParams.get("code") || telegramData.start_param || "";
const ipPromise = detectIp();

init();

function init() {
  if (!tg || !telegramData.hash) {
    state.showError("Запустите приложение из Telegram, чтобы авторизация работала корректно.");
    return;
  }
  state.showLoading("Готовим приложение...");
  setTimeout(() => state.showBind(inviteCode), 200);
}

ui.bindButton.addEventListener("click", async () => {
  await attemptRegister();
});

ui.retryButton.addEventListener("click", () => {
  state.showBind(inviteCode);
});

ui.successBack.addEventListener("click", () => {
  if (state.profile) {
    state.showProfile(state.profile);
  } else {
    state.showBind(inviteCode);
  }
});

ui.setPassword.addEventListener("click", async () => {
  const profile = state.profile;
  if (!profile) {
    state.showBind(inviteCode);
    return;
  }
  const password = prompt("Введите новый пароль (минимум 6 символов):");
  if (!password) {
    return;
  }
  if (password.length < 6) {
    alert("Пароль должен содержать минимум 6 символов.");
    return;
  }
  state.showLoading("Сохраняем пароль...");
  try {
    const updated = await postJson(endpoints.setPassword, {
      telegram_id: profile.telegram_id,
      password,
    });
    state.showProfile(updated);
    state.showSuccess("Пароль для Minecraft сохранён.");
    tg?.HapticFeedback?.notificationOccurred?.("success");
  } catch (error) {
    state.showError(error.message);
  }
});

ui.changeName.addEventListener("click", async () => {
  const profile = state.profile;
  if (!profile) {
    state.showBind(inviteCode);
    return;
  }
  const name = prompt("Введите новый никнейм:", profile.player_name || "");
  if (!name || name === profile.player_name) {
    return;
  }
  state.showLoading("Обновляем никнейм...");
  try {
    const updated = await postJson(endpoints.changeName, {
      telegram_id: profile.telegram_id,
      new_name: name.trim(),
    });
    state.showProfile(updated);
    state.showSuccess("Никнейм успешно изменён.");
    tg?.HapticFeedback?.notificationOccurred?.("success");
  } catch (error) {
    state.showError(error.message);
  }
});

async function attemptRegister() {
  state.showLoading("Привязываем аккаунт...");
  try {
    const ip = await ipPromise;
    const profile = await postJson(endpoints.register, {
      telegram_data: telegramData,
      code: inviteCode,
      ip,
    });
    state.showProfile(profile);
    tg?.HapticFeedback?.notificationOccurred?.("success");
  } catch (error) {
    state.showError(error.message);
  }
}

function createStateController(elements) {
  let currentProfile = null;

  const hideAll = () =>
    Object.values(elements.cards).forEach((card) => card.classList.add("hidden"));

  const badge = elements.profileStatus;

  const setBadge = (status) => {
    badge.classList.remove("status-ok", "status-warn", "status-muted");
    badge.classList.add(status);
  };

  return {
    get profile() {
      return currentProfile;
    },
    showLoading(message = "Загрузка...") {
      hideAll();
      elements.loadingText.textContent = message;
      elements.cards.loading.classList.remove("hidden");
    },
    showBind(code) {
      hideAll();
      elements.successTitle.textContent = "Привязать аккаунт";
      elements.successDescription.textContent = code
        ? `Нажмите кнопку ниже, чтобы привязать код ${code} к вашему Minecraft-профилю.`
        : "Нажмите кнопку, чтобы связать Telegram и Minecraft.";
      elements.bindButton.classList.remove("hidden");
      elements.bindButton.disabled = false;
      elements.successBack.classList.add("hidden");
      elements.cards.success.classList.remove("hidden");
    },
    showSuccess(message) {
      hideAll();
      elements.successTitle.textContent = "Готово!";
      elements.successDescription.textContent = message;
      elements.bindButton.classList.add("hidden");
      elements.successBack.classList.remove("hidden");
      elements.cards.success.classList.remove("hidden");
    },
    showError(message) {
      hideAll();
      elements.errorText.textContent = message || "Неизвестная ошибка. Повторите позже.";
      elements.cards.error.classList.remove("hidden");
    },
    showProfile(profile) {
      currentProfile = profile;
      hideAll();
      renderProfile(profile);
      elements.cards.profile.classList.remove("hidden");
    },
  };

  function renderProfile(profile) {
    elements.playerName.textContent = profile.player_name || "—";
    elements.playerTelegram.textContent = formatTelegram(profile);
    elements.playerIp.textContent = profile.ip || "—";
    elements.playerLastCheck.textContent = formatDate(profile.last_verified);
    const verified = Boolean(profile.verified);
    elements.playerVerified.textContent = verified ? "Подтверждён" : "Нужна реверификация";
    elements.profileStatus.textContent = verified ? "Подтверждён" : "Нужно обновить";
    setBadge(verified ? "status-ok" : "status-warn");
  }
}

async function postJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await safeJson(response);
  if (!response.ok) {
    const detail = data?.detail || data?.message;
    throw new Error(detail || "Сервер вернул ошибку");
  }
  return data;
}

async function detectIp() {
  try {
    const res = await fetch("https://api.ipify.org?format=json");
    if (!res.ok) {
      throw new Error("Failed to detect IP");
    }
    const payload = await res.json();
    return payload.ip;
  } catch {
    return "0.0.0.0";
  }
}

function serializeTelegramData(data) {
  try {
    return JSON.parse(JSON.stringify(data));
  } catch {
    return {};
  }
}

function formatTelegram(profile) {
  if (profile.telegram_username) {
    return `@${profile.telegram_username}`;
  }
  if (profile.telegram_id) {
    return `ID: ${profile.telegram_id}`;
  }
  return "—";
}

function formatDate(date) {
  if (!date) {
    return "—";
  }
  try {
    const dt = new Date(date);
    return new Intl.DateTimeFormat("ru-RU", {
      dateStyle: "medium",
      timeStyle: "short",
    }).format(dt);
  } catch {
    return String(date);
  }
}

async function safeJson(response) {
  try {
    return await response.json();
  } catch {
    return null;
  }
}
