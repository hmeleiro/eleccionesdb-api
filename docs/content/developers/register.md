---
title: "Registro de desarrollador"
description: "Solicita acceso a la API de eleccionesdb."
type: "developers"
layout: "single"
---

<div class="api-section">
<p>Rellena el formulario para solicitar acceso a la API. Recibirás un email de verificación con instrucciones para activar tu cuenta.</p>
<form id="api-register-form" class="api-form" novalidate>
<div class="api-form__group">
<label for="reg-email" class="api-form__label">Email <span class="required">*</span></label>
<input type="email" id="reg-email" name="email" class="api-form__input" required placeholder="tu@email.com" autocomplete="email">
</div>
<div class="api-form__group">
<label for="reg-nombre" class="api-form__label">Nombre <span class="required">*</span></label>
<input type="text" id="reg-nombre" name="nombre" class="api-form__input" required placeholder="Tu nombre" autocomplete="name">
</div>
<div class="api-form__group">
<label for="reg-organizacion" class="api-form__label">Organización</label>
<input type="text" id="reg-organizacion" name="organizacion" class="api-form__input" placeholder="Universidad, medio, empresa…" autocomplete="organization">
</div>
<div class="api-form__group">
<label for="reg-uso" class="api-form__label">Uso previsto <span class="required">*</span></label>
<textarea id="reg-uso" name="uso_previsto" class="api-form__input api-form__textarea" required placeholder="Describe brevemente para qué quieres usar la API" rows="3"></textarea>
</div>
<div id="register-feedback" class="api-feedback" hidden></div>
<button type="submit" class="btn btn-primary">Registrarse</button>
</form>
<p class="api-form__footer">¿Ya tienes una cuenta? <a href="../account/">Accede a tu panel</a>. ¿Has perdido tu API key? <a href="../recover/">Recupera tu acceso</a>.</p>
</div>
