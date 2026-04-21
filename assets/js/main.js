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
        'posters',
        'research',
        'teaching',
        'experience',
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
    '.contact__info', '.contact__form',
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

/*===== EMAILJS CONTACT FORM =====*/
// ─────────────────────────────────────────────────────────────
// SETUP (one-time, ~3 minutes):
//  1. Go to https://emailjs.com  →  create a free account
//  2. Add Service: Email Services → Add New Service → Gmail
//     Copy the Service ID  (e.g. "service_abc123")
//  3. Add Template: Email Templates → Create New Template
//     Use these variables in the template body:
//       From: {{user_name}}  <{{user_email}}>
//       Subject: {{subject}}
//       Message: {{message}}
//     Set "To email" to kazi.mahmood@wayne.edu
//     Copy the Template ID  (e.g. "template_xyz789")
//  4. Account → General → Public Key  (e.g. "AbCdEfGhIj...")
//  5. Paste the three values below and save the file.
// ─────────────────────────────────────────────────────────────
const EMAILJS_SERVICE_ID  = 'service_ap8isfe'
const EMAILJS_TEMPLATE_ID = 'template_h2216lq'
const EMAILJS_PUBLIC_KEY  = '92Tdxm5T9uCiG0XYJ'

if (typeof emailjs !== 'undefined') {
    emailjs.init({ publicKey: EMAILJS_PUBLIC_KEY })

    const contactForm = document.getElementById('contact-form')
    const contactBtn  = document.getElementById('contact-btn')
    const formStatus  = document.getElementById('form-status')

    if (contactForm) {
        contactForm.addEventListener('submit', function (e) {
            e.preventDefault()

            if (!contactForm.checkValidity()) {
                contactForm.reportValidity()
                return
            }

            contactBtn.disabled    = true
            contactBtn.innerHTML   = 'Sending… <i class="uil uil-spinner-alt spin"></i>'
            formStatus.textContent = ''
            formStatus.className   = 'form__status'

            emailjs.sendForm(EMAILJS_SERVICE_ID, EMAILJS_TEMPLATE_ID, contactForm)
                .then(() => {
                    contactBtn.innerHTML = 'Sent! <i class="uil uil-check-circle"></i>'
                    formStatus.textContent = 'Message sent — I\'ll get back to you soon!'
                    formStatus.className   = 'form__status form__status--ok'
                    contactForm.reset()
                    setTimeout(() => {
                        contactBtn.disabled  = false
                        contactBtn.innerHTML = 'Send Message <i class="uil uil-message"></i>'
                    }, 4000)
                })
                .catch(() => {
                    contactBtn.disabled  = false
                    contactBtn.innerHTML = 'Send Message <i class="uil uil-message"></i>'
                    formStatus.textContent = 'Could not send — please email kazi.mahmood@wayne.edu directly.'
                    formStatus.className   = 'form__status form__status--err'
                })
        })
    }
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

    document.addEventListener('mousemove', e => { mx = e.clientX; my = e.clientY })
    document.addEventListener('mouseleave', () => { mx = -100; my = -100 })

    function loop() {
        rx += (mx - rx) * 0.13
        ry += (my - ry) * 0.13
        dot.style.left  = mx + 'px';  dot.style.top  = my + 'px'
        ring.style.left = rx + 'px';  ring.style.top = ry + 'px'
        requestAnimationFrame(loop)
    }
    loop()

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
        { id: 'skills',       label: 'Skills',       num: '04' },
        { id: 'research',     label: 'Research',     num: '05' },
        { id: 'projects',     label: 'Projects',     num: '06' },
        { id: 'publications', label: 'Publications', num: '07' },
        { id: 'conferences',  label: 'Conferences',  num: '08' },
        { id: 'posters',      label: 'Posters',      num: '09' },
        { id: 'teaching',     label: 'Teaching',     num: '10' },
        { id: 'experience',   label: 'Experience',   num: '11' },
        { id: 'blogs',        label: 'Blogs',        num: '12' },
        { id: 'awards',       label: 'Awards',       num: '13' },
        { id: 'contact',      label: 'Contact',      num: '14' },
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
