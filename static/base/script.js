const menuButton = document.querySelector('#menu-button');
const menu = document.querySelector('#menu');

menuButton.addEventListener('click', () => {
    switch(menu.getAttribute('class')) {
        case 'in':
            menu.setAttribute('class', 'out');
            break;
        case 'out':
            menu.setAttribute('class', 'in');
            break;
    }
});