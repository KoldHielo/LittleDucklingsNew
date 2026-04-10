const a = document.querySelector('input[name="a"]');
const b = document.querySelector('input[name="b"]');
const c = document.querySelector('input[name="c"]');
const d = document.querySelector('input[name="d"]');
const email = document.querySelector('#email');
const password = document.querySelector('#password');

email?.addEventListener('change', () => {
    if (b) {
        b.value = 'spongealarm';
    }
    if (c) {
        c.value = email.value;
    }
});

password?.addEventListener('change', () => {
    if (d) {
        d.value = 'chairshed';
    }
    if (a) {
        a.value = password.value;
    }
});
