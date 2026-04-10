const menuButton = document.querySelector('#menu-button');
const menu = document.querySelector('#menu');

if (menuButton && menu) {
    const closeMenu = () => {
        menu.classList.remove('in');
        menu.classList.add('out');
        menuButton.setAttribute('aria-expanded', 'false');
        menuButton.setAttribute('aria-label', 'Open site navigation');
    };

    const openMenu = () => {
        menu.classList.remove('out');
        menu.classList.add('in');
        menuButton.setAttribute('aria-expanded', 'true');
        menuButton.setAttribute('aria-label', 'Close site navigation');
    };

    menuButton.addEventListener('click', () => {
        const isOpen = menu.classList.contains('in');

        if (isOpen) {
            closeMenu();
            return;
        }

        openMenu();
    });

    menu.querySelectorAll('a').forEach((link) => {
        link.addEventListener('click', closeMenu);
    });

    window.addEventListener('resize', () => {
        if (window.innerWidth > 960) {
            closeMenu();
        }
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            closeMenu();
        }
    });
}
