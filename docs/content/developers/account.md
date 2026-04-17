---
title: "Panel de cuenta"
description: "Consulta tu perfil de desarrollador y gestiona tus API keys."
type: "developers"
layout: "single"
---

<div class="api-section" id="api-account">
<div class="api-key-entry">
<h2>Tu API key</h2>
<p>Introduce tu API key para acceder a tu perfil y gestionar tus claves. La clave se guarda temporalmente en la sesión del navegador y se elimina al cerrar la pestaña.</p>
<div class="api-form__group">
<label for="account-api-key-input" class="api-form__label">API key</label>
<div class="api-key-entry__row">
<input type="password" id="account-api-key-input" class="api-form__input" placeholder="sep_xxxxxxxxxxxxxxxx">
<button type="button" id="account-save-key" class="btn btn-primary btn-sm">Guardar en sesión</button>
<button type="button" id="account-logout" class="btn btn-secondary btn-sm">Cerrar sesión</button>
</div>
</div>
</div>
<div id="account-feedback" class="api-feedback" hidden></div>
<div class="api-account-actions">
<h2>Gestión de cuenta</h2>
<div class="api-account-actions__grid">
<div class="api-account-action-card">
<h3>Ver perfil</h3>
<p>Consulta tu información de desarrollador y el estado de tu API key activa.</p>
<button type="button" id="account-load-profile" class="btn btn-secondary">Cargar perfil</button>
</div>
<div class="api-account-action-card">
<h3>Rotar API key</h3>
<p>Genera una nueva API key. La clave actual será revocada tras un periodo de gracia.</p>
<button type="button" id="account-rotate" class="btn btn-secondary">Rotar clave</button>
</div>
<div class="api-account-action-card">
<h3>Revocar API keys</h3>
<p>Revoca inmediatamente <strong>todas</strong> tus API keys activas. Perderás el acceso y tendrás que <a href="../recover/">restaurarlo por email</a>.</p>
<button type="button" id="account-revoke" class="btn btn-secondary api-btn-danger">Revocar todas</button>
</div>
</div>
<h2>Tus datos</h2>
<div class="api-account-actions__grid">
<div class="api-account-action-card">
<h3>Exportar mis datos</h3>
<p>Descarga una copia de todos tus datos personales en formato JSON (derecho de portabilidad).</p>
<button type="button" id="account-export" class="btn btn-secondary">Exportar datos</button>
</div>
<div class="api-account-action-card">
<h3>Eliminar cuenta</h3>
<p>Elimina tu cuenta y anonimiza todos tus datos personales. Esta acción es <strong>irreversible</strong>.</p>
<button type="button" id="account-delete" class="btn btn-secondary api-btn-danger">Eliminar cuenta</button>
</div>
</div>
</div>
<div id="account-key-container" hidden></div>
<div id="account-profile" hidden></div>
<p class="api-form__footer"><a href="../">Volver a Desarrolladores</a> · <a href="../recover/">Recuperar acceso</a></p>
</div>
