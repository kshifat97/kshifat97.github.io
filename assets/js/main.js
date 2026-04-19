/*===== NAV MENU TOGGLE =====*/
const navMenu   = document.getElementById('nav-menu'),
      navToggle = document.getElementById('nav-toggle'),
      navClose  = document.getElementById('nav-close')

if (navToggle) {
    navToggle.addEventListener('click', () => navMenu.classList.add('show-menu'))
}
if (navClose) {
    navClose.addEventListener('click', () => navMenu.classList.remove('show-menu'))
}

document.querySelectorAll('.nav__link').forEach(link => {
    link.addEventListener('click', () => navMenu.classList.remove('show-menu'))
})

/*===== SECTION ORDER =====*/
const mainContent = document.querySelector('main')

if (mainContent) {
    const orderedSectionIds = [
        'home',
        'about',
        'education',
        'publications',
        'conferences',
        'research',
        'teaching',
        'skills',
        'projects',
        'blogs',
        'awards',
        'contact'
    ]

    orderedSectionIds.forEach(id => {
        const section = document.getElementById(id)
        if (section) mainContent.appendChild(section)
    })
}

/*===== ACTIVE NAV LINK ON SCROLL =====*/
const sections = document.querySelectorAll('section[id]')

function updateActiveLink() {
    const scrollY = window.pageYOffset
    sections.forEach(section => {
        const top    = section.offsetTop - 90
        const height = section.offsetHeight
        const id     = section.getAttribute('id')
        const link   = document.querySelector(`.nav__link[href="#${id}"]`)
        if (!link) return
        if (scrollY >= top && scrollY < top + height) {
            link.classList.add('active-link')
        } else {
            link.classList.remove('active-link')
        }
    })
}
window.addEventListener('scroll', updateActiveLink)
window.addEventListener('load', updateActiveLink)

/*===== HEADER SHADOW ON SCROLL =====*/
function toggleHeaderBg() {
    const header = document.getElementById('header')
    if (window.scrollY >= 80) header.classList.add('scroll-header')
    else                       header.classList.remove('scroll-header')
}
window.addEventListener('scroll', toggleHeaderBg)
window.addEventListener('load', toggleHeaderBg)

/*===== PROJECT CARD EXPANSION =====*/
const projectCards = document.querySelectorAll('[data-project-card]')

function closeAllProjectCards() {
    projectCards.forEach(card => {
        const toggle = card.querySelector('.project__card-toggle')
        card.classList.remove('project__card--open')
        if (toggle) toggle.setAttribute('aria-expanded', 'false')
        setProjectCardHeight(card, false)
    })
}

function setProjectCardHeight(card, isOpen) {
    const detail = card.querySelector('.project__card-detail')
    if (!detail) return
    detail.style.maxHeight = isOpen ? `${detail.scrollHeight + 32}px` : '0'
}

projectCards.forEach(card => {
    const toggle = card.querySelector('.project__card-toggle')
    const isOpen = card.classList.contains('project__card--open')
    setProjectCardHeight(card, isOpen)

    if (!toggle) return

    toggle.addEventListener('click', event => {
        event.stopPropagation()
        const willOpen = !card.classList.contains('project__card--open')

        closeAllProjectCards()

        if (willOpen) {
            card.classList.add('project__card--open')
            toggle.setAttribute('aria-expanded', 'true')
            setProjectCardHeight(card, true)
        }
    })
})

document.addEventListener('click', event => {
    if (!event.target.closest('[data-project-card]')) {
        closeAllProjectCards()
    }
})

window.addEventListener('resize', () => {
    projectCards.forEach(card => {
        setProjectCardHeight(card, card.classList.contains('project__card--open'))
    })
})

/*===== BLOG POPUP VIEWER =====*/
const blogCards = document.querySelectorAll('[data-blog-target]')
const blogPanels = document.querySelectorAll('[data-blog-panel]')
const blogsViewer = document.getElementById('blogs-viewer')
const blogCloseButtons = document.querySelectorAll('[data-blog-close]')

function openBlogPopup(targetId) {
    if (!blogsViewer) return

    blogCards.forEach(item => {
        const isMatch = item.dataset.blogTarget === targetId
        item.classList.toggle('blog__card--active', isMatch)
        item.setAttribute('aria-selected', isMatch ? 'true' : 'false')
    })

    blogPanels.forEach(panel => {
        const isMatch = panel.id === targetId
        panel.hidden = !isMatch
        panel.classList.toggle('blog__feature--active', isMatch)
    })

    blogsViewer.classList.add('blogs__viewer--open')
    blogsViewer.setAttribute('aria-hidden', 'false')
    document.body.classList.add('modal-open')
}

function closeBlogPopup() {
    if (!blogsViewer) return
    blogsViewer.classList.remove('blogs__viewer--open')
    blogsViewer.setAttribute('aria-hidden', 'true')
    document.body.classList.remove('modal-open')
}

blogCards.forEach(card => {
    card.addEventListener('click', () => {
        openBlogPopup(card.dataset.blogTarget)
    })
})

blogCloseButtons.forEach(button => {
    button.addEventListener('click', closeBlogPopup)
})

if (blogsViewer) {
    blogsViewer.addEventListener('click', event => {
        if (event.target === blogsViewer) closeBlogPopup()
    })
}

window.addEventListener('keydown', event => {
    if (event.key === 'Escape' && blogsViewer?.classList.contains('blogs__viewer--open')) {
        closeBlogPopup()
    }
})

/*===== PUBLICATION ACCORDION =====*/
document.querySelectorAll('.pub__item:not(.pub__item--more)').forEach(item => {
    const abstract = item.querySelector('.pub__abstract')

    function toggle() {
        const isOpen = item.classList.toggle('pub--open')
        item.setAttribute('aria-expanded', isOpen)
        abstract.style.maxHeight = isOpen ? abstract.scrollHeight + 'px' : '0'
    }

    item.addEventListener('click', toggle)
    item.addEventListener('keydown', e => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle() }
    })
})

/*===== PUBLICATION SORTING =====*/
const pubList = document.querySelector('.pub__list')

if (pubList) {
    const regularPubItems = Array.from(pubList.querySelectorAll('.pub__item:not(.pub__item--more)'))
    const morePubItem = pubList.querySelector('.pub__item--more')

    regularPubItems
        .sort((a, b) => {
            const yearA = Number(a.querySelector('.pub__year')?.textContent.trim() || 0)
            const yearB = Number(b.querySelector('.pub__year')?.textContent.trim() || 0)
            return yearB - yearA
        })
        .forEach((item, index) => {
            const numberEl = item.querySelector('.pub__num')
            if (numberEl) numberEl.textContent = String(index + 1)
            pubList.appendChild(item)
        })

    if (morePubItem) pubList.appendChild(morePubItem)
}

/*===== PUBLICATION FILTERS =====*/
const pubFilters = document.querySelectorAll('.pub__filter')
const pubItems = document.querySelectorAll('.pub__item[data-topic]')

pubFilters.forEach(filter => {
    filter.addEventListener('click', () => {
        const topic = filter.dataset.filter

        pubFilters.forEach(btn => btn.classList.remove('pub__filter--active'))
        filter.classList.add('pub__filter--active')

        pubItems.forEach(item => {
            const shouldShow = topic === 'all' || item.dataset.topic === topic
            item.hidden = !shouldShow

            if (!shouldShow) {
                item.classList.remove('pub--open')
                item.setAttribute('aria-expanded', 'false')
                const abstract = item.querySelector('.pub__abstract')
                if (abstract) abstract.style.maxHeight = '0'
            }
        })
    })
})

/*===== SCROLL-TO-TOP BUTTON =====*/
function toggleScrollUp() {
    const btn = document.getElementById('scroll-up')
    if (window.scrollY >= 560) btn.classList.add('show-scroll')
    else                        btn.classList.remove('show-scroll')
}
window.addEventListener('scroll', toggleScrollUp)
window.addEventListener('load', toggleScrollUp)
