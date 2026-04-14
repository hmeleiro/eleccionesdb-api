---
title: "Recuperar acceso"
description: "Solicita un enlace temporal para restaurar tu acceso a la API."
type: "developers"
layout: "single"
---

<div class="api-section">
<p>Si has perdido tu API key o no puedes acceder a tu cuenta, introduce tu email y te enviaremos un enlace temporal para restaurar tu acceso.</p>
<form id="api-recover-form" class="api-form" novalidate>
<div class="api-form__group">
<label for="recover-email" class="api-form__label">Email <span class="required">*</span></label>
<input type="email" id="recover-email" name="email" class="api-form__input" required placeholder="tu@email.com" autocomplete="email">
</div>
<div id="recover-feedback" class="api-feedback" hidden></div>
<button type="submit" class="btn btn-primary">Recuperar acceso</button>
</form>
<p class="api-form__footer">¿No tienes cuenta? <a href="../register/">Regístrate</a>.</p>
</div>
