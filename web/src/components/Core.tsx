export default function Core() {
  return (
    <div className="core-scene" aria-hidden="true">
      <div className="core-grid" />
      <div className="core-topline">
        <span>TS / DIAGNOSTIC CORE</span>
        <span>01—03</span>
      </div>
      <svg className="core-art" viewBox="0 0 600 620" fill="none">
        <defs>
          <radialGradient id="ambient">
            <stop stopColor="#b0da42" stopOpacity=".16" />
            <stop offset="1" stopColor="#b0da42" stopOpacity="0" />
          </radialGradient>
          <radialGradient id="core-light" cx=".35" cy=".25" r=".9">
            <stop stopColor="#f1ffa7" />
            <stop offset=".42" stopColor="#c9f24b" />
            <stop offset="1" stopColor="#657c2d" />
          </radialGradient>
          <linearGradient
            id="edge"
            x1="100"
            y1="180"
            x2="430"
            y2="390"
            gradientUnits="userSpaceOnUse"
          >
            <stop stopColor="#d6ff43" />
            <stop offset=".4" stopColor="#7d9940" />
            <stop offset="1" stopColor="#20271a" />
          </linearGradient>
          <linearGradient
            id="shell"
            x1="200"
            y1="190"
            x2="430"
            y2="430"
            gradientUnits="userSpaceOnUse"
          >
            <stop stopColor="#383e34" />
            <stop offset=".45" stopColor="#151a14" />
            <stop offset="1" stopColor="#090c09" />
          </linearGradient>
          <linearGradient id="beam" x1="0" y1="0" x2="0" y2="1">
            <stop stopColor="#d6ff43" stopOpacity="0" />
            <stop offset=".5" stopColor="#d6ff43" stopOpacity=".35" />
            <stop offset="1" stopColor="#d6ff43" stopOpacity="0" />
          </linearGradient>
          <pattern id="microgrid" width="12" height="12" patternUnits="userSpaceOnUse">
            <path d="M12 0H0v12" stroke="#3d531b" strokeOpacity=".14" strokeWidth=".7" />
          </pattern>
        </defs>
        <circle cx="300" cy="306" r="290" fill="url(#ambient)" />
        <g className="orbital-lines" stroke="#65714b">
          <circle cx="300" cy="306" r="230" strokeOpacity=".17" />
          <circle cx="300" cy="306" r="209" strokeDasharray="1 9" strokeOpacity=".5" />
          <path d="M300 60v24m0 445v24M49 306h25m451 0h26" strokeOpacity=".6" />
          <path d="M128 137a239 239 0 0 1 336 0M129 476a239 239 0 0 0 335 0" strokeOpacity=".35" />
          <ellipse
            cx="300"
            cy="330"
            rx="251"
            ry="100"
            transform="rotate(-27 300 330)"
            strokeOpacity=".3"
          />
          <ellipse
            cx="300"
            cy="330"
            rx="240"
            ry="91"
            transform="rotate(-27 300 330)"
            strokeOpacity=".15"
          />
        </g>
        <g className="core-floating">
          <path
            d="m300 219 142 83v55l-142 84-142-84v-55Z"
            fill="url(#shell)"
            stroke="#52613b"
            strokeWidth=".8"
          />
          <path d="m158 302 142 83 142-83M300 385v56" stroke="#758d45" strokeOpacity=".5" />
          <path d="m179 334 121 70 121-70" stroke="#d6ff43" strokeOpacity=".16" />
          <path
            d="m179 342 121 70 121-70m-242 8 121 70 121-70"
            stroke="#576544"
            strokeOpacity=".3"
          />
          <path
            d="m300 173 142 83v45l-142 83-142-83v-45Z"
            fill="url(#shell)"
            stroke="#647648"
            strokeWidth=".8"
          />
          <path d="m158 256 142 83 142-83M300 339v45" stroke="url(#edge)" strokeWidth="1.2" />
          <path d="m181 286 119 69 119-69" stroke="#d6ff43" strokeOpacity=".45" />
          <path d="m300 151 143 84v20l-143 84-143-84v-20Z" fill="#556b2f" stroke="url(#edge)" />
          <path
            d="m300 151 143 84-143 84-143-84Z"
            fill="url(#core-light)"
            stroke="#e5ff8a"
            strokeWidth="1.2"
          />
          <path d="m300 151 143 84-143 84-143-84Z" fill="url(#microgrid)" />
          <path d="m300 167 116 68-116 68-116-68Z" stroke="#536829" strokeOpacity=".5" />
          <path d="m300 177 99 58-99 58-99-58Z" stroke="#f2ffb3" strokeOpacity=".6" />
          <path
            d="m269 218 30-18 47 28-15 9-16-10-15 9 17 10-15 9-47-28 14-8 16 9 15-9-15-9Z"
            fill="#26351a"
          />
          <path d="M300 320v19" stroke="#e6ff8c" />
          <g fill="#d6ff43">
            <circle cx="185" cy="293" r="2" />
            <circle cx="194" cy="298" r="2" />
            <circle cx="203" cy="303" r="2" />
          </g>
        </g>
        <path d="M300 78v74m0 290v72" stroke="url(#beam)" strokeDasharray="3 5" />
        <g stroke="#7b8962" strokeWidth=".7">
          <path d="m151 248-39-23H46m385 137 36 21h80M254 426l-44 50h-70" />
        </g>
        <g fill="#a8b28f" fontFamily="'DM Mono', monospace" fontSize="9" letterSpacing="1">
          <text x="46" y="211">
            LOCAL REASONING
          </text>
          <text x="463" y="403">
            BOUNDED
          </text>
          <text x="463" y="416">
            ACTIONS
          </text>
          <text x="125" y="493">
            FRESH EVIDENCE
          </text>
        </g>
        <g fill="#d6ff43">
          <circle cx="151" cy="248" r="3" />
          <circle cx="431" cy="362" r="3" />
          <circle cx="254" cy="426" r="3" />
        </g>
        <circle className="orbit-dot" cx="496" cy="188" r="4" fill="#d6ff43" />
      </svg>
      <div className="core-caption">
        <span className="live-dot" /> <span>DESIGNED TO KEEP YOU IN CONTROL</span>
        <span className="core-cross">+</span>
      </div>
    </div>
  )
}
