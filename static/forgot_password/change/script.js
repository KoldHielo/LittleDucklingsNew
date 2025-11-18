const a = document.querySelector('input[name="a"]');
const b = document.querySelector('input[name="b"]');
const form = document.querySelector('form');
const email = document.querySelector('#email');
const password = document.querySelector('#password');
const confirmPassword = document.querySelector('#confirm_password');

const clientEmail = email.value;

confirmPassword.addEventListener('change', () => {
    a.value = 'monsterbiscuit';
    b.value = email.value;
});

email.addEventListener('change', () => {
    email.value = clientEmail;
});

form.addEventListener('submit', e => {
    e.preventDefault();
    const errorMessage = (!validatePasswords(password.value, confirmPassword.value)) ? 'Password\'s criterea not fulfilled and/or passwords do not match. Please try again.' :
                          null;
                          
    if(errorMessage == null) {
        form.submit();
    } else {
        alert(errorMessage);
    };
});