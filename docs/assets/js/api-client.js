/**
 * EleccionesDB API — Developer Portal Client
 *
 * Cliente ligero para los endpoints de autenticación y gestión
 * de cuenta. La URL base se inyecta desde Hugo en el atributo
 * data-api-base del <body>.
 *
 * Seguridad:
 * - La API key se almacena SOLO en sessionStorage y se borra al
 *   cerrar la pestaña. Esto evita persistirla en disco (localStorage)
 *   pero sigue accesible a cualquier JS en la misma página. En un
 *   sitio estático sin dependencias de terceros el riesgo es bajo.
 * - Nunca se inserta HTML proveniente del backend sin escapar.
 */

(function () {
  "use strict";

  /* --------------------------------------------------------- */
  /*  Configuración                                             */
  /* --------------------------------------------------------- */

  const API_BASE = (
    document.body.dataset.apiBase || "https://api.spainelectoralproject.com"
  ).replace(/\/+$/, "");

  const SESSION_KEY = "sep_api_key";

  /* --------------------------------------------------------- */
  /*  Helpers                                                   */
  /* --------------------------------------------------------- */

  /** Muestra un bloque de feedback (#id) con clase y mensaje */
  function showFeedback(id, type, message) {
    const el = document.getElementById(id);
    if (!el) return;
    el.className = "api-feedback api-feedback--" + type;
    el.innerHTML = "";
    const p = document.createElement("p");
    p.textContent = message;
    el.appendChild(p);
    el.hidden = false;
  }

  function hideFeedback(id) {
    const el = document.getElementById(id);
    if (!el) return;
    el.hidden = true;
  }

  /** Petición genérica con manejo de errores */
  async function request(path, opts) {
    const url = API_BASE + path;
    const headers = Object.assign(
      { "Content-Type": "application/json" },
      opts.headers || {},
    );
    const config = {
      method: opts.method || "GET",
      headers: headers,
    };
    if (opts.body) config.body = JSON.stringify(opts.body);
    const res = await fetch(url, config);
    let data = null;
    const ct = res.headers.get("content-type") || "";
    if (ct.includes("application/json")) {
      try {
        data = await res.json();
      } catch (_) {
        /* respuesta vacía o JSON mal formado */
      }
    }
    return { ok: res.ok, status: res.status, data: data };
  }

  function authHeaders() {
    const key = sessionStorage.getItem(SESSION_KEY);
    return key ? { "X-API-Key": key } : {};
  }

  /** Copia texto al portapapeles y muestra confirmación breve */
  function copyToClipboard(text, btnEl) {
    navigator.clipboard.writeText(text).then(function () {
      const prev = btnEl.textContent;
      btnEl.textContent = "¡Copiada!";
      setTimeout(function () {
        btnEl.textContent = prev;
      }, 2000);
    });
  }

  /** Construye un bloque visual para mostrar una API key nueva */
  function renderNewKey(containerEl, apiKey) {
    containerEl.innerHTML = "";
    const wrapper = document.createElement("div");
    wrapper.className = "api-key-display";

    const label = document.createElement("p");
    label.className = "api-key-display__warning";
    label.textContent =
      "⚠ Esta clave solo se mostrará una vez. Cópiala y guárdala en un lugar seguro.";
    wrapper.appendChild(label);

    const row = document.createElement("div");
    row.className = "api-key-display__row";

    const code = document.createElement("code");
    code.className = "api-key-display__value";
    code.textContent = apiKey;
    row.appendChild(code);

    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "btn btn-secondary btn-sm";
    btn.textContent = "Copiar";
    btn.addEventListener("click", function () {
      copyToClipboard(apiKey, btn);
    });
    row.appendChild(btn);

    wrapper.appendChild(row);
    containerEl.appendChild(wrapper);
    containerEl.hidden = false;
  }

  /** Extrae un mensaje de error legible desde la respuesta */
  function errorMsg(res, fallback) {
    if (res.data) {
      if (typeof res.data.detail === "string") return res.data.detail;
      if (typeof res.data.message === "string") return res.data.message;
      if (typeof res.data.error === "string") return res.data.error;
    }
    return fallback || "Ha ocurrido un error inesperado.";
  }

  /* --------------------------------------------------------- */
  /*  Reenvío de verificación — helper inline                   */
  /* --------------------------------------------------------- */

  /**
   * Muestra en el bloque de feedback un aviso con botón para reenviar
   * el email de verificación cuando la cuenta ya existe en estado pendiente.
   */
  async function showResendVerificationPrompt(feedbackId, email) {
    const el = document.getElementById(feedbackId);
    if (!el) return;
    el.className = "api-feedback api-feedback--warning";
    el.innerHTML = "";

    const p = document.createElement("p");
    p.textContent =
      "Ya existe un registro pendiente de verificación con este email. ¿Quieres que te reenviemos el correo de verificación?";
    el.appendChild(p);

    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "btn btn-secondary btn-sm";
    btn.textContent = "Reenviar correo de verificación";
    btn.addEventListener("click", async function () {
      btn.disabled = true;
      btn.textContent = "Enviando…";
      try {
        const res = await request("/v1/auth/resend-verification", {
          method: "POST",
          body: { email: email },
        });
        if (res.ok) {
          el.className = "api-feedback api-feedback--success";
          el.innerHTML = "";
          const msg = document.createElement("p");
          msg.textContent =
            "Correo de verificación reenviado. Revisa tu bandeja de entrada.";
          el.appendChild(msg);
        } else {
          btn.disabled = false;
          btn.textContent = "Reenviar correo de verificación";
          const msg = document.createElement("p");
          msg.className = "api-feedback__error";
          msg.textContent = errorMsg(
            res,
            "No se pudo reenviar el correo. Inténtalo de nuevo.",
          );
          el.appendChild(msg);
        }
      } catch (err) {
        btn.disabled = false;
        btn.textContent = "Reenviar correo de verificación";
        const msg = document.createElement("p");
        msg.className = "api-feedback__error";
        msg.textContent =
          "No se pudo conectar con el servidor. Inténtalo de nuevo.";
        el.appendChild(msg);
      }
    });

    el.appendChild(btn);
    el.hidden = false;
  }

  /* --------------------------------------------------------- */
  /*  Registro  — /developers/register/                         */
  /* --------------------------------------------------------- */

  function initRegister() {
    const form = document.getElementById("api-register-form");
    if (!form) return;

    form.addEventListener("submit", async function (e) {
      e.preventDefault();
      const btn = form.querySelector('button[type="submit"]');
      btn.disabled = true;
      btn.textContent = "Enviando…";
      hideFeedback("register-feedback");

      const payload = {
        email: form.email.value.trim(),
        name: form.nombre.value.trim(),
        organization: form.organizacion.value.trim(),
        intended_use: form.uso_previsto.value.trim(),
      };

      try {
        const res = await request("/v1/auth/register", {
          method: "POST",
          body: payload,
        });

        if (res.ok) {
          showFeedback(
            "register-feedback",
            "success",
            "Registro enviado correctamente. Revisa tu correo electrónico para verificar tu cuenta.",
          );
          form.reset();
        } else if (
          res.status === 409 &&
          typeof res.data?.detail === "string" &&
          res.data.detail.includes("pendiente")
        ) {
          const emailValue = payload.email;
          showResendVerificationPrompt("register-feedback", emailValue);
        } else if (res.status === 422) {
          showFeedback(
            "register-feedback",
            "error",
            errorMsg(res, "Error de validación. Revisa los campos."),
          );
        } else {
          showFeedback("register-feedback", "error", errorMsg(res));
        }
      } catch (err) {
        console.error("[API] Register error:", err);
        showFeedback(
          "register-feedback",
          "error",
          "No se pudo conectar con el servidor. Inténtalo de nuevo. (" +
            err.message +
            ")",
        );
      }

      btn.disabled = false;
      btn.textContent = "Registrarse";
    });
  }

  /* --------------------------------------------------------- */
  /*  Recuperación de acceso — /developers/recover/              */
  /* --------------------------------------------------------- */

  function initRecover() {
    const form = document.getElementById("api-recover-form");
    if (!form) return;

    form.addEventListener("submit", async function (e) {
      e.preventDefault();
      const btn = form.querySelector('button[type="submit"]');
      btn.disabled = true;
      btn.textContent = "Enviando…";
      hideFeedback("recover-feedback");

      const payload = { email: form.email.value.trim() };

      try {
        const res = await request("/v1/auth/recover-access", {
          method: "POST",
          body: payload,
        });

        // Siempre mostramos un mensaje genérico para no filtrar información
        showFeedback(
          "recover-feedback",
          "success",
          "Si existe una cuenta con ese email, recibirás un enlace para restaurar tu acceso.",
        );
        form.reset();
      } catch (_) {
        showFeedback(
          "recover-feedback",
          "error",
          "No se pudo conectar con el servidor. Inténtalo de nuevo.",
        );
      }

      btn.disabled = false;
      btn.textContent = "Recuperar acceso";
    });
  }

  /* --------------------------------------------------------- */
  /*  Restauración de sesión — /developers/restore/              */
  /* --------------------------------------------------------- */

  function initRestore() {
    const container = document.getElementById("api-restore");
    if (!container) return;

    const token = new URLSearchParams(window.location.search).get("token");
    if (!token) {
      showFeedback(
        "restore-feedback",
        "error",
        "No se ha proporcionado un token de restauración.",
      );
      return;
    }

    showFeedback("restore-feedback", "loading", "Restaurando sesión…");

    request("/v1/auth/restore-session?token=" + encodeURIComponent(token), {
      method: "GET",
    })
      .then(function (res) {
        if (res.ok) {
          showFeedback(
            "restore-feedback",
            "success",
            "Sesión restaurada correctamente.",
          );

          if (res.data && res.data.api_key) {
            sessionStorage.setItem(SESSION_KEY, res.data.api_key);
            renderNewKey(
              document.getElementById("restore-key-container"),
              res.data.api_key,
            );
          }

          if (res.data) {
            renderProfile(document.getElementById("restore-profile"), res.data);
          }
        } else if (
          res.status === 400 ||
          res.status === 401 ||
          res.status === 404
        ) {
          showFeedback(
            "restore-feedback",
            "error",
            errorMsg(res, "El enlace es inválido o ha expirado."),
          );
        } else {
          showFeedback("restore-feedback", "error", errorMsg(res));
        }
      })
      .catch(function () {
        showFeedback(
          "restore-feedback",
          "error",
          "No se pudo conectar con el servidor.",
        );
      });
  }

  /** Muestra datos de perfil básicos recibidos desde la API */
  function renderProfile(container, data) {
    if (!container) return;
    const fields = [
      ["Email", data.email],
      ["Nombre", data.nombre || data.name],
      ["Organización", data.organizacion || data.organization],
    ];

    container.innerHTML = "";
    const dl = document.createElement("dl");
    dl.className = "api-profile-list";
    fields.forEach(function (f) {
      if (!f[1]) return;
      var dt = document.createElement("dt");
      dt.textContent = f[0];
      var dd = document.createElement("dd");
      dd.textContent = f[1];
      dl.appendChild(dt);
      dl.appendChild(dd);
    });
    container.appendChild(dl);
    container.hidden = false;
  }

  /* --------------------------------------------------------- */
  /*  Panel de cuenta — /developers/account/                     */
  /* --------------------------------------------------------- */

  function initAccount() {
    const section = document.getElementById("api-account");
    if (!section) return;

    const keyInput = document.getElementById("account-api-key-input");
    const saveKeyBtn = document.getElementById("account-save-key");
    const loadProfileBtn = document.getElementById("account-load-profile");
    const rotateBtn = document.getElementById("account-rotate");
    const revokeBtn = document.getElementById("account-revoke");
    const logoutBtn = document.getElementById("account-logout");
    const profileContainer = document.getElementById("account-profile");
    const keyContainer = document.getElementById("account-key-container");

    // Restaurar API key si estaba guardada en sessionStorage
    const stored = sessionStorage.getItem(SESSION_KEY);
    if (stored) {
      keyInput.value = stored;
    }

    saveKeyBtn.addEventListener("click", function () {
      const val = keyInput.value.trim();
      if (!val) {
        showFeedback("account-feedback", "error", "Introduce tu API key.");
        return;
      }
      sessionStorage.setItem(SESSION_KEY, val);
      showFeedback(
        "account-feedback",
        "success",
        "API key guardada en la sesión.",
      );
    });

    logoutBtn.addEventListener("click", function () {
      sessionStorage.removeItem(SESSION_KEY);
      keyInput.value = "";
      profileContainer.innerHTML = "";
      profileContainer.hidden = true;
      keyContainer.innerHTML = "";
      keyContainer.hidden = true;
      hideFeedback("account-feedback");
      showFeedback(
        "account-feedback",
        "success",
        "Sesión cerrada. Tu API key ha sido eliminada del navegador.",
      );
    });

    // Cargar perfil
    loadProfileBtn.addEventListener("click", async function () {
      ensureKeySaved();
      if (!sessionStorage.getItem(SESSION_KEY)) return;

      loadProfileBtn.disabled = true;
      showFeedback("account-feedback", "loading", "Cargando perfil…");

      try {
        const res = await request("/v1/developers/me", {
          method: "GET",
          headers: authHeaders(),
        });

        if (res.ok && res.data) {
          hideFeedback("account-feedback");
          renderAccountProfile(profileContainer, res.data);
        } else if (res.status === 401 || res.status === 403) {
          showFeedback(
            "account-feedback",
            "error",
            "API key inválida o sin permisos.",
          );
        } else {
          showFeedback("account-feedback", "error", errorMsg(res));
        }
      } catch (_) {
        showFeedback(
          "account-feedback",
          "error",
          "No se pudo conectar con el servidor.",
        );
      }

      loadProfileBtn.disabled = false;
    });

    // Rotar clave
    rotateBtn.addEventListener("click", async function () {
      ensureKeySaved();
      if (!sessionStorage.getItem(SESSION_KEY)) return;

      if (
        !confirm(
          "¿Seguro que quieres rotar tu API key? La clave actual será revocada tras un periodo de gracia.",
        )
      ) {
        return;
      }

      rotateBtn.disabled = true;
      showFeedback("account-feedback", "loading", "Rotando API key…");

      try {
        const res = await request("/v1/developers/me/api-keys/rotate", {
          method: "POST",
          headers: authHeaders(),
        });

        if (res.ok && res.data) {
          const newKey = res.data.api_key || res.data.key;
          if (newKey) {
            sessionStorage.setItem(SESSION_KEY, newKey);
            keyInput.value = newKey;
            renderNewKey(keyContainer, newKey);
          }
          showFeedback(
            "account-feedback",
            "success",
            "API key rotada correctamente.",
          );
        } else {
          showFeedback("account-feedback", "error", errorMsg(res));
        }
      } catch (_) {
        showFeedback(
          "account-feedback",
          "error",
          "No se pudo conectar con el servidor.",
        );
      }

      rotateBtn.disabled = false;
    });

    // Revocar claves
    revokeBtn.addEventListener("click", async function () {
      if (
        !confirm(
          "¿Seguro que quieres revocar TODAS tus API keys? Perderás el acceso inmediatamente y tendrás que restaurarlo por email.",
        )
      ) {
        return;
      }

      ensureKeySaved();
      if (!sessionStorage.getItem(SESSION_KEY)) return;

      revokeBtn.disabled = true;

      try {
        const res = await request("/v1/developers/me/api-keys/revoke", {
          method: "POST",
          headers: authHeaders(),
        });

        if (res.ok) {
          sessionStorage.removeItem(SESSION_KEY);
          keyInput.value = "";
          profileContainer.innerHTML = "";
          profileContainer.hidden = true;
          showFeedback(
            "account-feedback",
            "success",
            "Todas tus API keys han sido revocadas. Para recuperar el acceso, usa la opción de recuperación de acceso.",
          );
        } else {
          showFeedback("account-feedback", "error", errorMsg(res));
        }
      } catch (_) {
        showFeedback(
          "account-feedback",
          "error",
          "No se pudo conectar con el servidor.",
        );
      }

      revokeBtn.disabled = false;
    });

    function ensureKeySaved() {
      const val = keyInput.value.trim();
      if (val) {
        sessionStorage.setItem(SESSION_KEY, val);
      }
      if (!sessionStorage.getItem(SESSION_KEY)) {
        showFeedback(
          "account-feedback",
          "error",
          "Introduce tu API key primero.",
        );
      }
    }
  }

  function renderAccountProfile(container, data) {
    container.innerHTML = "";
    container.hidden = false;

    // Perfil del desarrollador
    const h3 = document.createElement("h3");
    h3.textContent = "Tu perfil";
    container.appendChild(h3);

    const profileFields = [
      ["Email", data.email],
      ["Nombre", data.nombre || data.name],
      ["Organización", data.organizacion || data.organization],
      ["Uso previsto", data.uso_previsto || data.intended_use],
      ["Registrado", data.created_at],
    ];

    const dl = document.createElement("dl");
    dl.className = "api-profile-list";
    profileFields.forEach(function (f) {
      if (!f[1]) return;
      var dt = document.createElement("dt");
      dt.textContent = f[0];
      var dd = document.createElement("dd");
      dd.textContent = f[1];
      dl.appendChild(dt);
      dl.appendChild(dd);
    });
    container.appendChild(dl);

    // Info de la API key activa
    var keyInfo = data.api_key || data.active_key;
    if (keyInfo && typeof keyInfo === "object") {
      var h3b = document.createElement("h3");
      h3b.textContent = "API key activa";
      h3b.style.marginTop = "var(--space-6)";
      container.appendChild(h3b);

      var keyFields = [
        ["Prefijo", keyInfo.prefix || keyInfo.key_prefix],
        ["Estado", keyInfo.status || keyInfo.state],
        ["Creada", keyInfo.created_at],
        ["Expira", keyInfo.expires_at],
      ];

      var dl2 = document.createElement("dl");
      dl2.className = "api-profile-list";
      keyFields.forEach(function (f) {
        if (!f[1]) return;
        var dt = document.createElement("dt");
        dt.textContent = f[0];
        var dd = document.createElement("dd");
        dd.textContent = f[1];
        dl2.appendChild(dt);
        dl2.appendChild(dd);
      });
      container.appendChild(dl2);
    }
  }

  /* --------------------------------------------------------- */
  /*  Inicialización                                            */
  /* --------------------------------------------------------- */

  document.addEventListener("DOMContentLoaded", function () {
    initRegister();
    initRecover();
    initRestore();
    initAccount();
  });
})();
