import { lazy, Suspense, useEffect, useRef, useState } from 'react'
import { Brand, Icon } from './components/Icon'
import Core from './components/Core'

const Demo = lazy(() => import('./components/Demo'))
const repository = 'https://github.com/Team-DROS/TroubleShoot'

const workflow = [
  {
    label: 'Understand the problem.',
    description:
      'Start with what feels wrong. A focused observation gives the diagnosis something real to work with.',
    icon: 'eye' as const,
    tag: '01 / OBSERVE',
    title: 'A little context. A clearer picture.',
    message: 'My printer is connected, but nothing is printing.',
    lines: [
      ['Print Spooler', 'Stopped'],
      ['Connection', 'Available'],
      ['Scope', 'Selected service'],
    ],
    status: 'Potential cause identified',
    note: 'A sample observation, not a scan of your device.',
  },
  {
    label: 'You make the call.',
    description:
      'See the exact action, its scope, and its recovery path. Nothing changes until you decide.',
    icon: 'shield' as const,
    tag: '02 / APPROVE',
    title: 'One action. Your permission.',
    message: 'The Print Spooler is stopped. Starting it may restore the printing service.',
    lines: [
      ['Proposed action', 'Start service'],
      ['Target', 'Print Spooler'],
      ['Recovery', 'Restore pre-state'],
    ],
    status: 'Waiting for your approval',
    note: 'Approval belongs to one specific action.',
  },
  {
    label: 'Check what changed.',
    description:
      'Fresh evidence closes the loop. See what improved, what still needs attention, and how to recover.',
    icon: 'check' as const,
    tag: '03 / VERIFY',
    title: 'Evidence over “probably fixed.”',
    message: 'The sample service is now running. A physical test print is still needed.',
    lines: [
      ['Before', 'Stopped'],
      ['After', 'Running'],
      ['Outcome', 'Partially resolved'],
    ],
    status: 'Service recovery verified',
    note: 'Service recovery does not prove a printed page.',
  },
]

const faqs = [
  [
    'Can I use this to repair my computer today?',
    'This is an interactive frontend preview. You can explore the workflow with sample printer, audio, and network scenarios. The local model, Windows executor, and API are still being developed; this website cannot inspect or change your device.',
  ],
  [
    'What stays on my computer?',
    'The planned default uses local Gemma through Ollama. An optional hosted mode will require explicit consent before sending text, with a separate choice for images. This preview runs entirely in your browser and does not send your scenario input to a server.',
  ],
  [
    'What will TroubleShoot be allowed to change?',
    'Only explicitly registered operations with validated arguments. Repair actions are designed to require specific approval, a fresh observation, and a recovery path. Arbitrary model-generated shell commands are outside the product’s scope.',
  ],
  [
    'Which platforms are supported?',
    'The application is being designed for Windows. This responsive website and its sample walkthrough work in modern desktop and mobile browsers. Native troubleshooting will require the local Windows application once it is available.',
  ],
]

function SectionLabel({ number, children }: { number: string; children: React.ReactNode }) {
  return (
    <div className="section-label">
      <span>{number}</span>
      <span>{children}</span>
    </div>
  )
}

export default function App() {
  const [menuOpen, setMenuOpen] = useState(false)
  const [demoOpen, setDemoOpen] = useState(false)
  const [step, setStep] = useState(0)
  const [activeSection, setActiveSection] = useState('')
  const demoTrigger = useRef<HTMLElement | null>(null)
  const selected = workflow[step]

  function openDemo() {
    demoTrigger.current = document.activeElement as HTMLElement
    setMenuOpen(false)
    setDemoOpen(true)
  }
  function closeDemo() {
    setDemoOpen(false)
    requestAnimationFrame(() => demoTrigger.current?.focus())
  }

  useEffect(() => {
    const sections = document.querySelectorAll<HTMLElement>('section[id]')
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) setActiveSection(entry.target.id)
        })
      },
      { rootMargin: '-15% 0px -65% 0px' },
    )
    sections.forEach((section) => observer.observe(section))
    return () => observer.disconnect()
  }, [])

  useEffect(() => {
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) return
    const elements = document.querySelectorAll<HTMLElement>('[data-reveal]')
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('revealed')
            observer.unobserve(entry.target)
          }
        })
      },
      { threshold: 0.07 },
    )
    elements.forEach((element) => {
      element.classList.add('will-reveal')
      observer.observe(element)
    })
    return () => observer.disconnect()
  }, [])

  return (
    <>
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      <header className="site-header">
        <div className="header-inner">
          <a href="#" className="brand-link" aria-label="TroubleShoot home">
            <Brand />
          </a>
          <nav
            className={menuOpen ? 'main-nav is-open' : 'main-nav'}
            id="main-navigation"
            aria-label="Main navigation"
          >
            {[
              ['workflow', 'How it works'],
              ['principles', 'Built different'],
              ['questions', 'Questions'],
            ].map(([id, label]) => (
              <a
                key={id}
                href={`#${id}`}
                className={activeSection === id ? 'active' : ''}
                onClick={() => setMenuOpen(false)}
              >
                {label}
              </a>
            ))}
          </nav>
          <div className="header-actions">
            <button className="button button-outline header-cta" onClick={openDemo}>
              Explore the demo <Icon name="up-right" size={16} />
            </button>
            <button
              className="icon-button menu-toggle"
              onClick={() => setMenuOpen(!menuOpen)}
              aria-label={menuOpen ? 'Close navigation' : 'Open navigation'}
              aria-expanded={menuOpen}
              aria-controls="main-navigation"
            >
              <Icon name={menuOpen ? 'close' : 'menu'} />
            </button>
          </div>
        </div>
      </header>

      <main id="main">
        <section className="hero" aria-labelledby="hero-title">
          <div className="hero-content container">
            <div className="hero-copy">
              <p className="eyebrow">
                <span className="live-dot" /> LESS TROUBLE. MORE POSSIBILITY.
              </p>
              <h1 id="hero-title">
                Get back to
                <br />
                <span className="outline-word">what</span>{' '}
                <span className="lime-text">matters.</span>
              </h1>
              <p className="hero-description">
                Your computer should move you forward.
                <br className="desktop-break" /> Meet a calmer way to troubleshoot Windows—
                <br className="desktop-break" /> with local AI and you in control.
              </p>
              <div className="hero-actions">
                <button className="button button-primary" onClick={openDemo}>
                  Explore the demo <Icon name="arrow" size={18} />
                </button>
                <a className="text-link" href="#workflow">
                  <span className="play-circle">
                    <Icon name="play" size={12} />
                  </span>
                  See how it works
                </a>
              </div>
              <div className="hero-detail">
                <span className="windows-mark" aria-hidden="true">
                  <i />
                  <i />
                  <i />
                  <i />
                </span>
                <span>DESIGNED FOR WINDOWS</span>
                <span className="detail-slash">/</span>
                <span>EARLY PREVIEW</span>
              </div>
            </div>
            <Core />
          </div>
          <div className="hero-bottom container">
            <span>COMPLEX PROBLEMS. CONSIDERED SOLUTIONS.</span>
            <a href="#workflow" aria-label="Scroll to how TroubleShoot works">
              <span>SCROLL TO EXPLORE</span>
              <Icon name="arrow" size={15} />
            </a>
          </div>
        </section>

        <div className="principle-strip">
          <div className="container strip-inner">
            <span>
              <Icon name="chip" />
              Local-first intelligence
            </span>
            <span>
              <Icon name="shield" />
              Permission, before action
            </span>
            <span>
              <Icon name="eye" />
              Evidence, at every step
            </span>
            <span className="strip-end">
              BUILT BY TEAM DROS <span>↗</span>
            </span>
          </div>
        </div>

        <section id="workflow" className="workflow-section section-padding">
          <div className="container">
            <SectionLabel number="01">A CLEARER WAY THROUGH</SectionLabel>
            <div className="section-heading" data-reveal>
              <h2>
                From “what’s wrong?”
                <br />
                to <span className="muted-text">“here’s why.”</span>
              </h2>
              <p>
                No maze of settings. No mystery commands.
                <br />A considered process that makes every
                <br className="desktop-break" /> next step understandable.
              </p>
            </div>
            <div className="workflow-layout" data-reveal>
              <div
                className="workflow-steps"
                role="tablist"
                aria-label="Troubleshooting workflow"
                aria-orientation="vertical"
              >
                {workflow.map((item, index) => (
                  <button
                    key={item.tag}
                    id={`step-${index}`}
                    role="tab"
                    type="button"
                    aria-selected={step === index}
                    aria-controls="workflow-panel"
                    tabIndex={step === index ? 0 : -1}
                    className={`workflow-step ${step === index ? 'selected' : ''}`}
                    onClick={() => setStep(index)}
                    onKeyDown={(event) => {
                      if (['ArrowDown', 'ArrowUp', 'Home', 'End'].includes(event.key)) {
                        event.preventDefault()
                        const next =
                          event.key === 'Home'
                            ? 0
                            : event.key === 'End'
                              ? 2
                              : (index + (event.key === 'ArrowDown' ? 1 : 2)) % 3
                        setStep(next)
                        document.getElementById(`step-${next}`)?.focus()
                      }
                    }}
                  >
                    <span className="step-number">0{index + 1}</span>
                    <span>
                      <strong>{item.label}</strong>
                      <span className="step-description">{item.description}</span>
                    </span>
                    <Icon name="arrow" size={18} />
                  </button>
                ))}
              </div>
              <div
                className="workflow-preview"
                id="workflow-panel"
                role="tabpanel"
                aria-labelledby={`step-${step}`}
                tabIndex={0}
              >
                <div className="preview-titlebar">
                  <Brand compact />
                  <span>TROUBLESHOOT / SESSION PREVIEW</span>
                  <span className="sample-pill">SAMPLE</span>
                </div>
                <div className="preview-body" key={step}>
                  <p className="eyebrow">{selected.tag}</p>
                  <h3>{selected.title}</h3>
                  <div className="preview-message">
                    <span className="preview-avatar">
                      <Icon name={selected.icon} size={18} />
                    </span>
                    <p>{selected.message}</p>
                  </div>
                  <div className="preview-facts">
                    {selected.lines.map(([label, value]) => (
                      <div key={label}>
                        <span>{label}</span>
                        <span>{value}</span>
                      </div>
                    ))}
                  </div>
                  <div className="preview-status">
                    <span className="live-dot" />
                    {selected.status}
                  </div>
                  <p className="preview-note">{selected.note}</p>
                </div>
                <button className="preview-footer" onClick={openDemo}>
                  Try the complete walkthrough <Icon name="up-right" size={17} />
                </button>
              </div>
            </div>
          </div>
        </section>

        <section id="principles" className="principles-section section-padding">
          <div className="container">
            <SectionLabel number="02">INTELLIGENCE WITH INTENTION</SectionLabel>
            <div className="section-heading" data-reveal>
              <h2>
                Powerful by design.
                <br />
                <span className="muted-text">Bounded by principle.</span>
              </h2>
              <p>
                A better experience starts with trust.
                <br />
                These are the boundaries we’re building
                <br className="desktop-break" /> into the heart of TroubleShoot.
              </p>
            </div>
            <div className="feature-grid" data-reveal>
              <article className="feature-card">
                <div className="feature-top">
                  <span>01 / LOCAL</span>
                  <Icon name="chip" size={21} />
                </div>
                <div className="feature-diagram local-diagram" aria-hidden="true">
                  <span className="local-boundary">
                    <span className="tiny-chip">G</span>
                    <span className="local-pulse" />
                  </span>
                  <span className="diagram-caption">YOUR DEVICE. YOUR CONTEXT.</span>
                </div>
                <h3>
                  Close to the problem.
                  <br />
                  Closer to you.
                </h3>
                <p>
                  Designed around local Gemma inference. Your machine’s context stays where it
                  belongs, unless you explicitly choose a hosted mode.
                </p>
                <span className="feature-footnote">LOCAL-FIRST ARCHITECTURE</span>
              </article>
              <article className="feature-card">
                <div className="feature-top">
                  <span>02 / CONTROL</span>
                  <Icon name="shield" size={21} />
                </div>
                <div className="feature-diagram approval-diagram" aria-hidden="true">
                  <span className="diagram-node">PROPOSE</span>
                  <span className="diagram-wire" />
                  <span className="diagram-approval">
                    <Icon name="check" size={20} />
                  </span>
                  <span className="diagram-wire" />
                  <span className="diagram-node">ACT</span>
                  <span className="diagram-caption">YOU ARE THE DECISION POINT.</span>
                </div>
                <h3>
                  Assistance.
                  <br />
                  On your terms.
                </h3>
                <p>
                  See what an action will change before it happens. Specific permissions, selected
                  targets, and a stop button that belongs to you.
                </p>
                <span className="feature-footnote">EXPLICIT ACTION APPROVAL</span>
              </article>
              <article className="feature-card">
                <div className="feature-top">
                  <span>03 / CLARITY</span>
                  <Icon name="eye" size={21} />
                </div>
                <div className="feature-diagram evidence-diagram" aria-hidden="true">
                  <span className="evidence-column">
                    <i />
                    <i />
                    <i />
                    <i />
                  </span>
                  <span className="evidence-divider">→</span>
                  <span className="evidence-column after">
                    <i />
                    <i />
                    <i />
                    <i />
                  </span>
                  <span className="diagram-caption">A RESULT YOU CAN REASON ABOUT.</span>
                </div>
                <h3>
                  Less guesswork.
                  <br />
                  More evidence.
                </h3>
                <p>
                  A completed action is only the beginning. Fresh checks show what changed, what
                  didn’t, and what needs your attention next.
                </p>
                <span className="feature-footnote">VERIFIABLE OUTCOMES</span>
              </article>
            </div>
          </div>
        </section>

        <section className="control-section" aria-labelledby="control-title">
          <div className="control-rings" aria-hidden="true">
            <i />
            <i />
            <i />
            <i />
          </div>
          <div className="control-content" data-reveal>
            <span className="control-icon">
              <Icon name="shield" size={28} />
            </span>
            <p className="eyebrow">THE MOST IMPORTANT PART OF THE SYSTEM</p>
            <h2 id="control-title">
              Is still <span className="lime-text">you.</span>
            </h2>
            <p>
              Good technology gives you more agency.
              <br />
              Every observation, every permission, every next step.
            </p>
            <a className="text-link" href="#questions">
              Get to know the boundaries <Icon name="up-right" size={17} />
            </a>
          </div>
          <span className="control-coordinate left">HUMAN / IN THE LOOP</span>
          <span className="control-coordinate right">ALWAYS.</span>
        </section>

        <section id="questions" className="faq-section section-padding">
          <div className="container faq-layout">
            <div data-reveal>
              <SectionLabel number="03">BEFORE YOU BEGIN</SectionLabel>
              <h2>
                A few
                <br />
                <span className="muted-text">good questions.</span>
              </h2>
              <p className="faq-intro">
                Clear expectations are part
                <br />
                of a good experience.
              </p>
            </div>
            <div className="faq-list" data-reveal>
              {faqs.map(([question, answer], index) => (
                <details key={question}>
                  <summary>
                    <span className="faq-number">0{index + 1}</span>
                    <span>{question}</span>
                    <span className="faq-toggle">
                      <Icon name="plus" size={18} />
                    </span>
                  </summary>
                  <p>{answer}</p>
                </details>
              ))}
            </div>
          </div>
        </section>

        <section className="closing-section">
          <div className="container closing-inner">
            <div data-reveal>
              <p className="eyebrow">
                <span className="live-dot" /> A LITTLE LESS FRICTION STARTS HERE
              </p>
              <h2>
                Your next step.
                <br />
                <span className="muted-text">Made clearer.</span>
              </h2>
              <p>Explore a more thoughtful troubleshooting experience.</p>
              <div className="closing-actions">
                <button className="button button-primary" onClick={openDemo}>
                  Step inside the demo <Icon name="up-right" size={18} />
                </button>
                <a className="text-link" href={repository} target="_blank" rel="noreferrer">
                  View the project <Icon name="up-right" size={16} />
                </a>
              </div>
              <p className="closing-note">
                BROWSER PREVIEW <span>·</span> NO INSTALLATION <span>·</span> NO SYSTEM ACCESS
              </p>
            </div>
            <div className="closing-monogram" aria-hidden="true">
              <Brand compact />
            </div>
          </div>
        </section>
      </main>

      <footer className="site-footer">
        <div className="container footer-top">
          <a href="#" className="brand-link" aria-label="TroubleShoot home">
            <Brand />
          </a>
          <p>Technology that helps you move forward.</p>
          <a href="#" className="back-top">
            BACK TO TOP <Icon name="arrow" size={16} />
          </a>
        </div>
        <div className="container footer-bottom">
          <span>© {new Date().getFullYear()} TEAM DROS</span>
          <span>DESIGNED FOR WINDOWS. BUILT WITH INTENTION.</span>
          <a href={repository} target="_blank" rel="noreferrer">
            GITHUB <Icon name="up-right" size={13} />
          </a>
        </div>
      </footer>
      {demoOpen && (
        <Suspense
          fallback={
            <div className="demo-loading" role="status">
              Opening the preview…
            </div>
          }
        >
          <Demo onClose={closeDemo} />
        </Suspense>
      )}
    </>
  )
}
