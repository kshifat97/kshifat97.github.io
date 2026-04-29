history.scrollRestoration = 'manual'
window.scrollTo(0, 0)

/*===== NAV MENU TOGGLE =====*/
const introLoader = document.getElementById('intro-loader')

if (introLoader) {
    let introFinished = false
    document.documentElement.classList.add('intro-is-running')

    const finishIntro = () => {
        if (introFinished) return
        introFinished = true

        const ktmGroup = introLoader.querySelector('.intro-loader__ktm-group')
        const mark     = introLoader.querySelector('.intro-loader__mark')

        // Fade bar, rings, grid immediately
        introLoader.querySelectorAll(
            '.intro-loader__bar-wrap, .intro-loader__field, .intro-loader__grid, .intro-loader__scan'
        ).forEach(el => { el.style.cssText = 'transition:opacity 0.2s ease;opacity:0' })

        // Make KTM letters solid gold so the zoom is visible
        if (mark) mark.style.cssText = 'color:rgba(240,192,64,1);animation:none'

        // Freeze each letter in its current visible state
        introLoader.querySelectorAll('.intro-loader__mark span').forEach(s => {
            s.style.cssText = 'animation:none;opacity:1;transform:translateY(0)'
        })

        if (ktmGroup) {
            // Set overflow visible so zoomed KTM isn't clipped
            introLoader.style.overflow = 'visible'
            ktmGroup.style.transformOrigin = 'center center'

            // Force reflow so transition picks up the initial state
            void ktmGroup.offsetWidth

            ktmGroup.style.transition = 'transform 3.5s cubic-bezier(0.2,0,0.8,1), opacity 1.2s ease 2.5s'
            ktmGroup.style.transform  = 'scale(22)'
            ktmGroup.style.opacity    = '0'
        }

        // Fade the dark background out after KTM has grown large
        introLoader.style.transition = 'background-color 1.4s ease 2.2s'
        introLoader.style.backgroundColor = 'transparent'

        document.documentElement.classList.remove('intro-is-running')
        document.documentElement.classList.add('intro-complete')
        window.setTimeout(() => introLoader.remove(), 4200)
    }

    const pctEl = document.getElementById('intro-loader-pct')

    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        if (pctEl) pctEl.textContent = '100%'
        window.setTimeout(finishIntro, 200)
    } else {
        if (pctEl) {
            const barDelay = 600
            const barDuration = 2200
            let startTs = null
            function tickPct(ts) {
                if (!startTs) startTs = ts
                const elapsed = ts - startTs
                if (elapsed < barDelay) { requestAnimationFrame(tickPct); return }
                const pct = Math.min(Math.round((elapsed - barDelay) / barDuration * 100), 100)
                pctEl.textContent = pct + '%'
                if (pct < 100) requestAnimationFrame(tickPct)
            }
            requestAnimationFrame(tickPct)
        }
        window.addEventListener('load', () => {
            // Bar finishes at 2800ms from nav start (delay 600 + duration 2200).
            // Wait until at least 3200ms so 100% is visible for ~400ms before exit.
            const minWait = Math.max(600, 3200 - Math.round(performance.now()))
            window.setTimeout(finishIntro, minWait)
        }, { once: true })
        window.setTimeout(finishIntro, 4800)
    }
}

const navMenu   = document.getElementById('nav-menu'),
      navToggle = document.getElementById('nav-toggle'),
      navClose  = document.getElementById('nav-close'),
      navMoreItem = document.querySelector('.nav__item--more'),
      navMoreToggle = document.querySelector('.nav__more-toggle')

function setNavMoreOpen(isOpen) {
    if (!navMoreItem || !navMoreToggle) return
    navMoreItem.classList.toggle('nav__item--open', isOpen)
    navMoreToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false')
}

function closeNavMore() {
    const hadFocus = navMoreItem?.contains(document.activeElement)
    setNavMoreOpen(false)
    if (hadFocus) document.activeElement.blur()
}

if (navToggle) {
    navToggle.addEventListener('click', () => navMenu.classList.add('show-menu'))
}
if (navClose) {
    navClose.addEventListener('click', () => {
        navMenu.classList.remove('show-menu')
        closeNavMore()
    })
}
if (navMoreToggle) {
    navMoreToggle.addEventListener('click', event => {
        event.stopPropagation()
        setNavMoreOpen(!navMoreItem?.classList.contains('nav__item--open'))
    })
}

document.querySelectorAll('.nav__link').forEach(link => {
    link.addEventListener('click', () => {
        navMenu.classList.remove('show-menu')
        closeNavMore()
    })
})

document.addEventListener('click', event => {
    if (navMoreItem && !navMoreItem.contains(event.target)) closeNavMore()
})

window.addEventListener('keydown', event => {
    if (event.key === 'Escape') closeNavMore()
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
        'posters',
        'research',
        'teaching',
        'experience',
        'skills',
        'projects',
        'blogs',
        'awards',
        'journeys',
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
    let hasActiveDropdownLink = false

    sections.forEach(section => {
        const top    = section.offsetTop - 90
        const height = section.offsetHeight
        const id     = section.getAttribute('id')
        const link   = document.querySelector(`.nav__link[href="#${id}"]`)
        if (!link) return
        const isActive = scrollY >= top && scrollY < top + height
        link.classList.toggle('active-link', isActive)
        if (isActive && link.closest('.nav__dropdown')) hasActiveDropdownLink = true
    })

    if (navMoreToggle) {
        navMoreToggle.classList.toggle('active-link', hasActiveDropdownLink)
    }
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

if (blogsViewer && blogsViewer.parentElement !== document.body) {
    document.body.appendChild(blogsViewer)
}

function openBlogPopup(targetId) {
    if (!blogsViewer) return

    blogCards.forEach(item => {
        const isMatch = item.dataset.blogTarget === targetId
        item.classList.toggle('blog__card--active', isMatch)
        item.setAttribute('aria-selected', isMatch ? 'true' : 'false')
    })

    blogPanels.forEach(panel => {
        const isMatch = panel.id === targetId
        panel.classList.remove('blog__feature--active')
        panel.hidden = !isMatch
    })

    blogsViewer.classList.add('blogs__viewer--open')
    blogsViewer.setAttribute('aria-hidden', 'false')
    document.body.classList.add('modal-open')

    const activePanel = document.getElementById(targetId)
    if (activePanel) {
        activePanel.scrollTop = 0
        void activePanel.offsetWidth
        window.requestAnimationFrame(() => {
            activePanel.classList.add('blog__feature--active')
        })
    }
}

function closeBlogPopup() {
    if (!blogsViewer) return
    blogsViewer.classList.remove('blogs__viewer--open')
    blogsViewer.setAttribute('aria-hidden', 'true')
    document.body.classList.remove('modal-open')
    blogPanels.forEach(panel => {
        panel.classList.remove('blog__feature--active')
    })
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

/*===== CUSTOM VIDEO PLAYBACK RATES =====*/
document.querySelectorAll('video[data-playback-rate]').forEach(video => {
    const rate = Number(video.dataset.playbackRate)
    if (!Number.isFinite(rate) || rate <= 0) return

    const applyRate = () => {
        video.playbackRate = rate
        video.defaultPlaybackRate = rate
    }

    if (video.readyState >= 1) applyRate()
    video.addEventListener('loadedmetadata', applyRate)
    video.addEventListener('play', applyRate)
})

/*===== PUBLICATION ACCORDION =====*/
const pubAccordionItems = document.querySelectorAll('.pub__item:not(.pub__item--more)')

function closePubItem(item) {
    item.classList.remove('pub--open')
    item.setAttribute('aria-expanded', 'false')
    const abstract = item.querySelector('.pub__abstract')
    if (abstract) abstract.style.maxHeight = '0'
}

function openPubItem(item) {
    item.classList.add('pub--open')
    item.setAttribute('aria-expanded', 'true')
    const abstract = item.querySelector('.pub__abstract')
    if (abstract) abstract.style.maxHeight = abstract.scrollHeight + 'px'
}

pubAccordionItems.forEach(item => {
    function toggle() {
        const isOpen = item.classList.contains('pub--open')
        pubAccordionItems.forEach(other => { if (other !== item) closePubItem(other) })
        isOpen ? closePubItem(item) : openPubItem(item)
    }

    item.addEventListener('click', toggle)
    item.addEventListener('keydown', e => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggle() }
    })
})

document.addEventListener('click', e => {
    if (!e.target.closest('.pub__item')) {
        pubAccordionItems.forEach(closePubItem)
    }
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


/*===== SECTION TITLE UNDERLINE GROW =====*/
const titleRevealObs = new IntersectionObserver(entries => {
    entries.forEach(e => {
        if (e.isIntersecting) { e.target.classList.add('title-revealed'); titleRevealObs.unobserve(e.target) }
    })
}, { threshold: 0.6 })
document.querySelectorAll('.section__title').forEach(t => {
    t.setAttribute('data-title-anim', '')
    titleRevealObs.observe(t)
})

/*===== SCROLL REVEAL (generic blocks) =====*/
const blockRevealObs = new IntersectionObserver(entries => {
    entries.forEach(e => {
        if (e.isIntersecting) { e.target.classList.add('anim-in'); blockRevealObs.unobserve(e.target) }
    })
}, { threshold: 0.08 })
;[
    '.about__text', '.about__profile', '.about__stats',
    '.pub__hint', '.pub__list', '.pub__scholar-btn',
    '.skills__group',
    '.contact__info', '.contact__card',
    '.poster-gallery', '.conf__list', '.projects__cards',
    '.section__subtitle',
].forEach(sel => {
    document.querySelectorAll(sel).forEach(el => {
        el.classList.add('anim-ready')
        blockRevealObs.observe(el)
    })
})

/*===== TIMELINE STAGGER =====*/
document.querySelectorAll('.timeline').forEach(tl => {
    tl.classList.add('timeline-anim')
    const items = tl.querySelectorAll('.timeline__item')
    const obs = new IntersectionObserver(([e]) => {
        if (e.isIntersecting) {
            items.forEach((item, i) => setTimeout(() => item.classList.add('anim-in'), i * 120))
            obs.unobserve(tl)
        }
    }, { threshold: 0.05 })
    obs.observe(tl)
})

/*===== TAG STAGGER =====*/
document.querySelectorAll('.tags').forEach(group => {
    group.classList.add('tags-anim')
    const tags = group.querySelectorAll('.tag')
    const obs = new IntersectionObserver(([e]) => {
        if (e.isIntersecting) {
            tags.forEach((t, i) => { t.style.transitionDelay = `${i * 0.05}s` })
            group.classList.add('tags-in')
            obs.unobserve(group)
        }
    }, { threshold: 0.15 })
    obs.observe(group)
})

/*===== CONFERENCE ITEMS STAGGER =====*/
document.querySelectorAll('.conf__list').forEach(list => {
    list.classList.add('conf-anim')
    const items = list.querySelectorAll('.conf__item')
    const obs = new IntersectionObserver(([e]) => {
        if (e.isIntersecting) {
            items.forEach((item, i) => setTimeout(() => item.classList.add('anim-in'), i * 65))
            obs.unobserve(list)
        }
    }, { threshold: 0.04 })
    obs.observe(list)
})

/*===== HERO PARALLAX =====*/
const heroPoster  = document.querySelector('.hero__poster')
const heroBgIcons = document.querySelector('.hero__science')
function heroParallax() {
    const y = window.scrollY
    if (y > window.innerHeight * 1.1) return
    if (heroPoster)  heroPoster.style.transform  = `translateY(${y * 0.18}px)`
    if (heroBgIcons) heroBgIcons.style.transform = `translateY(${y * 0.42}px)`
}
window.addEventListener('scroll', heroParallax, { passive: true })


/*===== DOT NAV =====*/
const dotNavEl   = document.getElementById('dot-nav')
const dotNavDots = document.querySelectorAll('.dot-nav__dot')
function updateDotNav() {
    const scrollY   = window.scrollY
    const aboutEl   = document.getElementById('about')
    const threshold = aboutEl ? aboutEl.offsetTop - 120 : window.innerHeight * 0.6
    dotNavEl && dotNavEl.classList.toggle('dot-nav--hidden', scrollY < threshold)
    let activeId = null
    document.querySelectorAll('section[id]').forEach(section => {
        if (scrollY >= section.offsetTop - 120) activeId = section.id
    })
    dotNavDots.forEach(dot => {
        dot.classList.toggle('dot-active', dot.getAttribute('href') === '#' + activeId)
    })
}
window.addEventListener('scroll', updateDotNav, { passive: true })
window.addEventListener('load', updateDotNav)

/*===== 3D CARD TILT =====*/
function attachTiltEffect(cards) {
    cards.forEach(card => {
        card.addEventListener('mousemove', e => {
            const r = card.getBoundingClientRect()
            const x = (e.clientY - r.top  - r.height / 2) / (r.height / 2)
            const y = (e.clientX - r.left - r.width  / 2) / (r.width  / 2)
            card.style.transition = 'transform 0.08s ease, box-shadow 0.08s ease'
            card.style.transform  = `perspective(900px) rotateX(${-x * 4}deg) rotateY(${y * 4}deg) translateY(-4px) scale(1.01)`
        })
        card.addEventListener('mouseleave', () => {
            card.style.transition = 'transform 0.55s cubic-bezier(0.23, 1, 0.32, 1), box-shadow 0.55s ease'
            card.style.transform  = ''
        })
    })
}

attachTiltEffect(document.querySelectorAll('.timeline__card'))
attachTiltEffect(document.querySelectorAll('.awards__col'))

/*===== TIMELINE FILL LINE =====*/
document.querySelectorAll('.timeline').forEach(tl => {
    const fill = document.createElement('div')
    fill.className = 'timeline__fill'
    tl.appendChild(fill)
})
function updateTimelineFills() {
    document.querySelectorAll('.timeline__fill').forEach(fill => {
        const tl   = fill.closest('.timeline')
        const rect = tl.getBoundingClientRect()
        const p    = Math.max(0, Math.min(1, (window.innerHeight * 0.65 - rect.top) / rect.height))
        fill.style.height = (p * 100) + '%'
    })
}
window.addEventListener('scroll', updateTimelineFills, { passive: true })
window.addEventListener('load',   updateTimelineFills)

/*===== AWARDS DIRECTIONAL ENTRANCE =====*/
const awardsCols = document.querySelectorAll('.awards__col')
if (awardsCols.length) {
    awardsCols.forEach((col, i) => {
        col.classList.add('anim-ready')
        col.style.transitionDelay = `${i * 0.13}s`
    })
    const awardsObs = new IntersectionObserver(entries => {
        entries.forEach(e => {
            if (e.isIntersecting) { e.target.classList.add('anim-in'); awardsObs.unobserve(e.target) }
        })
    }, { threshold: 0.15 })
    awardsCols.forEach(col => awardsObs.observe(col))
}

/*===== MAGNETIC BUTTONS =====*/
document.querySelectorAll('.btn--primary, .btn--outline, .btn--outline-navy').forEach(btn => {
    btn.addEventListener('mousemove', e => {
        const r = btn.getBoundingClientRect()
        const x = (e.clientX - r.left - r.width  / 2) * 0.22
        const y = (e.clientY - r.top  - r.height / 2) * 0.22
        btn.style.transition = 'transform 0.12s ease'
        btn.style.transform  = `translate(${x}px, ${y}px) translateY(-2px)`
    })
    btn.addEventListener('mouseleave', () => {
        btn.style.transition = 'transform 0.45s cubic-bezier(0.23, 1, 0.32, 1)'
        btn.style.transform  = ''
    })
})

/*===== POSTER LIGHTBOX =====*/
function openPosterModal(src) {
    const modal = document.getElementById('posterModal')
    const img   = document.getElementById('posterModalImg')
    img.src = src
    modal.classList.add('active')
    requestAnimationFrame(() => requestAnimationFrame(() => modal.classList.add('anim-in')))
    document.body.classList.add('modal-open')
}

function closePosterModal() {
    const modal = document.getElementById('posterModal')
    modal.classList.remove('anim-in')
    document.body.classList.remove('modal-open')
    modal.addEventListener('transitionend', () => modal.classList.remove('active'), { once: true })
}

document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closePosterModal()
})

/*===== HERO PARTICLES =====*/
;(function () {
    const canvas = document.getElementById('hero-canvas')
    const hero   = canvas && canvas.closest('.hero')
    if (!canvas || !hero) return
    const ctx = canvas.getContext('2d')
    let W, H, particles = []
    let mx = -999, my = -999

    function resize() {
        W = canvas.width  = canvas.offsetWidth
        H = canvas.height = canvas.offsetHeight
    }
    resize()
    window.addEventListener('resize', resize)

    hero.addEventListener('mousemove', e => {
        const r = hero.getBoundingClientRect()
        mx = e.clientX - r.left
        my = e.clientY - r.top
    })
    hero.addEventListener('mouseleave', () => { mx = -999; my = -999 })

    function rand(a, b) { return a + Math.random() * (b - a) }
    for (let i = 0; i < 55; i++) {
        particles.push({
            x: rand(0, 1), y: rand(0, 1),
            vx: rand(-0.06, 0.06), vy: rand(-0.06, 0.06),
            r: rand(1, 2.5),
            baseA: rand(0.15, 0.45),
            phase: rand(0, Math.PI * 2),
            twinkleSpeed: rand(0.0008, 0.0018)
        })
    }

    function draw() {
        const now = Date.now()
        ctx.clearRect(0, 0, W, H)
        const pts = particles.map(p => {
            p.x += p.vx / W; p.y += p.vy / H
            if (p.x < 0) p.x = 1; if (p.x > 1) p.x = 0
            if (p.y < 0) p.y = 1; if (p.y > 1) p.y = 0
            const a = p.baseA * (0.5 + 0.5 * Math.sin(now * p.twinkleSpeed + p.phase))
            return { px: p.x * W, py: p.y * H, a, r: p.r }
        })

        // particle-to-particle connections
        for (let i = 0; i < pts.length; i++) {
            for (let j = i + 1; j < pts.length; j++) {
                const dx = pts[i].px - pts[j].px, dy = pts[i].py - pts[j].py
                const d = Math.sqrt(dx*dx + dy*dy)
                if (d < 110) {
                    ctx.beginPath()
                    ctx.moveTo(pts[i].px, pts[i].py)
                    ctx.lineTo(pts[j].px, pts[j].py)
                    ctx.strokeStyle = `rgba(240,192,64,${0.1 * (1 - d/110)})`
                    ctx.lineWidth = 0.6
                    ctx.stroke()
                }
            }
        }

        // cursor-to-particle connections
        pts.forEach(p => {
            const dx = p.px - mx, dy = p.py - my
            const d = Math.sqrt(dx*dx + dy*dy)
            if (d < 140) {
                ctx.beginPath()
                ctx.moveTo(p.px, p.py)
                ctx.lineTo(mx, my)
                ctx.strokeStyle = `rgba(240,192,64,${0.35 * (1 - d/140)})`
                ctx.lineWidth = 1
                ctx.stroke()
            }
        })

        // draw dots
        pts.forEach(p => {
            ctx.beginPath()
            ctx.arc(p.px, p.py, p.r, 0, Math.PI * 2)
            ctx.fillStyle = `rgba(240,192,64,${p.a})`
            ctx.fill()
        })
        requestAnimationFrame(draw)
    }
    draw()
})()

/*===== HERO MOUSE-FOLLOW GLOW =====*/
;(function () {
    const hero = document.querySelector('.hero')
    const glow = document.querySelector('.hero__mouse-glow')
    if (!hero || !glow) return
    hero.addEventListener('mousemove', e => {
        const rect = hero.getBoundingClientRect()
        glow.style.left = (e.clientX - rect.left) + 'px'
        glow.style.top  = (e.clientY - rect.top)  + 'px'
        hero.classList.add('hero--mouse-active')
    })
    hero.addEventListener('mouseleave', () => hero.classList.remove('hero--mouse-active'))
})()

/*===== TYPEWRITER =====*/
;(function () {
    const el = document.getElementById('typewriter-text')
    if (!el) return
    const roles = [
        'PhD in Mechanical Engineering',
        'Topological Metamaterials',
        'Nonlinear Dynamics',
        'Quantum Analogous Computing'
    ]
    let ri = 0, ci = 0, del = false
    function tick() {
        const word = roles[ri]
        el.textContent = del ? word.slice(0, --ci) : word.slice(0, ++ci)
        if (!del && ci === word.length) { del = true; setTimeout(tick, 1600); return }
        if ( del && ci === 0)           { del = false; ri = (ri + 1) % roles.length }
        setTimeout(tick, del ? 45 : 75)
    }
    tick()
})()

/*===== ANIMATED COUNTERS =====*/
function animateCounter(el, target) {
    let cur = 0
    const step = Math.max(1, Math.ceil(target / 50))
    clearInterval(el._countTimer)
    el._countTimer = setInterval(() => {
        cur = Math.min(cur + step, target)
        el.textContent = cur
        if (cur >= target) clearInterval(el._countTimer)
    }, 30)
}

;(function () {
    const pubEl  = document.getElementById('stat-publications')
    const confEl = document.getElementById('stat-conferences')
    if (pubEl)  pubEl.dataset.count  = document.querySelectorAll('.pub__item:not(.pub__item--more)').length
    if (confEl) confEl.dataset.count = document.querySelectorAll('.conf__item').length

    const statsBox = document.querySelector('.about__stats')
    if (!statsBox) return
    let fired = false
    const obs = new IntersectionObserver(entries => {
        if (!entries[0].isIntersecting || fired) return
        fired = true
        ;[pubEl, confEl].forEach(el => { if (el) animateCounter(el, +el.dataset.count) })
        const citEl = document.getElementById('stat-citations')
        if (citEl && citEl.dataset.count) animateCounter(citEl, +citEl.dataset.count)
        obs.disconnect()
    }, { threshold: 0.4 })
    obs.observe(statsBox)
})()

/*===== BUTTON RIPPLE =====*/
document.querySelectorAll('.btn').forEach(btn => {
    btn.addEventListener('click', function (e) {
        const r = document.createElement('span')
        r.className = 'btn__ripple'
        r.style.left = e.offsetX + 'px'
        r.style.top  = e.offsetY + 'px'
        this.appendChild(r)
        r.addEventListener('animationend', () => r.remove())
    })
})

/*===== TIMELINE DOT PULSE =====*/
document.querySelectorAll('.timeline').forEach(tl => {
    const firstDot = tl.querySelector('.timeline__dot')
    if (firstDot) firstDot.classList.add('timeline__dot--pulse')
})

/*===== CUSTOM CURSOR =====*/
;(function () {
    const dot  = document.getElementById('cursor-dot')
    const ring = document.getElementById('cursor-ring')
    if (!dot || !ring) return
    let mx = -100, my = -100, rx = -100, ry = -100
    let rafId = 0

    function render() {
        rafId = 0
        rx += (mx - rx) * 0.13
        ry += (my - ry) * 0.13
        dot.style.transform = `translate3d(${mx}px, ${my}px, 0) translate(-50%, -50%)`
        ring.style.transform = `translate3d(${rx}px, ${ry}px, 0) translate(-50%, -50%)`

        if (Math.abs(mx - rx) > 0.2 || Math.abs(my - ry) > 0.2) {
            rafId = requestAnimationFrame(render)
        }
    }

    function requestRender() {
        if (!rafId) rafId = requestAnimationFrame(render)
    }

    document.addEventListener('mousemove', e => {
        mx = e.clientX
        my = e.clientY
        requestRender()
    }, { passive: true })

    document.addEventListener('mouseleave', () => {
        mx = -100
        my = -100
        requestRender()
    })

    const targets = 'a, button, [role="button"], input, textarea, select, label, .pub__item, .project__card-toggle, .poster-gallery__item'
    document.querySelectorAll(targets).forEach(el => {
        el.addEventListener('mouseenter', () => { dot.classList.add('cursor--hover');  ring.classList.add('cursor--hover') })
        el.addEventListener('mouseleave', () => { dot.classList.remove('cursor--hover'); ring.classList.remove('cursor--hover') })
    })
})()

/*===== SECTION TITLE UNDERLINE GROW =====*/
;(function () {
    const titles = document.querySelectorAll('.section__title')
    if (!titles.length) return
    const obs = new IntersectionObserver(entries => {
        entries.forEach(e => {
            if (e.isIntersecting) {
                e.target.classList.add('title--in')
                obs.unobserve(e.target)
            }
        })
    }, { threshold: 0.6 })
    titles.forEach(t => obs.observe(t))
})()

/*===== SECTION TRACKER =====*/
;(function () {
    const numEl  = document.getElementById('tracker-num')
    const nameEl = document.getElementById('tracker-name')
    const tracker = document.getElementById('section-tracker')
    if (!tracker || !numEl || !nameEl) return

    const sections = [
        { id: 'home',         label: 'Home',         num: '01' },
        { id: 'about',        label: 'About',        num: '02' },
        { id: 'education',    label: 'Education',    num: '03' },
        { id: 'publications', label: 'Publications', num: '04' },
        { id: 'conferences',  label: 'Conferences',  num: '05' },
        { id: 'posters',      label: 'Posters',      num: '06' },
        { id: 'research',     label: 'Research',     num: '07' },
        { id: 'teaching',     label: 'Teaching',     num: '08' },
        { id: 'experience',   label: 'Experience',   num: '09' },
        { id: 'skills',       label: 'Skills',       num: '10' },
        { id: 'projects',     label: 'Projects',     num: '11' },
        { id: 'blogs',        label: 'Blogs',        num: '12' },
        { id: 'awards',       label: 'Awards',       num: '13' },
        { id: 'journeys',     label: 'Journeys',     num: '14' },
        { id: 'contact',      label: 'Contact',      num: '15' },
    ]

    function update(id) {
        if (id === 'home') { tracker.classList.remove('tracker--visible'); return }
        const s = sections.find(x => x.id === id)
        if (!s) return
        numEl.textContent  = s.num
        nameEl.textContent = s.label
        tracker.classList.add('tracker--visible')
    }

    const obs = new IntersectionObserver(entries => {
        entries.forEach(e => { if (e.isIntersecting) update(e.target.id) })
    }, { threshold: 0.3 })

    sections.forEach(s => {
        const el = document.getElementById(s.id)
        if (el) obs.observe(el)
    })
})()

/*===== SCHOLAR CITATION COUNT =====*/
;(async function () {
    try {
        const res = await fetch(
            'https://api.semanticscholar.org/graph/v1/author/2198945293?fields=citationCount,hIndex',
            { headers: { 'Accept': 'application/json' } }
        )
        if (!res.ok) return
        const author = await res.json()
        const citEl     = document.getElementById('scholar-citations')
        const hiEl      = document.getElementById('scholar-hindex')
        const statCitEl = document.getElementById('stat-citations')
        if (citEl && author.citationCount != null) citEl.textContent = author.citationCount
        if (hiEl  && author.hIndex        != null) hiEl.textContent  = author.hIndex
        if (statCitEl && author.citationCount != null) {
            statCitEl.dataset.count = author.citationCount
            animateCounter(statCitEl, author.citationCount)
        }
    } catch (_) {}
})()

/*===== JOURNEY ALBUM VIEWER =====*/
;(function () {
    const albums = Array.isArray(window.JOURNEY_ALBUMS)
        ? window.JOURNEY_ALBUMS.filter(album => Array.isArray(album.photos) && album.photos.length)
        : []
    const placesContainer = document.querySelector('.journeys__places')
    const journeysViewer = document.getElementById('journeys-viewer')
    let journeyPlaces = []
    let journeyPanels = []
    let lastJourneyTrigger = null

    if (!placesContainer || !journeysViewer || !albums.length) return

    function createEl(tag, className, text) {
        const el = document.createElement(tag)
        if (className) el.className = className
        if (text != null) el.textContent = text
        return el
    }

    function photoCountLabel(count) {
        return `${count} ${count === 1 ? 'Photo' : 'Photos'}`
    }

    function buildPlaceCard(album, index) {
        const button = document.createElement('button')
        const targetId = `journey-${album.id}`
        button.className = `journey__place${index === 0 ? ' journey__place--large' : ''}`
        button.type = 'button'
        button.dataset.journeyTarget = targetId
        button.setAttribute('aria-haspopup', 'dialog')
        button.setAttribute('aria-controls', targetId)
        button.setAttribute('aria-expanded', 'false')

        const media = createEl('span', 'journey__place-media')
        const firstImg = document.createElement('img')
        firstImg.className = 'journey__place-img journey__place-img--active'
        firstImg.src = album.cover || album.photos[0]
        firstImg.alt = `${album.title} album preview`
        firstImg.loading = 'lazy'
        firstImg.decoding = 'async'
        media.appendChild(firstImg)

        const content = createEl('span', 'journey__place-content')
        content.append(
            createEl('span', 'journey__place-kicker', photoCountLabel(album.photos.length)),
            createEl('span', 'journey__place-title', album.title),
            createEl('span', 'journey__place-copy', 'A rotating window into this album.')
        )

        button.append(media, content)
        button.addEventListener('click', () => openJourneyAlbum(targetId))
        return button
    }

    function buildAlbumPanel(album) {
        const article = createEl('article', 'journey__album')
        const titleId = `journey-${album.id}-title`
        article.id = `journey-${album.id}`
        article.dataset.journeyPanel = ''
        article.role = 'dialog'
        article.setAttribute('aria-modal', 'true')
        article.setAttribute('aria-labelledby', titleId)
        article.hidden = true

        const header = createEl('header', 'journey__album-header')
        const titleWrap = document.createElement('div')
        titleWrap.append(
            createEl('span', 'journey__album-kicker', 'Journey Album'),
            createEl('h3', 'journey__album-title', album.title),
            createEl('p', 'journey__album-copy', photoCountLabel(album.photos.length))
        )
        titleWrap.querySelector('.journey__album-title').id = titleId

        const closeButton = createEl('button', 'journey__close')
        closeButton.type = 'button'
        closeButton.dataset.journeyClose = ''
        closeButton.setAttribute('aria-label', `Close ${album.title} album`)
        closeButton.innerHTML = '<i class="uil uil-times"></i>'
        closeButton.addEventListener('click', closeJourneyAlbum)
        header.append(titleWrap, closeButton)

        const controls = createEl('div', `journey__slider-controls${album.photos.length < 2 ? ' journey__slider-controls--single' : ''}`)
        controls.innerHTML = `
            <button class="journey__slider-button" type="button" data-journey-prev aria-label="Previous photo">
                <i class="uil uil-angle-left-b"></i>
            </button>
            <button class="journey__slider-button" type="button" data-journey-next aria-label="Next photo">
                <i class="uil uil-angle-right-b"></i>
            </button>
        `
        controls.querySelector('[data-journey-prev]')?.addEventListener('click', () => moveJourneySlide(article, -1))
        controls.querySelector('[data-journey-next]')?.addEventListener('click', () => moveJourneySlide(article, 1))

        const photos = createEl('div', 'journey__photos')
        photos.setAttribute('aria-label', `${album.title} photos`)
        album.photos.forEach((src, photoIndex) => {
            const figure = createEl('figure', 'journey__photo')
            const img = document.createElement('img')
            img.dataset.src = src
            img.alt = `${album.title} journey photo ${photoIndex + 1}`
            img.loading = 'lazy'
            img.decoding = 'async'
            figure.appendChild(img)
            figure.addEventListener('click', event => {
                event.stopPropagation()
                if (figure.classList.contains('journey__photo--prev')) {
                    moveJourneySlide(article, -1)
                } else {
                    moveJourneySlide(article, 1)
                }
            })
            photos.appendChild(figure)
        })

        article.append(header, controls, photos)
        return article
    }

    function getJourneyPhotos(panel) {
        return Array.from(panel?.querySelectorAll('.journey__photo') || [])
    }

    function loadJourneyPhoto(photo) {
        const img = photo?.querySelector('img[data-src]')
        if (img && !img.getAttribute('src')) {
            img.src = img.dataset.src
        }
    }

    function setJourneySlide(panel, index) {
        const photos = getJourneyPhotos(panel)
        if (!photos.length) return

        const count = photos.length
        const activeIndex = ((index % count) + count) % count
        const prevIndex = (activeIndex - 1 + count) % count
        const nextIndex = (activeIndex + 1) % count
        panel.dataset.activeSlide = String(activeIndex)

        photos.forEach((photo, photoIndex) => {
            if (
                photoIndex === activeIndex ||
                photoIndex === prevIndex ||
                photoIndex === nextIndex
            ) {
                loadJourneyPhoto(photo)
            }

            photo.classList.remove(
                'journey__photo--current',
                'journey__photo--prev',
                'journey__photo--next',
                'journey__photo--far'
            )

            if (photoIndex === activeIndex) {
                photo.classList.add('journey__photo--current')
            } else if (count > 2 && photoIndex === prevIndex) {
                photo.classList.add('journey__photo--prev')
            } else if (count > 1 && photoIndex === nextIndex) {
                photo.classList.add('journey__photo--next')
            } else {
                photo.classList.add('journey__photo--far')
            }
        })
    }

    function moveJourneySlide(panel, direction) {
        const activeIndex = Number(panel?.dataset.activeSlide || 0)
        setJourneySlide(panel, activeIndex + direction)
    }

    function openJourneyAlbum(targetId) {
        lastJourneyTrigger = document.activeElement

        journeyPlaces.forEach(place => {
            const isMatch = place.dataset.journeyTarget === targetId
            place.classList.toggle('journey__place--active', isMatch)
            place.setAttribute('aria-expanded', isMatch ? 'true' : 'false')
        })

        journeyPanels.forEach(panel => {
            const isMatch = panel.id === targetId
            panel.classList.remove('journey__album--active')
            panel.hidden = !isMatch
        })

        journeysViewer.classList.add('journeys__viewer--open')
        journeysViewer.setAttribute('aria-hidden', 'false')
        document.body.classList.add('modal-open')

        const activePanel = document.getElementById(targetId)
        if (activePanel) {
            setJourneySlide(activePanel, 0)
            void activePanel.offsetWidth
            window.requestAnimationFrame(() => {
                activePanel.classList.add('journey__album--active')
                activePanel.querySelector('[data-journey-close]')?.focus()
            })
        }
    }

    function closeJourneyAlbum() {
        journeysViewer.classList.remove('journeys__viewer--open')
        journeysViewer.setAttribute('aria-hidden', 'true')
        document.body.classList.remove('modal-open')
        journeyPlaces.forEach(place => {
            place.classList.remove('journey__place--active')
            place.setAttribute('aria-expanded', 'false')
        })
        journeyPanels.forEach(panel => panel.classList.remove('journey__album--active'))
        lastJourneyTrigger?.focus?.()
        lastJourneyTrigger = null
    }

    placesContainer.replaceChildren(...albums.map(buildPlaceCard))
    journeysViewer.replaceChildren(...albums.map(buildAlbumPanel))
    journeyPlaces = Array.from(placesContainer.querySelectorAll('[data-journey-target]'))
    journeyPanels = Array.from(journeysViewer.querySelectorAll('[data-journey-panel]'))

    if (journeysViewer.parentElement !== document.body) {
        document.body.appendChild(journeysViewer)
    }

    journeysViewer.addEventListener('click', event => {
        if (event.target === journeysViewer) closeJourneyAlbum()
    })

    window.addEventListener('keydown', event => {
        if (!journeysViewer.classList.contains('journeys__viewer--open')) return

        if (event.key === 'Escape') {
            closeJourneyAlbum()
            return
        }

        if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
            const activePanel = document.querySelector('.journey__album--active')
            if (!activePanel) return
            event.preventDefault()
            moveJourneySlide(activePanel, event.key === 'ArrowRight' ? 1 : -1)
        }
    })
})()

/*===== PHOTO FAN =====*/
;(function () {
    const fan = document.getElementById('photoFan')
    if (!fan) return
    fan.addEventListener('click', e => {
        e.stopPropagation()
        fan.classList.toggle('is-open')
    })
    document.addEventListener('click', () => fan.classList.remove('is-open'))
})()
