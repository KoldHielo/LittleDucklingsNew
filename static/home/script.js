const form = document.querySelector('#contact-form');

if (form) {
    const msg = form.querySelector('[name="msg"]');
    const message = form.querySelector('[name="message"]');
    const mensaje = form.querySelector('[name="mensaje"]');
    const letter = form.querySelector('[name="letter"]');
    const tel = form.querySelector('[name="tel"]');
    const phone = form.querySelector('[name="phone"]');
    const telephone = form.querySelector('[name="telephone"]');
    const telefono = form.querySelector('[name="telefono"]');
    const name = form.querySelector('[name="name"]');

    msg?.addEventListener('change', () => {
        if (mensaje) {
            mensaje.value = msg.value;
        }
        if (telefono) {
            telefono.value = 'Go away naughty bots';
        }
        if (letter) {
            letter.value = 62668977;
        }
    });

    tel?.addEventListener('change', () => {
        if (telephone) {
            telephone.value = tel.value;
        }
        if (message) {
            message.value = 'Hooray for no bots';
        }
    });

    form.addEventListener('submit', (event) => {
        event.preventDefault();

        if (name) {
            name.setAttribute('name', 'nombre');
        }
        if (phone) {
            phone.value = 82636683;
        }

        form.submit();
    });
}
