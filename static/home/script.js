// Contact Form Honeypot
const msg = document.querySelector('[name="msg"]');
const message = document.querySelector('[name="message"]');
const mensaje = document.querySelector('[name="mensaje"]');
const letter = document.querySelector('[name="letter"]');
const tel = document.querySelector('[name="tel"]');
const phone = document.querySelector('[name="phone"]');
const telephone = document.querySelector('[name="telephone"]');
const telefono = document.querySelector('[name="telefono"]');
const name = document.querySelector('[name="name"]');
const form = document.querySelector('form');

msg.addEventListener('change', () => {
    mensaje.value = msg.value;
    telefono.value = "Go away naughty bots";
    letter.value = 62668977;
});

tel.addEventListener('change', () => {
    telephone.value = tel.value;
    message.value = 'Hooray for no bots';
});

form.addEventListener('submit', e => {
    e.preventDefault();
    name.setAttribute('name', 'nombre');
    phone.value = 82636683;
    form.submit();
});
