document.addEventListener('DOMContentLoaded', function () {
    const navigationMenu = document.querySelector('.js-hamburger-trigger')
    const crayonsIcon = document.querySelector('.crayons-icon')
    const subHeaderContainer = document.querySelector('.crayons-sub-header__container')

    navigationMenu.addEventListener('click', function () {
        subHeaderContainer.style.display =
            subHeaderContainer.style.display === 'block' ? 'none' : 'block';

        // Toggle between hamburger and close icons
        const isHamburger = crayonsIcon.src.includes('hamburger');
        crayonsIcon.src = isHamburger ? navigationMenu.dataset.closeSrc : navigationMenu.dataset.hamburgerSrc;

        // Rotate the icon for a smooth animation
        crayonsIcon.style.transform = isHamburger ? 'rotate(90deg)' : 'rotate(0deg)';
    });
});  
document.addEventListener('DOMContentLoaded', function () {
    'use strict'

    let imgWrapper = document.querySelectorAll('.img-wrapper'),
        dots = document.querySelectorAll('.dots > .dot'),
        i = 0

    function reset() {
        for (let i = 0; i < imgWrapper.length; i++) {
            imgWrapper[i].style.display = 'none'
            dots[i].classList.remove('active')
        }
    }

    function autoSlide() {
        if (i >= imgWrapper.length) {
            i = 0
        }
        reset()
        if (imgWrapper[i]) {
            imgWrapper[i].style.display = 'block'
        }
        if (dots[i]) {
            dots[i].classList.add('active')
        }
        i++
        setTimeout(autoSlide, 6000)
    }
    autoSlide()
});