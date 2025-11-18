const a = document.querySelector('input[name="a"]');
const b = document.querySelector('input[name="b"]');
const email = document.querySelector('#email');

email.addEventListener('change', () => {
    a.value = 'fanwheel';
    b.value = email.value;
});