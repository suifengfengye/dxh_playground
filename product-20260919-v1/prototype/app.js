/* =========================================================
   Workspace — interactive prototype
   Vanilla JS. No build step, no dependencies, no backend.
   All data is fake and lives in memory only.
   ========================================================= */

/* ---------------- helpers ---------------- */
const $ = (s, r) => (r || document).querySelector(s);
const $$ = (s, r) => Array.from((r || document).querySelectorAll(s));
const esc = (s) => String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const wait = (ms) => new Promise((r) => setTimeout(r, ms));
const titleCase = (s) => s.charAt(0).toUpperCase() + s.slice(1);

/* ---------------- seed data ---------------- */
const JOB_TEXT = `Operations Manager
Northstar Co. · Austin, TX · Hybrid · Full-time

Responsibilities
- Coordinate cross-functional operations projects across sales, support and finance
- Own the onboarding programme for new clients and internal teams
- Build reporting and dashboards for the operations leadership team
- Manage vendor relationships and contract renewals
- Support the annual budget planning cycle

Requirements
- 3+ years of project coordination or operations experience
- Experience working across functions (sales, support, finance)
- Strong reporting and spreadsheet skills
- Vendor or contract management experience
- Experience owning an onboarding or enablement programme
- Bachelor's degree or equivalent experience
- Must be authorized to work in the United States
- Ability to manage a team of 5 operations associates
- Budget planning experience`;

function reqsFor(kind) {
  const R = (id, text, status, note) => ({ id, text, status, note: note || '' });
  if (kind === 'none') return [];
  return [
    R('r4', '3+ years of project coordination', 'supported', 'Northstar Co., Jan 2022 – Present'),
    R('r1', 'Cross-functional projects', 'supported', 'Northstar experience, bullet 1'),
    R('r5', 'Reporting and dashboards', 'supported', 'Skills you confirmed'),
    R('r7', 'Owning an onboarding programme', 'supported', 'Northstar experience, bullet 1'),
    R('r6', 'Vendor or contract management', 'supported', 'Northstar experience, bullet 2'),
    R('r9', "Bachelor's degree", 'supported', 'Education on file'),
    R('r8', 'Budget planning experience', 'gap', 'No budget ownership in your profile'),
    R('r2', 'Manage a team of 5 associates', 'gap', 'No people management in your profile'),
    R('r3', 'US work authorization', 'confirm', 'You have not provided this')
  ];
}

function seedApps() {
  return [
    {
      id: 'a1',
      title: 'Operations Manager',
      company: 'Northstar Co.',
      location: 'Austin, TX',
      arrangement: 'Hybrid',
      employment: 'Full-time',
      deadline: '',
      status: 'drafting',
      importedAt: 'Sep 19, 2026',
      sourceUrl: 'https://careers.example.com/jobs/ops-manager',
      sourceDomain: 'careers.example.com',
      jobText: JOB_TEXT,
      requirements: reqsFor('full'),
      unresolved: true,
      draft: {
        version: 2,
        summary: 'Operations professional with experience coordinating cross-functional onboarding projects.',
        bullets: [
          'Coordinated onboarding projects across sales and customer support.',
          'Built weekly reporting used by three teams to track onboarding progress.'
        ],
        userEdited: false,
        cover: null,
        coverFailed: false,
        changes: [
          { text: 'Summary reworded to lead with operations work', reason: 'The posting names cross-functional coordination first.' },
          { text: 'Bullet 1 moved up under Experience', reason: 'Same reason — it is the closest match to the core requirement.' },
          { text: 'Removed "detail-oriented"', reason: 'No evidence in your profile, so it was dropped rather than invented.' }
        ]
      },
      checks: { contact: true, extractable: true, overflow: true, reviewed: false, pdfFail: false },
      applied: null,
      activity: [
        { when: 'Sep 19, 2026', what: 'Job imported from URL', who: 'You' },
        { when: 'Sep 19, 2026', what: 'Fit analysis completed', who: 'System' },
        { when: 'Sep 19, 2026', what: 'Resume draft v1 created', who: 'You' },
        { when: 'Sep 20, 2026', what: 'Status: Saved → Drafting', who: 'You · note added' }
      ]
    },
    {
      id: 'a2',
      title: 'Project Coordinator',
      company: 'Example Works',
      location: 'Austin, TX',
      arrangement: 'Remote',
      employment: 'Full-time',
      deadline: 'Sep 25, 2026',
      status: 'ready',
      importedAt: 'Sep 18, 2026',
      sourceUrl: 'https://jobs.example-works.com/project-coordinator',
      sourceDomain: 'jobs.example-works.com',
      jobText: 'Project Coordinator\nExample Works · Remote\n\nRequirements\n- Coordinate schedules across teams\n- Track project budgets\n- Prepare status reports',
      requirements: [
        { id: 'b1', text: 'Coordinate schedules across teams', status: 'supported', note: 'Northstar experience' },
        { id: 'b2', text: 'Prepare status reports', status: 'supported', note: 'Skills you confirmed' }
      ],
      unresolved: false,
      draft: {
        version: 1,
        summary: 'Coordinator with experience keeping cross-team projects on schedule.',
        bullets: ['Kept onboarding projects on schedule across sales and support.'],
        userEdited: false,
        cover: null,
        coverFailed: false,
        changes: [{ text: 'Summary written from your confirmed experience', reason: 'First draft.' }]
      },
      checks: { contact: true, extractable: true, overflow: true, reviewed: true, pdfFail: false },
      applied: null,
      activity: [
        { when: 'Sep 18, 2026', what: 'Job imported from URL', who: 'You' },
        { when: 'Sep 18, 2026', what: 'Resume draft v1 created and reviewed', who: 'You' }
      ]
    },
    {
      id: 'a3',
      title: 'Customer Success Lead',
      company: 'Sample Studio',
      location: 'Remote (US)',
      arrangement: 'Remote',
      employment: 'Full-time',
      deadline: '',
      status: 'applied',
      importedAt: 'Sep 14, 2026',
      sourceUrl: 'https://sample-studio.example.com/careers/cs-lead',
      sourceDomain: 'sample-studio.example.com',
      jobText: 'Customer Success Lead\nSample Studio · Remote (US)',
      requirements: [{ id: 'c1', text: 'Own customer relationships', status: 'supported', note: 'Northstar experience' }],
      unresolved: false,
      draft: { version: 1, summary: 'Customer-facing operations professional.', bullets: [], userEdited: false, cover: null, coverFailed: false, changes: [] },
      checks: { contact: true, extractable: true, overflow: true, reviewed: true, pdfFail: false },
      applied: { date: 'Sep 15, 2026', version: 'Resume v1', note: 'Applied on employer website' },
      activity: [
        { when: 'Sep 14, 2026', what: 'Job imported from URL', who: 'You' },
        { when: 'Sep 15, 2026', what: 'Status: Ready → Applied', who: 'You · submission recorded' }
      ]
    },
    {
      id: 'a4',
      title: 'Program Specialist',
      company: 'Demo Group',
      location: 'Dallas, TX',
      arrangement: 'On-site',
      employment: 'Full-time',
      deadline: '',
      status: 'saved',
      importedAt: 'Sep 14, 2026',
      sourceUrl: '',
      sourceDomain: '',
      jobText: 'Program Specialist\nDemo Group · Dallas, TX\n\nRequirements\n- Programme coordination\n- Stakeholder communication',
      requirements: [],
      unresolved: false,
      draft: null,
      checks: null,
      applied: null,
      activity: [{ when: 'Sep 14, 2026', what: 'Job added by pasting text', who: 'You' }]
    }
  ];
}

function seedState() {
  return {
    route: 'signin',
    email: '',
    signinSent: false,
    profile: {
      contact: { name: 'Alex Morgan', email: 'alex@example.com', city: 'Austin, TX', confirmed: false },
      experience: [{
        id: 'e1', title: 'Operations Specialist', company: 'Northstar Co.',
        dates: 'Jan 2022 – Present',
        text: 'Coordinated onboarding projects across sales and customer support.',
        confirmed: false, editedByUser: false
      }],
      education: [{ id: 'ed1', degree: 'B.A.', field: '', confirmed: false }],
      skills: [],
      sourceFile: null
    },
    setup: { attached: false, reading: false, extracted: false, paste: '', pasteMode: null, editId: null, proposed: null },
    ui: { filter: 'all', moreReqs: false, editLine: null, newFact: '', para: null, toolbar: false, askInput: '', asked: null, confirmDelete: '', coverChoice: false },
    apps: seedApps(),
    quota: { used: 3, total: 10 },
    demo: { empty: false, readFail: false, partial: false, quotaOut: false, degraded: false, expired: false },
    modal: null,
    toasts: [],
    task: null,
    imp: { url: 'https://careers.example.com/jobs/ops-manager', reading: false, read: null, error: false, pasted: '' }
  };
}

let S = seedState();

/* ---------------- routing ---------------- */
function parseRoute() {
  const raw = (location.hash || '#/signin').replace(/^#\/?/, '');
  const p = raw.split('/').filter(Boolean);
  if (!p.length) return { name: 'signin' };
  if (p[0] === 'applications' && p[1] && p[2]) return { name: p[2], id: p[1] };
  return { name: p[0], id: p[1] };
}
function go(name, id) {
  location.hash = '#/' + name + (id ? '/' + id : '');
}
function appById(id) { return S.apps.find((a) => a.id === id); }
function currentId() { return parseRoute().id; }

/* ---------------- small builders ---------------- */
const chip = (kind, text) => `<span class="chip chip-${kind}">${esc(text)}</span>`;
const ai = (label, inner, secondary) => `<div class="ai-block${secondary ? ' ai-secondary' : ''}"><span class="ai-label">${esc(label)}</span>${inner}</div>`;
const btn = (label, action, data, kind) =>
  `<button class="btn ${kind || 'btn-secondary'}" data-action="${action}"${data ? ' ' + data : ''}>${esc(label)}</button>`;

function statusLabel(s) {
  return { saved: 'Saved', drafting: 'Drafting', ready: 'Ready', applied: 'Applied', interview: 'Interview', offer: 'Offer', closed: 'Closed' }[s] || s;
}
function reqChip(status) {
  if (status === 'supported') return chip('success', 'Supported');
  if (status === 'gap') return chip('neutral', 'Gap');
  return chip('attention', 'Needs confirmation');
}
function openCount(a) { return a.requirements ? a.requirements.filter((r) => r.status !== 'supported').length : 0; }
function supportedCount(a) { return a.requirements ? a.requirements.filter((r) => r.status === 'supported').length : 0; }

/* ---------------- shell ---------------- */
function shell(active, inner) {
  return `
  <header class="appbar">
    <div class="appbar-left"><span class="brandmark">Workspace</span></div>
    <div class="appbar-right">
      <span class="savestate">${esc(S.saveState || 'Saved')}</span>
      <button class="btn btn-ghost btn-sm" data-action="nav" data-route="settings">${esc(S.profile.contact.email)}</button>
    </div>
  </header>
  <div class="shell">
    <nav class="sidenav" aria-label="Main">
      <a data-action="nav" data-route="applications" class="${active === 'applications' ? 'on' : ''}">Applications</a>
      <a data-action="nav" data-route="profile" class="${active === 'profile' ? 'on' : ''}">My profile</a>
      <a data-action="nav" data-route="settings" class="${active === 'settings' ? 'on' : ''}">Settings</a>
    </nav>
    <main class="main">${inner}</main>
  </div>`;
}

/* =========================================================
   P01 — sign in
   ========================================================= */
function renderSignin() {
  const right = S.signinSent
    ? `<div class="card">
        <h2 class="card-title">Check your email</h2>
        <p class="text-muted">We sent a sign-in link to <strong>${esc(S.email || 'you@example.com')}</strong>. It expires in 15 minutes.</p>
        <div class="btn-row" style="margin-top:var(--space-4)">
          ${btn('Open the workspace (simulate the link)', 'signin-open', '', 'btn-primary')}
          ${btn('Change email', 'signin-change')}
          ${btn('Resend link', 'signin-resend', '', 'btn-ghost')}
        </div>
        <p class="text-muted" style="margin-top:var(--space-3)">Expired links come back to this same page. There is no separate sign-up, sign-in, or forgot-password flow.</p>
      </div>`
    : `<div class="card">
        <h2 class="card-title">Start your workspace</h2>
        <p class="text-muted">Already have an account? Use the same email.</p>
        <label class="field-label" for="email">Email address</label>
        <input class="input" id="email" type="email" value="${esc(S.email)}" placeholder="you@example.com" autocomplete="email">
        <div class="btn-row" style="margin-top:var(--space-4)">
          ${btn('Send sign-in link', 'signin-send', '', 'btn-primary')}
        </div>
        <p class="text-muted" style="margin-top:var(--space-3)">By continuing, you agree to the Terms and acknowledge the Privacy notice.</p>
        <div class="notice" style="margin-top:var(--space-4)">Your resume is processed in the cloud.<br><a data-action="nav" data-route="settings">Read how your data is used and deleted</a></div>
      </div>`;

  return `
  <header class="appbar">
    <div class="appbar-left"><span class="brandmark">Workspace</span></div>
    <div class="appbar-right"><span class="savestate">Prototype · no installation · no API key</span></div>
  </header>
  <main class="main">
    <div class="auth-grid" style="max-width:1000px;margin:auto;padding-top:var(--space-8)">
      <div>
        <h1 class="page-title">Bring a job posting.<br>See how your experience lines up with it.</h1>
        <p class="page-sub">Then get a resume built from your real experience — and see exactly what the assistant changed.</p>
        <div class="card" style="margin-top:var(--space-5)">
          <strong>What the assistant does</strong>
          <ul class="checklist" style="margin-top:var(--space-3)">
            <li>Reads your resume and turns it into facts you confirm</li>
            <li>Reads the posting and maps it to those facts</li>
            <li>Drafts and rewrites, showing its reasons</li>
          </ul>
        </div>
        <div class="notice" style="margin-top:var(--space-4)">
          <strong>What it never does</strong>
          Invent experience, numbers, or skills you don't have.<br>
          Search for jobs or submit applications for you.
        </div>
      </div>
      ${right}
    </div>
  </main>`;
}

/* =========================================================
   P02 — build your profile
   ========================================================= */
function profileChecklist() {
  const c = S.profile.contact;
  const e = S.profile.experience[0];
  const ed = S.profile.education[0];
  const requiredDone = c.confirmed && e && e.confirmed;

  const item = (label, done, has) =>
    `<li class="${done ? 'done' : (has ? 'attention' : '')}">${esc(label)}${!done && has ? ' <button data-action="focus-waiting">Fix</button>' : ''}</li>`;

  return `
  <div class="card">
    <h2 class="card-title">What's in your profile</h2>

    <div class="group">
      <span class="group-label">Required to start</span>
      <ul class="checklist">
        <li class="${c.confirmed ? 'done' : 'attention'}">Contact — ${c.confirmed ? 'confirmed' : 'needs your confirmation'}</li>
        <li class="${e && e.confirmed ? 'done' : 'attention'}">One experience — ${e && e.confirmed ? 'confirmed' : 'needs your confirmation'}</li>
      </ul>
    </div>

    <div class="group">
      <span class="group-label">Waiting on you · ${waitingCount()}</span>
      <ul class="checklist">
        ${ed.confirmed ? '' : `<li class="${ed.field ? 'done' : 'attention'}">Education — ${ed.field ? 'confirmed' : 'needs a field of study'}</li>`}
        ${S.profile.experience.length > 1 ? '' : '<li>The rest of your experience — optional</li>'}
        ${waitingCount() === 1 && !ed.confirmed ? '' : ''}
      </ul>
    </div>

    <div class="group">
      <span class="group-label">Optional</span>
      <ul class="checklist muted-list">
        <li class="${S.profile.skills.length ? 'done' : ''}">Skills ${S.profile.skills.length ? '— ' + S.profile.skills.length + ' confirmed' : ''}</li>
        <li class="${S.profile.experience.length > 1 ? 'done' : ''}">A second role</li>
        <li>Projects</li>
      </ul>
    </div>

    <div class="group">
      <span class="group-label">Asked later, only when a job needs it</span>
      <ul class="checklist muted-list">
        <li>Work authorization</li>
        <li>Target roles / locations</li>
        <li>Salary preference</li>
      </ul>
    </div>

    <button class="btn btn-primary btn-block" style="margin-top:var(--space-5)" data-action="setup-finish" ${requiredDone ? '' : 'disabled'}>
      ${requiredDone ? 'Start with what I have' : 'Confirm contact and one role first'}
    </button>
    ${requiredDone ? '' : '<p class="text-muted" style="margin-top:var(--space-2)">Nothing else is required — this unlocks after two confirmations.</p>'}
  </div>`;
}
function waitingCount() {
  let n = 0;
  if (!S.profile.education[0].confirmed) n++;
  if (!S.profile.contact.confirmed || !S.profile.experience[0].confirmed) n++;
  return n;
}

function factCardContact() {
  const c = S.profile.contact;
  if (S.ui.editId === 'contact') {
    return `<div class="fact">
      <div class="fact-head"><span class="fact-title">Contact</span>${chip('attention', 'Editing')}</div>
      <label class="field-label" for="c-name">Full name</label><input class="input" id="c-name" value="${esc(c.name)}">
      <label class="field-label" for="c-email">Email</label><input class="input" id="c-email" value="${esc(c.email)}">
      <label class="field-label" for="c-city">City / State <span class="optional">(optional)</span></label><input class="input" id="c-city" value="${esc(c.city)}">
      <div class="btn-row" style="margin-top:var(--space-4)">
        ${btn('Save', 'fact-save', 'data-kind="contact"', 'btn-primary')}${btn('Cancel', 'fact-cancel', '', 'btn-ghost')}
      </div>
    </div>`;
  }
  return `<div class="fact${c.confirmed ? ' confirmed' : ''}">
    <div class="fact-head"><span class="fact-title">Contact</span>${c.confirmed ? chip('success', 'Confirmed') : chip('attention', 'Needs confirmation')}</div>
    <div class="fact-body">${esc(c.name)} · ${esc(c.email)}${c.city ? ' · ' + esc(c.city) : ''}</div>
    <div class="btn-row">
      ${c.confirmed ? btn('Edit', 'fact-edit', 'data-kind="contact"') : btn('Looks right', 'fact-confirm', 'data-kind="contact"', 'btn-primary') + btn('Edit', 'fact-edit', 'data-kind="contact"')}
    </div>
  </div>`;
}

function factCardExperience() {
  const e = S.profile.experience[0];
  if (S.ui.editId === 'e1') {
    return `<div class="fact">
      <div class="fact-head"><span class="fact-title">Experience · ${esc(e.title)}</span>${chip('attention', 'Editing')}</div>
      <label class="field-label" for="e-company">Company</label><input class="input" id="e-company" value="${esc(e.company)}">
      <label class="field-label" for="e-title">Job title</label><input class="input" id="e-title" value="${esc(e.title)}">
      <label class="field-label" for="e-dates">Dates</label><input class="input" id="e-dates" value="${esc(e.dates)}">
      <label class="field-label" for="e-text">What you did — your own words are fine</label>
      <textarea class="textarea" id="e-text">${esc(e.text)}</textarea>
      <div class="btn-row" style="margin-top:var(--space-4)">
        ${btn('Save', 'fact-save', 'data-kind="e1"', 'btn-primary')}${btn('Cancel', 'fact-cancel', '', 'btn-ghost')}
      </div>
      <p class="text-muted" style="margin-top:var(--space-3)">Your own wording is stored separately — a later AI rewrite will never overwrite it.</p>
    </div>`;
  }
  return `<div class="fact${e.confirmed ? ' confirmed' : ''}">
    <div class="fact-head"><span class="fact-title">Experience · ${esc(e.title)}</span>${e.confirmed ? chip('success', 'Confirmed') : chip('attention', 'Needs confirmation')}</div>
    <div class="fact-body">${esc(e.company)} · <span class="num">${esc(e.dates)}</span><br><span class="quote">"${esc(e.text)}"</span>${e.editedByUser ? '<br><span class="text-muted">You edited this line</span>' : ''}</div>
    <div class="btn-row">
      ${e.confirmed ? btn('Edit', 'fact-edit', 'data-kind="e1"') : btn('Looks right', 'fact-confirm', 'data-kind="e1"', 'btn-primary') + btn('Edit', 'fact-edit', 'data-kind="e1"')}
      ${btn('Remove', 'fact-remove', 'data-kind="e1"', 'btn-ghost')}
    </div>
  </div>`;
}

function factCardEducation() {
  const ed = S.profile.education[0];
  if (S.ui.editId === 'ed1') {
    return `<div class="fact">
      <div class="fact-head"><span class="fact-title">Education</span>${chip('attention', 'Editing')}</div>
      <label class="field-label" for="ed-degree">Degree</label><input class="input" id="ed-degree" value="${esc(ed.degree)}">
      <label class="field-label" for="ed-field">Field of study</label><input class="input" id="ed-field" value="${esc(ed.field)}" placeholder="e.g. Business Administration">
      <div class="btn-row" style="margin-top:var(--space-4)">
        ${btn('Save', 'fact-save', 'data-kind="ed1"', 'btn-primary')}${btn('Cancel', 'fact-cancel', '', 'btn-ghost')}
      </div>
    </div>`;
  }
  return `<div class="fact${ed.confirmed ? ' confirmed' : ''}">
    <div class="fact-head"><span class="fact-title">Education</span>${ed.confirmed ? chip('success', 'Confirmed') : chip('neutral', 'Missing a detail')}</div>
    <div class="fact-body">${ed.field ? esc(ed.degree) + ' in ' + esc(ed.field) : 'I found a degree with no field of study. Optional — add it or skip.'}</div>
    <div class="btn-row">
      ${ed.confirmed ? btn('Edit', 'fact-edit', 'data-kind="ed1"') : btn('Add detail', 'fact-edit', 'data-kind="ed1"') + btn('Skip', 'fact-confirm', 'data-kind="ed1"', 'btn-ghost')}
    </div>
  </div>`;
}

function renderSetup() {
  const st = S.setup;
  const pending = [];
  if (st.extracted && !S.profile.contact.confirmed) pending.push('contact');
  if (st.extracted && !S.profile.experience[0].confirmed) pending.push('experience');

  let stream = '';
  if (!st.attached && !st.pasteMode) {
    stream = ai('Assistant', `<p>Let's start with what you already have. Any of these works — you can change everything after.</p>
      <div class="btn-row">
        ${btn('Attach a file', 'setup-attach')}${btn('Paste resume text', 'setup-paste')}${btn('Just type it', 'setup-type')}
      </div>`);
  }

  if (st.pasteMode) {
    stream += `<div class="card">
      <h2 class="card-title">${st.pasteMode === 'paste' ? 'Paste your resume text' : 'Tell me about your most recent job'}</h2>
      <p class="text-muted">${st.pasteMode === 'paste' ? 'Open your resume, select all, and paste it here.' : 'A whole paragraph is fine. I will turn it into facts you can correct.'}</p>
      <textarea class="textarea" id="paste-box" placeholder="${st.pasteMode === 'paste' ? 'ALEX MORGAN...' : 'I ran client onboarding at a logistics company...'}">${esc(st.paste)}</textarea>
      <div class="btn-row" style="margin-top:var(--space-4)">
        ${btn('Extract facts', 'setup-extract', '', 'btn-primary')}${btn('Cancel', 'setup-cancel', '', 'btn-ghost')}
      </div>
    </div>`;
  }

  if (st.attached) {
    stream += `<div class="attach-row"><span class="chip chip-neutral">resume.docx</span><span>${st.reading ? 'Reading your resume…' : 'Read'}</span></div>`;
  }

  if (st.extracted) {
    stream += ai('Assistant', `<p>I read it. Confirm, fix, or remove anything — nothing is used until you confirm it.</p>
      ${factCardContact()}${factCardExperience()}${factCardEducation()}`);

    if (S.profile.skills.length === 0) {
      stream += ai('Assistant', `<p>Two things most people add. Both optional — or go straight to your workspace.</p>
        <div class="btn-row">
          ${btn('Skills', 'setup-skills')}${btn('A second role', 'setup-role')}${btn('Nothing else for now', 'setup-finish', '', 'btn-ghost')}
        </div>`);
    } else {
      stream += ai('Assistant', `<p>Added skills: <strong>${esc(S.profile.skills.join(' · '))}</strong></p>
        <div class="btn-row">${btn('Add a second role', 'setup-role')}${btn('Nothing else for now', 'setup-finish', '', 'btn-ghost')}</div>`);
    }

    stream += `<div class="composer">
      <input class="input" id="chat-input" type="text" placeholder="Tell me anything I missed…" aria-label="Message the assistant">
      ${btn('Send', 'chat-send', '', 'btn-primary')}
    </div>`;
  }

  const railNote = pending.length
    ? `<div class="card card-quiet"><strong>${pending.length} item${pending.length > 1 ? 's' : ''} waiting on you.</strong><p>Unconfirmed facts are never used to write a resume. Confirm them above, or come back later — your work is saved.</p></div>`
    : `<div class="card card-quiet"><strong>Only contact and one role are required.</strong><p>Everything else can wait. Preferences are never asked here — a posting asks when it actually matters.</p></div>`;

  return `
  <header class="appbar">
    <div class="appbar-left"><span class="brandmark">Build your profile</span></div>
    <div class="appbar-right">
      <span class="savestate">Saved · just now</span>
      ${btn('Finish later', 'setup-finish', '', 'btn-ghost btn-sm')}
    </div>
  </header>
  <div class="shell" style="grid-template-columns:1fr">
    <main class="main">
      <div class="grid-2">
        <div class="col stack">
          <h1 class="page-title">Build your profile</h1>
          <p class="page-sub" style="margin:0">Upload your resume, paste the text, or just tell me about your most recent job.</p>
          ${stream}
        </div>
        <aside class="stack">${profileChecklist()}${railNote}</aside>
      </div>
    </main>
  </div>`;
}

/* =========================================================
   P03 — applications
   ========================================================= */
function assistantStrip() {
  const drafting = S.apps.find((a) => a.status === 'drafting');
  const ready = S.apps.find((a) => a.status === 'ready');
  const gaps = S.apps.find((a) => a.status === 'saved' && a.requirements.length === 0);
  const lines = [];
  if (ready) lines.push(`${ready.title} at ${ready.company}${ready.deadline ? ` closes ${ready.deadline}` : ''} and the resume is ready. Download and submit whenever you want.`);
  if (drafting && openCount(drafting) > 0) lines.push(`${drafting.title} fit is done. ${openCount(drafting)} requirement${openCount(drafting) > 1 ? 's need' : ' needs'} a decision — open it to see which.`);
  if (gaps) lines.push(`${gaps.title} has not been analysed yet. Run the fit to see where you stand.`);
  if (!lines.length) return '';
  return ai('Assistant · what needs you today', `${lines.map((l) => `<p>${esc(l)}</p>`).join('')}
    <p class="disclaimer">Read from the applications below and the postings you imported. It never suggests jobs you have not added.</p>`);
}

function renderApplications() {
  const list = S.demo.empty ? [] : S.apps.filter((a) => S.ui.filter === 'all' || a.status === S.ui.filter);
  const filters = ['all', 'saved', 'drafting', 'ready', 'applied', 'closed'];

  if (!S.apps.length || S.demo.empty) {
    return shell('applications', `
      <div class="page-head"><div><h1 class="page-title">Applications</h1></div>${btn('+ Add a job', 'nav', 'data-route="new"', 'btn-primary')}</div>
      <div class="card" style="max-width:560px">
        <h2 class="card-title">No applications yet</h2>
        <p class="font-reading">Found a role on a job board or company site?</p>
        <p class="font-reading">Paste the link and I'll read it, tell you how your experience lines up, and prepare a resume if you want one.</p>
        <div class="btn-row" style="margin-top:var(--space-4)">${btn('Add your first job', 'nav', 'data-route="new"', 'btn-primary')}</div>
        <p class="text-muted" style="margin-top:var(--space-3)">I don't search for jobs or apply anywhere for you.</p>
      </div>`);
  }

  const rows = list.map((a) => {
    const read = S.demo.degraded
      ? `<span class="text-muted">Analysis finished — open to see what is covered</span><br><span class="row-sub">No count available this time</span>`
      : a.requirements.length === 0
        ? `<span class="row-sub">Not analysed yet — run the fit</span>`
        : `${supportedCount(a)} of ${a.requirements.length} requirements have evidence<br><span class="row-sub">${openCount(a)} need${openCount(a) === 1 ? 's' : ''} your attention</span>`;
    const next = { drafting: 'View progress', ready: 'Download', applied: 'Update status', saved: a.requirements.length ? 'View fit' : 'Run fit', interview: 'Update status', offer: 'Update status', closed: 'View history' }[a.status] || 'Open';
    return `<tr class="clickable" data-action="open-app" data-id="${a.id}">
      <td><span class="row-title">${esc(a.title)}</span><span class="row-sub">${esc(a.company)}</span></td>
      <td>${chip(a.status === 'ready' ? 'success' : 'neutral', statusLabel(a.status))}</td>
      <td class="num">${esc(a.importedAt)}<br><span class="row-sub">${a.deadline ? 'Closes ' + esc(a.deadline) : (a.applied ? 'Applied ' + esc(a.applied.date) : 'Deadline not stated')}</span></td>
      <td>${read}</td>
      <td><button class="btn btn-secondary btn-sm" data-action="open-app" data-id="${a.id}">${esc(next)}</button></td>
    </tr>`;
  }).join('');

  return shell('applications', `
    <div class="page-head">
      <div><h1 class="page-title">Applications</h1><p class="page-sub" style="margin:0">Pick up where you left off.</p></div>
      ${btn('+ Add a job', 'nav', 'data-route="new"', 'btn-primary')}
    </div>
    ${assistantStrip()}
    <div class="btn-row" style="margin:var(--space-5) 0">
      ${filters.map((f) => `<button class="btn ${S.ui.filter === f ? 'btn-primary' : 'btn-secondary'} btn-sm" data-action="filter" data-value="${f}">${f === 'all' ? 'All' : statusLabel(f)}</button>`).join('')}
    </div>
    <table class="table">
      <thead><tr><th scope="col">Role / company</th><th scope="col">Status</th><th scope="col">Updated / deadline</th><th scope="col">Assistant read</th><th scope="col">Next step</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>
    <p class="text-muted" style="margin-top:var(--space-3)">${list.length} application${list.length > 1 ? 's' : ''} · example data</p>
  `);
}

/* =========================================================
   P04 — add a job
   ========================================================= */
function renderNewJob() {
  const i = S.imp;
  let right = '';
  if (i.error) {
    right = `<div class="card">
      <h2 class="card-title">We couldn't read this page</h2>
      <div class="notice">Your original URL is preserved: <span class="num">${esc(i.url)}</span></div>
      <p class="text-muted" style="margin-top:var(--space-3)">This site may require sign-in, or it may block automated access. I will not sign in on your behalf.</p>
      <label class="field-label" for="paste-fallback">Paste the full job description</label>
      <textarea class="textarea" id="paste-fallback" placeholder="Paste the full responsibilities and requirements...">${esc(i.pasted)}</textarea>
      <div class="btn-row" style="margin-top:var(--space-4)">
        ${btn('Import from pasted text', 'job-paste', '', 'btn-primary')}${btn('Try another link', 'job-retry', '', 'btn-ghost')}
      </div>
    </div>`;
  } else if (i.reading) {
    right = `<div class="card"><p><span class="spinner"></span> Reading the posting…</p>
      <ul class="task-list" style="margin-top:var(--space-3)"><li class="running"><span class="mark">·</span>Fetching the page</li><li class="pending"><span class="mark">·</span>Extracting company, title and location</li><li class="pending"><span class="mark">·</span>Counting requirements</li></ul>
    </div>`;
  } else if (i.read) {
    right = ai('Assistant · what I read', `
      <p class="disclaimer" style="margin-top:0">Read from ${esc(i.read.domain)} on ${esc(i.read.when)} · every line below is editable</p>
      <div class="btn-row" style="margin:var(--space-3) 0">
        <span class="chip chip-neutral">Title</span><strong>${esc(i.read.title)}</strong>
        <button class="btn btn-ghost btn-sm" data-action="job-edit-line">Edit</button>
      </div>
      <div class="btn-row" style="margin-bottom:var(--space-3)">
        <span class="chip chip-neutral">Company</span><strong>${esc(i.read.company)}</strong>
        <button class="btn btn-ghost btn-sm" data-action="job-edit-line">Edit</button>
      </div>
      <p>${esc(i.read.location)} · ${esc(i.read.arrangement)} · ${esc(i.read.employment)}</p>
      <p>I found <strong>${i.read.count} requirements</strong> across the responsibilities and qualifications.</p>
      <hr style="border:0;border-top:1px solid var(--ai-border);margin:var(--space-4) 0">
      <p><strong>Not stated in the posting</strong></p>
      <p>${esc(i.read.notStated.join(' · '))}</p>
      <p class="disclaimer">I left these blank instead of guessing. Add them only if you actually know them.</p>
      <div class="btn-row" style="margin-top:var(--space-4)">
        ${btn('Edit text', 'job-edit-text')}${btn('Save & analyze', 'job-save', '', 'btn-primary')}
      </div>`);
  }

  return shell('applications', `
    <div class="page-head">
      <div><h1 class="page-title">Add a job</h1><p class="page-sub" style="margin:0">Paste a public posting link, or paste the full description.</p></div>
      ${btn('Cancel', 'nav', 'data-route="applications"', 'btn-ghost')}
    </div>
    <div class="grid-2">
      <div class="col stack">
        <div class="tabs">
          <button class="${i.pasted ? '' : 'on'}" data-action="tab-import" data-value="url">Job URL</button>
          <button class="${i.pasted ? 'on' : ''}" data-action="tab-import" data-value="paste">Paste description</button>
        </div>
        ${i.pasted
          ? `<label class="field-label" for="pd">Full job description</label>
             <textarea class="textarea" id="pd" placeholder="Paste the full responsibilities and requirements...">${esc(i.pasted)}</textarea>
             <label class="field-label" for="pd-url">Source URL <span class="optional">(optional)</span></label>
             <input class="input" id="pd-url" placeholder="https://...">
             <p class="text-muted">I will pull the company and title out of the text — you won't have to fill those in.</p>
             <div class="btn-row">${btn('Import from text', 'job-paste', '', 'btn-primary')}</div>`
          : `<label class="field-label" for="job-url">Job posting URL</label>
             <input class="input" id="job-url" value="${esc(i.url)}">
             <div class="btn-row" style="margin-top:var(--space-3)">${btn('Import job', 'job-import', '', 'btn-primary')}</div>
             <div class="notice" style="margin-top:var(--space-4)">Some job sites block imports. You can always paste the description. We won't sign in to a job site for you.</div>`}
      </div>
      <aside class="col">${right || `<div class="card card-quiet"><p class="text-muted">Nothing read yet. Paste a link and press Import — the assistant's reading appears here, not in a blank form.</p></div>`}</aside>
    </div>
  `);
}

/* =========================================================
   P05 — job detail
   ========================================================= */
function activityTab(a) {
  return `<table class="table"><thead><tr><th scope="col">When</th><th scope="col">Event</th></tr></thead><tbody>
    ${a.activity.map((e) => `<tr><td class="num">${esc(e.when)}</td><td>${esc(e.what)} <span class="row-sub">· ${esc(e.who)}</span></td></tr>`).join('')}
    <tr><td>—</td><td>${a.applied ? 'Submitted ' + esc(a.applied.date) : 'No application submitted yet'}</td></tr>
  </tbody></table>
  <p class="text-muted" style="margin-top:var(--space-3)">Events are appended, never overwritten. This records what happened — it is not a message inbox.</p>`;
}

function jobPostingTab(a) {
  return `<div class="card">
    <p class="text-muted">${a.sourceDomain ? esc(a.sourceDomain) + ' · ' : ''}Imported ${esc(a.importedAt)} · Saved snapshot</p>
    <label class="field-label" for="jobtext">Posting text</label>
    <textarea class="textarea" id="jobtext" style="min-height:280px">${esc(a.jobText)}</textarea>
    <div class="btn-row" style="margin-top:var(--space-3)">
      ${btn('Save as new snapshot', 'job-text-save', `data-id="${a.id}"`, 'btn-primary')}
      ${btn('Re-import from URL', 'job-reimport', `data-id="${a.id}"`)}
      ${btn('Copy text', 'copy-job', `data-id="${a.id}"`, 'btn-ghost')}
    </div>
    <p class="text-muted" style="margin-top:var(--space-3)">Edits create a new snapshot and mark the previous analysis as out of date. This text is what every fit check and every draft is measured against.</p>
  </div>`;
}

function fitTab(a) {
  if (!a.requirements.length) {
    return `<div class="card"><h2 class="card-title">Not analysed yet</h2><p class="text-muted">Run the fit to see how this posting lines up with your confirmed profile.</p>
      <div class="btn-row" style="margin-top:var(--space-3)">${btn('Analyze this job', 'run-fit', `data-id="${a.id}"`, 'btn-primary')}</div></div>`;
  }
  const list = S.ui.moreReqs ? a.requirements : a.requirements.slice(0, 3);
  const degraded = S.demo.degraded;
  const readBlock = degraded
    ? ai('Assistant · my read', `<p>Your coordination background lines up with the main work described here. This time I could not reliably split the posting into individual requirements.</p>
        <p class="disclaimer">No count and no per-line mapping — you still get the plain-language read.</p>
        <div class="btn-row">${btn('Re-run analysis', 'run-fit', `data-id="${a.id}"`, 'btn-ai btn-sm')}${btn('Read the posting myself', 'tab', `data-id="${a.id}" data-value="posting"`, 'btn-secondary btn-sm')}</div>`)
    : ai('Assistant · my read', `
        <p>Your cross-functional coordination work covers the core of this role. ${openCount(a)} requirement${openCount(a) === 1 ? ' has' : 's have'} no evidence yet: ${a.requirements.filter((r) => r.status !== 'supported').map((r) => esc(r.text.toLowerCase())).join(', ')}. Everything else is either supported by your profile or not stated in the posting.</p>
        <p><strong>What I'd do next:</strong> ${a.unresolved ? 'if you have led anyone — even contractors or interns — add it as a fact and I will re-check. If not, keep it as a gap. It is one line, not a blocker.' : 'Given the gaps are accepted, draft the resume and I will show every change I make.'}</p>
        <div class="btn-row">
          ${a.unresolved ? btn('Add a fact', 'new-fact', `data-id="${a.id}"`, 'btn-ai btn-sm') : ''}
          ${a.unresolved ? btn('Keep as a gap', 'accept-gaps', `data-id="${a.id}"`, 'btn-secondary btn-sm') : btn('Tailor resume', 'tailor', `data-id="${a.id}"`, 'btn-ai btn-sm')}
        </div>
        <p class="disclaimer">Based on this posting and Profile v3. Not a prediction of interview success, and not a hiring decision.</p>`);

  return `<div class="stack">
    ${readBlock}
    <table class="table">
      <thead><tr><th scope="col">Job requirement</th><th scope="col">Your evidence / action</th></tr></thead>
      <tbody>
        ${list.map((r) => `<tr>
          <td>${esc(r.text)}</td>
          <td>${reqChip(r.status)}
            <p style="margin:var(--space-2) 0 0">${esc(r.note)} ${r.status === 'supported' ? '· <a data-action="show-source" data-id="' + a.id + '">View source</a>' : '· <a data-action="new-fact" data-id="' + a.id + '">Add a fact</a>'}</p>
          </td></tr>`).join('')}
      </tbody>
    </table>
    ${a.requirements.length > 3 ? `<div class="btn-row">${btn(S.ui.moreReqs ? 'Show fewer requirements' : 'Show all ' + a.requirements.length + ' requirements', 'toggle-reqs')}</div>` : ''}
  </div>`;
}

function askPanel(a) {
  const asked = S.ui.asked;
  let answer = '';
  if (asked) {
    answer = `<div class="notice" style="margin-top:var(--space-3)">${esc(asked.answer)}${asked.line ? ' <a data-action="show-source" data-id="' + a.id + '">Show the line</a>' : ''}
      ${asked.unknown ? '<br><span class="text-muted">I can only answer from this posting and your profile.</span>' : ''}</div>`;
  }
  return ai('Ask about this job', `
    <label class="field-label" for="ask" style="margin-top:0">Your question</label>
    <input class="input" id="ask" value="${esc(S.ui.askInput)}" placeholder="Does this posting require sponsorship?">
    <div class="btn-row" style="margin-top:var(--space-3)">
      ${btn('Ask', 'ask', `data-id="${a.id}"`, 'btn-primary btn-sm')}
      ${btn('Team size?', 'ask-quick', `data-id="${a.id}" data-q="What is the team size?"`, 'btn-ghost btn-sm')}
      ${btn('Culture?', 'ask-quick', `data-id="${a.id}" data-q="What is the company culture like?"`, 'btn-ghost btn-sm')}
    </div>
    ${answer}
    <p class="disclaimer">Answers use only this posting and your profile. Not a general chat, and it cannot change anything.</p>`);
}

function renderJob(id) {
  const a = appById(id);
  if (!a) return shell('applications', '<div class="card">Application not found.</div>');
  const tab = S.ui.jobTab || 'fit';
  const body = tab === 'posting' ? jobPostingTab(a) : tab === 'activity' ? activityTab(a) : fitTab(a);

  return shell('applications', `
    <div class="page-head">
      <div>
        <a data-action="nav" data-route="applications">Applications</a> <span class="text-muted">/ ${esc(a.company)}</span>
        <h1 class="page-title" style="margin-top:var(--space-3)">${esc(a.title)}</h1>
        <p class="page-sub" style="margin:0">${esc(a.company)} · ${esc(a.location)} · ${esc(a.arrangement)}${a.employment ? ' · ' + esc(a.employment) : ''}</p>
        <p class="text-muted" style="margin-top:var(--space-2)">Imported <span class="num">${esc(a.importedAt)}</span> · ${a.deadline ? 'Closes ' + esc(a.deadline) : 'Deadline not stated'} · ${a.sourceUrl ? '<a data-action="open-posting" data-id="' + a.id + '">Original posting</a>' : '<span class="text-muted">No source URL (pasted text)</span>'}</p>
      </div>
      <div class="btn-row">
        ${chip(a.status === 'ready' ? 'success' : 'neutral', statusLabel(a.status))}
        ${btn('Update status', 'open-d01', `data-id="${a.id}"`, 'btn-ghost')}
        ${a.draft ? btn(a.status === 'drafting' ? 'Continue draft' : 'Open documents', 'nav', `data-route="documents" data-id="${a.id}"`, 'btn-secondary') : btn('Tailor resume', 'tailor', `data-id="${a.id}"`, 'btn-primary')}
      </div>
    </div>
    <div class="tabs">
      <button class="${tab === 'fit' ? 'on' : ''}" data-action="tab" data-id="${a.id}" data-value="fit">Fit</button>
      <button class="${tab === 'posting' ? 'on' : ''}" data-action="tab" data-id="${a.id}" data-value="posting">Job posting</button>
      <button class="${tab === 'activity' ? 'on' : ''}" data-action="tab" data-id="${a.id}" data-value="activity">Activity</button>
    </div>
    <div class="grid-2">
      <div class="col">${body}</div>
      <aside class="col stack">
        ${askPanel(a)}
        <div class="card">
          <h2 class="card-title">What I could not determine</h2>
          <ul class="checklist muted-list">
            <li>Visa sponsorship: ${a.jobText.toLowerCase().indexOf('sponsor') >= 0 ? 'mentioned in the posting' : 'not stated in the posting'}</li>
            <li>Company culture: not researched — I only read this posting</li>
            <li>Work arrangement: ${esc(a.arrangement.toLowerCase())}, matches what you told me</li>
          </ul>
          ${btn('View exact requirements', 'tab', `data-id="${a.id}" data-value="posting"`, 'btn-secondary btn-sm')}
        </div>
        <div class="card">
          <h2 class="card-title">Your decision</h2>
          <p class="text-muted">Create a draft, keep this for later, or record an application you made elsewhere. Nothing is submitted for you.</p>
          <div class="btn-row">
            ${btn('Keep saved', 'keep-saved', `data-id="${a.id}"`)}
            ${btn('Mark as applied', 'open-d01', `data-id="${a.id}" data-mode="applied" `)}
          </div>
        </div>
      </aside>
    </div>
  `);
}

/* =========================================================
   P06 — documents
   ========================================================= */
const REWRITES = {
  s: 'Coordinated cross-functional onboarding projects for sales and support.',
  m: 'Coordinated cross-functional onboarding projects across sales and customer support — the same coordination work this role names first.',
  p: 'Kept onboarding projects moving for sales and support teams.'
};

function renderDocuments(id) {
  const a = appById(id);
  if (!a || !a.draft) return shell('applications', '<div class="card">No draft yet. Tailor a resume first.</div>');
  const d = a.draft;
  const p = S.ui.para;

  const coverTab = S.ui.docTab === 'cover';
  const para = (key, text, extra) =>
    `<div class="para ${p === key ? 'sel' : ''}" data-action="sel-para" data-id="${a.id}" data-value="${key}">
      ${S.ui.editPara === key
        ? `<textarea class="textarea" id="para-edit" style="min-height:80px">${esc(text)}</textarea>
           <div class="btn-row" style="margin-top:var(--space-2)">${btn('Save my wording', 'para-save', `data-id="${a.id}" data-value="${key}"`, 'btn-primary btn-sm')}${btn('Cancel', 'para-cancel', '', 'btn-ghost btn-sm')}</div>`
        : `${esc(text)} ${extra || ''}`}
    </div>`;

  let aside = `<div class="card card-quiet"><p class="text-muted">Select a paragraph in the document to see what the assistant changed and what you can do with it.</p></div>`;
  if (p) {
    aside = `<div class="ai-block">
        <span class="ai-label">Why I changed this</span>
        <p><strong>Source:</strong> ${p === 'summary' ? 'Profile v3 · Experience / Northstar' : 'Profile v3 · Experience / Northstar / bullet 1'}</p>
        <p>${p === 'summary' ? 'Reworded to lead with operations work, because the posting names cross-functional coordination first.' : 'Reordered this line to the top of Experience, for the same reason.'}</p>
        <div class="btn-row">${btn('Keep change', 'keep-change', '', 'btn-ai btn-sm')}${btn('Restore original', 'restore', `data-id="${a.id}" data-value="${p}"`)}</div>
      </div>
      <div class="card">
        <h2 class="card-title">Rewrite this paragraph</h2>
        <p class="text-muted">Applies to the paragraph you selected.</p>
        <div class="btn-row">
          ${btn('Make it shorter', 'rewrite', `data-id="${a.id}" data-value="s"`)}
          ${btn('Match this requirement', 'rewrite', `data-id="${a.id}" data-value="m"`)}
          ${btn('Plain language', 'rewrite', `data-id="${a.id}" data-value="p"`)}
          ${btn("I'll write it", 'para-edit', `data-id="${a.id}" data-value="${p}"`, 'btn-ghost')}
        </div>
      </div>`;
  }

  const blocked = a.unresolved;
  const canExport = !blocked && a.checks && a.checks.reviewed;

  return shell('applications', `
    <div class="page-head">
      <div>
        <a data-action="nav" data-route="job" data-id="${a.id}">Job details</a> <span class="text-muted">/ Documents</span>
        <h1 class="page-title" style="margin-top:var(--space-3)">${esc(a.company)} · ${esc(a.title)}</h1>
        <p class="page-sub" style="margin:0">${chip('neutral', statusLabel(a.status))} <span class="text-muted" style="margin-left:var(--space-2)">v${d.version} · ${esc(S.saveState || 'Saved')}</span></p>
      </div>
      <div class="btn-row">${btn(blocked ? 'Resolve 1 item first' : 'Review & export', 'export', `data-id="${a.id}"`, 'btn-primary')} ${blocked ? '' : ''}</div>
    </div>

    <div class="tabs">
      <button class="${coverTab ? '' : 'on'}" data-action="doc-tab" data-value="resume">Resume</button>
      <button class="${coverTab ? 'on' : ''}" data-action="doc-tab" data-value="cover">${d.cover ? 'Cover letter' : '+ Add cover letter'}</button>
      <span style="flex:1"></span>
      <button data-action="version-history" style="margin-left:auto">Version history</button>
    </div>

    ${coverTab ? renderCoverTab(a) : `
    <div class="grid-2">
      <div class="col">
        <div class="doc">
          <h1>Alex Morgan</h1>
          <p class="text-muted" style="font-family:var(--font-ui);font-size:var(--text-caption)">Austin, TX · alex@example.com</p>
          <h2>Summary</h2>
          ${para('summary', d.summary, '<span class="text-muted">[View changes]</span>')}
          <h2>Experience</h2>
          <p><strong>Operations Specialist · Northstar Co.</strong><br><span class="num">Jan 2022 – Present</span></p>
          ${d.bullets.map((b, idx) => para('b' + idx, b, idx === 0 ? '<span class="text-muted">[View changes]</span>' : '')).join('')}
          <h2>Skills</h2>
          <p>${S.profile.skills.length ? esc(S.profile.skills.join(' · ')) : '<span class="text-muted">No skills confirmed yet — add them in My profile.</span>'}</p>
        </div>
        <div class="card" style="margin-top:var(--space-4)">
          <label style="display:flex;gap:var(--space-3);align-items:flex-start;font-size:var(--text-sm)">
            <input type="checkbox" data-action="review-check" data-id="${a.id}" ${a.checks && a.checks.reviewed ? 'checked' : ''}>
            <span>I have reviewed this version for accuracy. <span class="text-muted">Changes after review require another check.</span></span>
          </label>
        </div>
      </div>
      <aside class="col stack">
        ${blocked ? `<div class="notice notice-warn">
            <strong>1 item needs your review</strong>
            Direct people management is claimed nowhere, but the posting asks for it. Add evidence or accept the gap — export stays disabled until you decide.
            <div class="btn-row" style="margin-top:var(--space-3)">${btn('Add supporting fact', 'new-fact', `data-id="${a.id}"`, 'btn-primary btn-sm')}${btn('Accept the gap', 'accept-gaps', `data-id="${a.id}"`, 'btn-sm')}</div>
          </div>` : ''}
        ${aside}
        <div class="card">
          <h2 class="card-title">Change log · v${d.version}</h2>
          ${d.changes.length ? `<ul class="checklist">${d.changes.map((c) => `<li class="done">${esc(c.text)}<br><span class="text-muted">${esc(c.reason)}</span></li>`).join('')}</ul>` : '<p class="text-muted">No changes recorded yet.</p>'}
        </div>
        <div class="card">
          <h2 class="card-title">Review status</h2>
          <ul class="checklist">
            <li class="done">Draft complete</li>
            <li class="done">Automated review complete</li>
            <li class="${a.checks && a.checks.reviewed ? 'done' : 'attention'}">Your review: ${a.checks && a.checks.reviewed ? 'done' : 'pending'}</li>
          </ul>
          <p class="text-muted" style="margin-top:var(--space-3)">Automated checks can miss mistakes. Review dates, names, skills and achievements.</p>
        </div>
      </aside>
    </div>`}
  `);
}

function renderCoverTab(a) {
  const d = a.draft;
  if (d.coverFailed) {
    return `<div class="notice notice-warn"><strong>The cover letter failed</strong>Your resume is saved and unaffected. Retrying the failed step does not use another draft credit.
      <div class="btn-row" style="margin-top:var(--space-3)">${btn('Retry letter', 'retry-cover', `data-id="${a.id}"`, 'btn-primary btn-sm')}${btn('Remove it', 'remove-cover', `data-id="${a.id}"`, 'btn-sm')}</div></div>`;
  }
  if (!d.cover) {
    return `<div class="card" style="max-width:620px">
      <h2 class="card-title">Add a cover letter</h2>
      <p class="text-muted">Optional, and only when a posting asks for one. It uses the same confirmed profile, and keeps its own version, checks and failure state — a failed letter never affects your resume.</p>
      <div class="btn-row" style="margin-top:var(--space-3)">${btn('Generate cover letter', 'gen-cover', `data-id="${a.id}"`, 'btn-primary')}</div>
    </div>`;
  }
  return `<div class="grid-2">
    <div class="col">
      <div class="doc">
        <p>Dear Hiring Manager,</p>
        <div class="para ${S.ui.para === 'cover1' ? 'sel' : ''}" data-action="sel-para" data-id="${a.id}" data-value="cover1">${esc(d.cover.body)} <span class="text-muted">[View changes]</span></div>
        <p>Sincerely,<br>Alex Morgan</p>
      </div>
    </div>
    <aside class="col stack">
      ${ai('Why I changed this', `<p>Opened with the onboarding programme you owned, because the posting lists it as a core responsibility.</p>
        <div class="btn-row">${btn('Keep change', 'keep-change', '', 'btn-ai btn-sm')}${btn('Restore original', 'restore', `data-id="${a.id}" data-value="cover1"`)}</div>`)}
      <div class="card"><h2 class="card-title">Checks for the letter</h2>
        <ul class="checklist"><li class="done">Exactly 1 page</li><li class="done">PDF text is extractable</li></ul>
      </div>
    </aside>
  </div>`;
}

/* =========================================================
   P07 — review & export
   ========================================================= */
function renderExport(id) {
  const a = appById(id);
  if (!a || !a.draft) return shell('applications', '<div class="card">Nothing to export yet.</div>');
  const fail = S.demo.partial || a.checks.pdfFail;
  const checks = fail
    ? `<div class="card"><h2 class="card-title">Checks for v${a.draft.version}</h2>
        <ul class="checklist">
          <li class="done">Required contact text present</li>
          <li class="done">Facts confirmed by you</li>
          <li class="attention">PDF text is extractable — <strong>failed on page 2</strong></li>
        </ul>
        <div class="notice notice-warn" style="margin-top:var(--space-3)"><strong>Why it failed</strong>Text on page 2 cannot be extracted — usually a text box or an image instead of real text. The assistant explains the cause and offers the smallest fix. It never marks the file Ready.
          <div class="btn-row" style="margin-top:var(--space-3)">${btn('Show me that section', 'download', `data-kind="fix"`, 'btn-primary btn-sm')}${btn('Download DOCX instead', 'download', `data-kind="docx"`, 'btn-sm')}</div>
        </div>
        <p class="text-muted" style="margin-top:var(--space-3)">DOCX is allowed as a fallback, but the PDF stays marked as not passed.</p>
      </div>`
    : `<div class="card"><h2 class="card-title">Checks for v${a.draft.version}</h2>
        <ul class="checklist">
          <li class="done">Required contact text present</li>
          <li class="done">PDF text is extractable</li>
          <li class="done">No detected page overflow</li>
          <li class="done">Facts confirmed by you</li>
        </ul>
        <p class="text-muted" style="margin-top:var(--space-3)">These checks do not guarantee an ATS result or an interview.</p>
      </div>`;

  return shell('applications', `
    <div class="page-head">
      <div>
        <a data-action="nav" data-route="documents" data-id="${a.id}">Documents</a> <span class="text-muted">/ Review &amp; export</span>
        <h1 class="page-title" style="margin-top:var(--space-3)">${fail ? 'Your resume needs one fix' : 'Your resume is ready to download'}</h1>
        <p class="page-sub" style="margin:0">${esc(a.company)} · ${chip(a.applied ? 'neutral' : 'neutral', a.applied ? 'Submitted ' + a.applied.date : 'Not submitted')}</p>
      </div>
      ${btn('Back to editing', 'nav', `data-route="documents" data-id="${a.id}"`, 'btn-ghost')}
    </div>
    <div class="grid-2">
      <div class="col">
        <div class="doc-paper">
          <h3>Resume v${a.draft.version} · 1 page · US Letter</h3>
          <hr style="border:0;border-top:1px solid var(--color-border);margin:var(--space-4) 0">
          <p><strong>Alex Morgan</strong><br><span class="text-muted">Austin, TX · alex@example.com</span></p>
          <p><strong>Summary</strong><br>${esc(a.draft.summary)}</p>
          <p><strong>Experience</strong><br>Operations Specialist · Northstar Co. · <span class="num">Jan 2022 – Present</span></p>
          <p class="text-muted">Page preview region · text-only sketch. A real build renders the actual PDF here.</p>
        </div>
      </div>
      <aside class="col stack">
        ${checks}
        <div class="card">
          <h2 class="card-title">Download</h2>
          <div class="btn-row">
            ${btn('Download resume (PDF)', 'download', `data-kind="pdf"`, 'btn-primary')}
            ${btn('Download resume (DOCX)', 'download', `data-kind="docx"`)}
          </div>
          <p class="text-muted" style="margin-top:var(--space-3)">Cover letter: ${a.draft.cover ? 'ready' : 'not generated'} ${a.draft.cover ? '' : '· ' + 'add it in the editor'}</p>
          ${a.draft.cover ? `<div class="btn-row">${btn('Download cover letter (PDF)', 'download', `data-kind="letter"`)}${btn('Copy text', 'download', `data-kind="copy"`, 'btn-ghost')}</div>` : ''}
          <p class="text-muted" style="margin-top:var(--space-3)">DOCX pagination may vary by editor. Downloading never changes your application status.</p>
        </div>
        <div class="notice">
          <strong>Next: submit it yourself</strong>
          Upload your file on the employer's site. ${a.sourceUrl ? 'Opening the posting does not change your status.' : 'This job was pasted without a URL, so there is no posting to open — submit on the site you found it.'}
          <div class="btn-row" style="margin-top:var(--space-3)">
            ${a.sourceUrl ? btn('Open original posting', 'open-posting', `data-id="${a.id}"`) : ''}
            ${btn('Mark as applied', 'open-d01', `data-id="${a.id}" data-mode="applied"`, 'btn-primary')}
          </div>
        </div>
      </aside>
    </div>
  `);
}

/* =========================================================
   P08 — my profile
   ========================================================= */
function renderProfile() {
  const pr = S.profile;
  const proposed = S.setup.proposed;

  return shell('profile', `
    <div class="page-head">
      <div><h1 class="page-title">My profile</h1><p class="page-sub" style="margin:0">Confirmed facts for future applications.</p></div>
      ${btn('Update from a newer resume', 'profile-update', '', 'btn-secondary')}
    </div>
    <div class="grid-2">
      <div class="col stack">
        ${ai('Assistant', `<p>What do you want to add or fix?</p>
          <div class="btn-row">${btn('Add a role', 'profile-add-role')}${btn('Add skills', 'setup-skills')}${btn('Update from a newer resume', 'profile-update')}</div>`)}
        <div class="composer">
          <input class="input" id="profile-chat" type="text" placeholder="Tell me what changed, in your own words…" aria-label="Tell the assistant what changed">
          ${btn('Send', 'profile-chat-send', '', 'btn-primary')}
        </div>

        ${proposed ? `<div class="card">
          <h2 class="card-title">Proposed changes from the new file</h2>
          <p class="text-muted">Nothing is replaced until you accept it. Facts you confirmed yourself are never overwritten silently.</p>
          ${proposed.map((c) => `<div class="fact">
            <div class="fact-head"><span class="fact-title">${esc(c.field)}</span>${chip('attention', 'Proposed')}</div>
            <div class="fact-body"><span class="text-muted">Now:</span> ${esc(c.before)}<br><span class="text-muted">New file says:</span> ${esc(c.after)}</div>
            <div class="btn-row">${btn('Accept', 'proposal-accept', `data-id="${c.id}"`, 'btn-primary btn-sm')}${btn('Keep current', 'proposal-reject', `data-id="${c.id}"`, 'btn-ghost btn-sm')}</div>
          </div>`).join('')}
        </div>` : ''}

        ${pr.experience.map((e) => `<div class="card">
          <div class="fact-head"><strong>${esc(e.title)} · ${esc(e.company)}</strong>${e.confirmed ? chip('success', 'Confirmed Sep 19') : chip('attention', 'Needs confirmation')}</div>
          <p class="num">${esc(e.dates)}</p>
          <p class="font-reading">${esc(e.text)}</p>
          <p class="text-muted">Source: ${pr.sourceFile ? esc(pr.sourceFile) : 'resume.docx'}${e.editedByUser ? ' · you edited this one' : ''}</p>
          <div class="btn-row">${btn('Edit', 'fact-edit', 'data-kind="e1"')}${btn('View evidence', 'view-evidence', '', 'btn-ghost')}</div>
        </div>`).join('')}

        ${pr.skills.length ? `<div class="card"><div class="fact-head"><strong>Skills</strong>${chip('success', pr.skills.length + ' confirmed')}</div><p>${esc(pr.skills.join(' · '))}</p></div>` : ''}
      </div>

      <aside class="col stack">
        ${profileChecklist()}
        <div class="notice"><strong>Changes affect future work</strong>Existing drafts and submitted files are not changed. Re-analyse or regenerate from a job when you choose.</div>
        <div class="card">
          <h2 class="card-title">Source files</h2>
          <p class="text-muted">resume.docx · uploaded Sep 19, 2026</p>
          <div class="btn-row">${btn('Delete source file', 'delete-source', '', 'btn-ghost')}</div>
          <p class="text-muted" style="margin-top:var(--space-3)">Deleting a source file does not delete the facts you confirmed from it.</p>
        </div>
      </aside>
    </div>
  `);
}

/* =========================================================
   P09 — settings
   ========================================================= */
function renderSettings() {
  const q = S.quota;
  const remaining = Math.max(0, q.total - q.used);
  return shell('settings', `
    <div class="page-head"><div><h1 class="page-title">Settings</h1><p class="page-sub" style="margin:0">Account, usage, and what the assistant can see.</p></div></div>
    <div class="grid-equal">
      <div class="stack">
        <div class="card">
          <h2 class="card-title">Account</h2>
          <p>${esc(S.profile.contact.email)}</p>
          <p class="text-muted">Sign in using an email link.</p>
          <div class="btn-row">${btn('Sign out', 'signout')}</div>
        </div>
        <div class="card">
          <h2 class="card-title">What the assistant can see</h2>
          <p class="font-reading">Each task sends only what it needs: the posting you selected, plus the parts of your profile that relate to it.</p>
          <div class="btn-row">${btn('See the exact fields sent', 'toggle-fields', '', 'btn-ghost btn-sm')}</div>
          ${S.ui.showFields ? `<ul class="checklist" style="margin-top:var(--space-3)">
            <li class="done">This application's posting text</li>
            <li class="done">Contact: name, email, city</li>
            <li class="done">Experience entries marked relevant to this job</li>
            <li class="done">Education and confirmed skills</li>
            <li>Your other applications — <strong>not sent</strong></li>
            <li>Other postings and full history — <strong>not sent</strong></li>
          </ul>` : ''}
        </div>
        <div class="card">
          <h2 class="card-title">Beta usage</h2>
          <p><span class="num">${remaining}</span> of <span class="num">${q.total}</span> draft runs remaining</p>
          <p class="text-muted">Resets Oct 1, 2026. Illustrative quota. Failed runs are not charged. Downloading existing files is not limited by draft quota.</p>
          <div class="btn-row">${btn('Simulate running out', 'demo', 'data-key="quotaOut"', 'btn-ghost btn-sm')}</div>
        </div>
      </div>
      <div class="stack">
        <div class="card">
          <h2 class="card-title">Your data</h2>
          <p class="font-reading">Profile, source files, job postings and application versions are stored in your private workspace.</p>
          <div class="btn-row">${btn('Export my data', 'export-data')}</div>
          <p class="text-muted" style="margin-top:var(--space-3)">A secure download link will appear here when the export is ready.</p>
        </div>
        <div class="card">
          <h2 class="card-title">Deletion</h2>
          <p class="text-muted">Three different scopes, three different confirmations.</p>
          <div class="btn-row">
            ${btn('Delete one application', 'open-d02', 'data-scope="job"')}
            ${btn('Delete a source file', 'open-d02', 'data-scope="file"')}
          </div>
          <hr style="border:0;border-top:1px solid var(--color-border);margin:var(--space-4) 0">
          <div class="btn-row">${btn('Delete account and data', 'open-d02', 'data-scope="account"', 'btn-danger')}</div>
        </div>
      </div>
    </div>
  `);
}

/* =========================================================
   Task overlay (S03 / S04)
   ========================================================= */
function renderTaskOverlay() {
  const root = $('#modal-root');
  if (!S.task) { if (root.dataset.kind === 'task') { root.innerHTML = ''; root.dataset.kind = ''; } return; }
  root.dataset.kind = 'task';
  root.innerHTML = `<div class="overlay"><div class="card">
    <h2 class="card-title">${esc(S.task.title)}</h2>
    <ul class="task-list">
      ${S.task.stages.map((s) => `<li class="${s.state}"><span class="mark">${s.state === 'done' ? '✓' : s.state === 'running' ? '<span class="spinner"></span>' : '·'}</span>${esc(s.text)}</li>`).join('')}
    </ul>
    <div class="btn-row" style="margin-top:var(--space-4)">
      ${btn('Back to applications', 'leave-task')}
      ${btn('Cancel task', 'cancel-task', '', 'btn-ghost')}
    </div>
    <p class="text-muted" style="margin-top:var(--space-3)">You can leave this page — the job stays in Applications. No artificial percentage, and no promised finish time.</p>
  </div></div>`;
}

/* =========================================================
   Modals
   ========================================================= */
function renderModal() {
  const root = $('#modal-root');
  if (root.dataset.kind === 'task' && !S.modal) return;
  if (!S.modal) { root.innerHTML = ''; root.dataset.kind = ''; return; }
  root.dataset.kind = 'modal';
  const m = S.modal;
  const a = m.appId ? appById(m.appId) : null;
  let inner = '';

  if (m.type === 'd01') {
    inner = `<h2 id="modal-title">${m.mode === 'applied' ? 'Mark as applied' : 'Update status'}</h2>
      <p class="modal-sub">Operations Manager · Northstar Co. This records your action. We do not submit anything.</p>
      ${m.mode === 'applied' ? `
        <label class="field-label" for="m-date">Actual submission date</label>
        <input class="input" id="m-date" value="Sep 19, 2026">
        <label class="field-label" for="m-docs">Documents you submitted</label>
        <select class="select" id="m-docs">
          <option>Resume v2</option><option>Another version</option><option>External documents (made elsewhere)</option>
        </select>
        <label class="field-label" for="m-note">Notes <span class="optional">(optional)</span></label>
        <input class="input" id="m-note" value="Applied on employer website">`
      : `<label class="field-label" for="m-status">New status</label>
        <select class="select" id="m-status">
          ${['saved', 'drafting', 'ready', 'interview', 'offer', 'closed'].map((s) => `<option value="${s}" ${a && a.status === s ? 'selected' : ''}>${statusLabel(s)}</option>`).join('')}
        </select>
        <label class="field-label" for="m-edate">Event date</label>
        <input class="input" id="m-edate" value="Sep 24, 2026">
        <label class="field-label" for="m-enote">Note <span class="optional">(optional)</span></label>
        <input class="input" id="m-enote" placeholder="Recruiter screen scheduled">
        <p class="text-muted" style="margin-top:var(--space-3)">History is preserved. Closing requires a reason. Changing a saved date to "unknown" is allowed — we never invent one.</p>`}
      <div class="modal-foot">${btn('Cancel', 'modal-close')}${btn(m.mode === 'applied' ? 'Confirm applied' : 'Save update', m.mode === 'applied' ? 'confirm-applied' : 'confirm-status', `data-id="${m.appId}"`, 'btn-primary')}</div>`;
  }

  if (m.type === 'd02') {
    const scope = m.scope;
    const copy = {
      job: { t: 'Delete this application?', b: 'Removes this application, its posting snapshot, its documents and its history. Other applications are untouched.' },
      file: { t: 'Delete this source file?', b: 'Removes resume.docx. The facts you already confirmed stay in your profile — deleting a file is not the same as deleting your profile.' },
      account: { t: 'Delete account and data', b: 'This removes your profile, source files, job postings, application history and generated documents. Active tasks will stop.' }
    }[scope];
    inner = `<h2 id="modal-title">${esc(copy.t)}</h2>
      <p class="modal-sub">${esc(copy.b)}</p>
      ${scope === 'account' ? `<div class="notice">Export your data first if you need it. Deletion and backup retention timeframes must be confirmed before this ships — they are not promised here.</div>
        <label class="field-label" for="del">Type DELETE to confirm</label>
        <input class="input" id="del" value="${esc(S.ui.confirmDelete)}" placeholder="DELETE">` : ''}
      <div class="modal-foot">${btn(scope === 'account' ? 'Keep account' : 'Cancel', 'modal-close')}${btn(scope === 'account' ? 'Delete account and data' : 'Delete', 'confirm-delete', `data-scope="${scope}"`, 'btn-danger')}</div>`;
  }

  if (m.type === 'd03') {
    inner = `<h2 id="modal-title">Confirm a new fact</h2>
      <p class="modal-sub">This is your statement, not something found in your resume. It will be recorded as your confirmation.</p>
      <label class="field-label" for="fact">The fact</label>
      <textarea class="textarea" id="fact">${esc(S.ui.newFact)}</textarea>
      <label class="field-label">Where should it apply?</label>
      <div class="btn-row">
        <button class="btn ${m.scope === 'job' ? 'btn-primary' : 'btn-secondary'} btn-sm" data-action="modal-scope" data-value="job">Only this application</button>
        <button class="btn ${m.scope === 'profile' ? 'btn-primary' : 'btn-secondary'} btn-sm" data-action="modal-scope" data-value="profile">Also add to My profile</button>
      </div>
      <div class="modal-foot">${btn('Cancel', 'modal-close')}${btn('Save fact', 'confirm-fact', `data-id="${m.appId}"`, 'btn-primary')}</div>`;
  }

  if (m.type === 'tailor') {
    const remaining = Math.max(0, S.quota.total - S.quota.used);
    const blocked = S.demo.quotaOut || remaining <= 0;
    inner = blocked
      ? `<h2 id="modal-title">Draft quota reached</h2>
        <p class="modal-sub">You can still edit, track applications and download existing files.</p>
        <div class="notice">Next reset: Oct 1, 2026 [example]. ${S.demo.quotaOut ? 'This is the simulated "out of quota" state.' : ''}</div>
        <p class="text-muted" style="margin-top:var(--space-3)">No automatic purchase and no hidden charge. Existing files stay downloadable.</p>
        <div class="modal-foot">${btn('Back to applications', 'modal-close')}</div>`
      : `<h2 id="modal-title">Prepare materials</h2>
        <p class="modal-sub">Choose what to generate. Nothing is generated until you confirm.</p>
        <label style="display:flex;gap:var(--space-3);align-items:center;font-size:var(--text-sm);margin-bottom:var(--space-3)">
          <input type="checkbox" checked disabled><span>Resume — required</span></label>
        <label style="display:flex;gap:var(--space-3);align-items:center;font-size:var(--text-sm)">
          <input type="checkbox" data-action="cover-choice" ${S.ui.coverChoice ? 'checked' : ''}><span>Cover letter — optional, only if the posting asks for one</span></label>
        <div class="notice" style="margin-top:var(--space-4)">This will use <strong>1</strong> of your <strong>${remaining}</strong> remaining draft runs. The fit analysis you already ran is free.</div>
        <div class="modal-foot">${btn('Cancel', 'modal-close')}${btn('Generate', 'confirm-tailor', `data-id="${m.appId}"`, 'btn-primary')}</div>`;
  }

  if (m.type === 'duplicate') {
    inner = `<h2 id="modal-title">This job looks familiar</h2>
      <p class="modal-sub">You already added "Operations Manager · Northstar Co." on Sep 14, 2026.</p>
      <div class="notice">Matched on URL first. The same company or title alone is only a possible duplicate — you can always create a separate application.</div>
      <div class="modal-foot">${btn('Open existing', 'dup-open', 'data-id="a1"', 'btn-primary')}${btn('Add separately', 'dup-separate', 'data-url="' + esc(m.url || '') + '"')}</div>`;
  }

  if (m.type === 's11') {
    inner = `<h2 id="modal-title">S11 · the answer isn't in the posting</h2>
      <p class="modal-sub">Shown inline in the Ask panel — reproduced here so you can see the wording on its own.</p>
      <div class="notice">"The posting does not state a team size. I can only answer from this posting and your profile."</div>
      <p class="text-muted" style="margin-top:var(--space-3)">No generic advice, no invented detail, no write actions.</p>
      <div class="modal-foot">${btn('Close', 'modal-close')}</div>`;
  }

  root.innerHTML = `<div class="modal-scrim" data-action="scrim"><div class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-title">${inner}</div></div>`;
}

/* =========================================================
   Toasts
   ========================================================= */
function renderToasts() {
  $('#toast-root').innerHTML = S.toasts.map((t) => `<div class="toast"><span>${esc(t.text)}</span><button data-action="toast-close" data-id="${t.id}" aria-label="Dismiss">×</button></div>`).join('');
}
let toastId = 0;
function toast(text) {
  const id = ++toastId;
  S.toasts.push({ id, text });
  renderToasts();
  setTimeout(() => { S.toasts = S.toasts.filter((t) => t.id !== id); renderToasts(); }, 5200);
}

/* =========================================================
   Demo toolbar
   ========================================================= */
const DEMO_TOGGLES = [
  ['empty', '空态：没有任何申请'],
  ['readFail', 'P04 读取失败（S02）'],
  ['degraded', 'S12 结构化降级'],
  ['partial', 'S04 部分成功 / PDF 检查失败'],
  ['quotaOut', 'S06 额度耗尽'],
  ['expired', 'S07 会话过期']
];
const JUMPS = [
  ['signin', 'P01 登录'], ['setup', 'P02 建立资料'], ['applications', 'P03 工作台'],
  ['new', 'P04 导入职位'], ['job', 'P05 职位适配'], ['documents', 'P06 文档编辑'],
  ['export', 'P07 检查导出'], ['profile', 'P08 主资料'], ['settings', 'P09 设置']
];

function renderToolbar() {
  const el = $('#toolbar');
  el.hidden = !S.ui.toolbar;
  $('.toolbar-toggle').setAttribute('aria-expanded', String(S.ui.toolbar));
  if (!S.ui.toolbar) return;
  el.innerHTML = `
    <h3>跳转页面</h3>
    <div class="tool-list">
      ${JUMPS.map(([r, label]) => {
        const needsId = ['job', 'documents', 'export'].includes(r);
        return `<button data-action="jump" data-route="${r}" ${needsId ? 'data-id="a1"' : ''}>${esc(label)}</button>`;
      }).join('')}
    </div>
    <h3>边缘状态开关</h3>
    <div class="tool-list">
      ${DEMO_TOGGLES.map(([k, label]) => `<button data-action="demo" data-key="${k}" class="${S.demo[k] ? 'on' : ''}">${esc(label)}</button>`).join('')}
    </div>
    <h3>数据</h3>
    <div class="tool-list">
      <button data-action="reset">重置全部状态</button>
      <button data-action="nav" data-route="signin">回到 P01 登录</button>
    </div>
    <p class="toolbar-note">开关只影响演示呈现，不改动你的真实数据。这个面板是评审工具，不是产品的一部分。</p>`;
}

/* =========================================================
   Expired session (S07)
   ========================================================= */
function renderExpired() {
  return `<div class="center-page">
    <div class="card">
      <h2 class="card-title">Your session expired</h2>
      <p class="text-muted">You were signed out, or the connection dropped.</p>
      <p class="font-reading">Your profile, drafts and files are saved on the server. Only text typed after the last successful save may be lost.</p>
      <div class="btn-row" style="margin-top:var(--space-4)">
        ${btn('Sign in again', 'demo', 'data-key="expired"', 'btn-primary')}
      </div>
      <p class="text-muted" style="margin-top:var(--space-3)">A signed-out visitor never sees cached resume or job content.</p>
    </div>
  </div>`;
}

/* =========================================================
   Render root
   ========================================================= */
function render() {
  if (S.demo.expired) {
    $('#app').innerHTML = renderExpired();
    renderModal(); renderToasts(); renderToolbar(); renderTaskOverlay();
    return;
  }
  const r = parseRoute();
  let html;
  switch (r.name) {
    case 'setup': html = renderSetup(); break;
    case 'applications': html = renderApplications(); break;
    case 'new': html = renderNewJob(); break;
    case 'job': html = renderJob(r.id || 'a1'); break;
    case 'documents': html = renderDocuments(r.id || 'a1'); break;
    case 'export': html = renderExport(r.id || 'a1'); break;
    case 'profile': html = renderProfile(); break;
    case 'settings': html = renderSettings(); break;
    default: html = renderSignin();
  }
  $('#app').innerHTML = html;
  renderModal(); renderToasts(); renderToolbar(); renderTaskOverlay();
}

/* =========================================================
   Task runner
   ========================================================= */
async function runTask(title, stages, ms) {
  S.task = { title, stages: stages.map((t) => ({ text: t, state: 'pending' })) };
  renderTaskOverlay();
  for (let i = 0; i < S.task.stages.length; i++) {
    S.task.stages[i].state = 'running';
    renderTaskOverlay();
    await wait(ms || 850);
    S.task.stages[i].state = 'done';
    renderTaskOverlay();
  }
  await wait(320);
  S.task = null;
}

/* =========================================================
   Ask engine (deliberately limited — see 02 §6.5)
   ========================================================= */
function answerQuestion(q, a) {
  const s = q.toLowerCase();
  const has = (w) => s.indexOf(w) >= 0;
  if (has('sponsor') || has('visa') || has('authoriz')) {
    return { answer: '"No — it says you must be authorized to work in the US, and sponsorship is not mentioned anywhere."', line: true };
  }
  if (has('team size') || has('how many people') || has('manage a team')) {
    return { answer: '"The posting says you would manage a team of 5 operations associates. It does not say the current team size."', line: true };
  }
  if (has('remote') || has('hybrid') || has('onsite') || has('on-site')) {
    return { answer: '"The posting lists Austin, TX · Hybrid · Full-time."', line: true };
  }
  if (has('culture') || has('review') || has('glassdoor') || has('salary') || has('pay')) {
    return { answer: '"The posting does not state this, and I have not researched anything outside the posting."', unknown: true };
  }
  return { answer: '"I could not find that in this posting or in your profile."', unknown: true };
}

/* =========================================================
   Actions
   ========================================================= */
document.addEventListener('click', async (e) => {
  const target = e.target.closest('[data-action]');
  if (!target) return;
  const act = target.dataset.action;
  const id = target.dataset.id;
  const a = id ? appById(id) : null;

  /* ---- navigation ---- */
  if (act === 'nav') { if (target.dataset.route === 'job' || target.dataset.route === 'documents' || target.dataset.route === 'export') go(target.dataset.route, target.dataset.id || 'a1'); else go(target.dataset.route); render(); return; }
  if (act === 'jump') { go(target.dataset.route, target.dataset.id); S.ui.toolbar = false; render(); return; }
  if (act === 'open-app') { go(a && a.draft ? 'documents' : 'job', id); render(); return; }

  /* ---- demo ---- */
  if (act === 'toolbar') { S.ui.toolbar = !S.ui.toolbar; renderToolbar(); return; }
  if (act === 'demo') {
    const k = target.dataset.key;
    S.demo[k] = !S.demo[k];
    toast(`${target.textContent.trim()} → ${S.demo[k] ? 'on' : 'off'}`);
    render(); return;
  }
  if (act === 'reset') { S = seedState(); location.hash = '#/signin'; render(); return; }
  if (act === 'scrim' && e.target.classList.contains('modal-scrim')) { S.modal = null; render(); return; }
  if (act === 'modal-close') { S.modal = null; render(); return; }
  if (act === 'toast-close') { S.toasts = S.toasts.filter((t) => String(t.id) !== String(target.dataset.id)); renderToasts(); return; }

  /* ---- P01 ---- */
  if (act === 'signin-send') { S.email = ($('#email') || {}).value || ''; if (!S.email) { toast('Enter an email first.'); return; } S.signinSent = true; render(); return; }
  if (act === 'signin-change') { S.signinSent = false; render(); return; }
  if (act === 'signin-resend') { toast('Link resent to ' + (S.email || 'you@example.com')); return; }
  if (act === 'signin-open') { go(S.profile.contact.confirmed ? 'applications' : 'setup'); render(); return; }
  if (act === 'signout') { S.signinSent = false; go('signin'); render(); return; }

  /* ---- P02 ---- */
  if (act === 'setup-attach') {
    S.setup.attached = true; S.setup.reading = true; S.profile.sourceFile = 'resume.docx'; render();
    await wait(1200);
    S.setup.reading = false; S.setup.extracted = true; S.saveState = 'Saved'; render(); return;
  }
  if (act === 'setup-paste') { S.setup.pasteMode = 'paste'; render(); return; }
  if (act === 'setup-type') { S.setup.pasteMode = 'type'; render(); return; }
  if (act === 'setup-cancel') { S.setup.pasteMode = null; S.setup.paste = ''; render(); return; }
  if (act === 'setup-extract') {
    const v = ($('#paste-box') || {}).value || '';
    if (!v.trim()) { toast('Paste or type something first.'); return; }
    S.setup.paste = v; S.setup.attached = true; S.setup.reading = true; S.setup.pasteMode = null; render();
    await wait(1100);
    S.setup.reading = false; S.setup.extracted = true; render(); return;
  }
  if (act === 'fact-edit') { S.ui.editId = target.dataset.kind; render(); return; }
  if (act === 'fact-cancel') { S.ui.editId = null; render(); return; }
  if (act === 'fact-save') {
    const kind = target.dataset.kind;
    if (kind === 'contact') {
      S.profile.contact = { name: ($('#c-name') || {}).value || '', email: ($('#c-email') || {}).value || '', city: ($('#c-city') || {}).value || '', confirmed: true };
    } else if (kind === 'e1') {
      const ex = S.profile.experience[0];
      ex.company = ($('#e-company') || {}).value || ''; ex.title = ($('#e-title') || {}).value || '';
      ex.dates = ($('#e-dates') || {}).value || ''; ex.text = ($('#e-text') || {}).value || '';
      ex.confirmed = true; ex.editedByUser = true;
    } else {
      const ed = S.profile.education[0];
      ed.degree = ($('#ed-degree') || {}).value || ''; ed.field = ($('#ed-field') || {}).value || ''; ed.confirmed = true;
    }
    S.ui.editId = null; S.saveState = 'Saved · just now';
    toast(target.dataset.kind === 'contact' ? 'Contact confirmed' : 'Saved — recorded as your own wording');
    render(); return;
  }
  if (act === 'fact-confirm') {
    const kind = target.dataset.kind;
    if (kind === 'contact') S.profile.contact.confirmed = true;
    else if (kind === 'e1') S.profile.experience[0].confirmed = true;
    else S.profile.education[0].confirmed = true;
    S.saveState = 'Saved · just now';
    toast('Confirmed — recorded as your statement, not a claim from the file');
    render(); return;
  }
  if (act === 'fact-remove') { S.profile.experience = []; toast('Removed'); render(); return; }
  if (act === 'setup-skills') { S.profile.skills = ['Project coordination', 'Reporting', 'Onboarding']; toast('3 skills added — edit them in My profile'); render(); return; }
  if (act === 'setup-role') { S.profile.experience.push({ id: 'e2', title: 'Program Assistant', company: 'Demo Group', dates: '2019 – 2021', text: 'Supported programme scheduling and reporting.', confirmed: true, editedByUser: false }); toast('Second role added'); render(); return; }
  if (act === 'chat-send' || act === 'profile-chat-send') {
    const sel = act === 'chat-send' ? '#chat-input' : '#profile-chat';
    const v = ($(sel) || {}).value || '';
    if (!v.trim()) return;
    S.ui.newFact = v; S.modal = { type: 'd03', appId: null, scope: 'profile' }; render(); return;
  }
  if (act === 'setup-finish') { go(S.apps.length ? 'applications' : 'new'); render(); return; }
  if (act === 'focus-waiting') { toast('Jump to the item marked with ! in the assistant panel'); return; }

  /* ---- P03 ---- */
  if (act === 'filter') { S.ui.filter = target.dataset.value; render(); return; }

  /* ---- P04 ---- */
  if (act === 'tab-import') { S.imp.pasted = target.dataset.value === 'paste' ? ($('#pd') || {}).value || '' : ''; render(); return; }
  if (act === 'job-import' || act === 'job-retry') {
    S.imp.url = ($('#job-url') || {}).value || S.imp.url;
    if (S.demo.readFail) { S.imp.error = true; S.imp.read = null; S.imp.reading = false; render(); return; }
    S.imp.error = false; S.imp.reading = true; render();
    await wait(1300);
    S.imp.reading = false;
    S.imp.read = { title: 'Operations Manager', company: 'Northstar Co.', location: 'Austin, TX', arrangement: 'Hybrid', employment: 'Full-time', domain: 'careers.example.com', when: 'Sep 19, 2026', count: 9, notStated: ['Deadline', 'Salary', 'Visa sponsorship', 'Team size'] };
    render(); return;
  }
  if (act === 'job-paste') {
    const txt = ($('#paste-fallback') || $('#pd') || {}).value || '';
    if (!txt.trim()) { toast('Paste the description first.'); return; }
    S.imp.error = false;
    S.imp.read = { title: 'Operations Manager', company: 'Northstar Co.', location: 'Not stated', arrangement: 'Not stated', employment: '', domain: 'pasted text', when: 'Sep 19, 2026', count: 9, notStated: ['Deadline', 'Salary', 'Visa sponsorship', 'Team size', 'Location'] };
    toast('Read from pasted text');
    render(); return;
  }
  if (act === 'job-edit-line') { toast('Every extracted line is editable — fields keep visible labels.'); return; }
  if (act === 'job-edit-text') { toast('Opening the full posting text for editing.'); return; }
  if (act === 'job-save') {
    const dup = S.apps.find((x) => x.sourceUrl && x.sourceUrl === S.imp.url);
    if (dup) { S.modal = { type: 'duplicate', url: S.imp.url }; render(); return; }
    await createAndAnalyze();
    return;
  }
  if (act === 'dup-open') { S.modal = null; go('job', 'a1'); render(); return; }
  if (act === 'dup-separate') { S.modal = null; await createAndAnalyze(); return; }

  /* ---- P05 ---- */
  if (act === 'tab') { S.ui.jobTab = target.dataset.value; render(); return; }
  if (act === 'toggle-reqs') { S.ui.moreReqs = !S.ui.moreReqs; render(); return; }
  if (act === 'run-fit') {
    await runTask('Analysing this posting', ['Reading the posting', 'Comparing it with your confirmed profile', 'Writing the fit summary']);
    a.requirements = reqsFor('full'); a.unresolved = true; a.status = a.status === 'saved' ? 'saved' : a.status;
    a.activity.push({ when: 'Sep 19, 2026', what: 'Fit analysis completed', who: 'System' });
    toast('Analysis done — 6 of 9 requirements have evidence');
    render(); return;
  }
  if (act === 'new-fact') { S.modal = { type: 'd03', appId: id, scope: 'job' }; render(); return; }
  if (act === 'modal-scope') { S.modal.scope = target.dataset.value; render(); return; }
  if (act === 'confirm-fact') {
    const v = ($('#fact') || {}).value || '';
    if (!v.trim()) { toast('Describe the fact first.'); return; }
    const scope = S.modal.scope;
    if (scope === 'profile') S.profile.experience.push({ id: 'e' + Date.now(), title: v.slice(0, 40), company: 'Added by you', dates: 'Dates unknown', text: v, confirmed: true, editedByUser: true });
    S.modal = null;
    if (a) {
      a.requirements = a.requirements.map((r) => (r.status !== 'supported' && (r.id === 'r2' || r.id === 'r8') ? { ...r, status: 'supported', note: 'Added by you on Sep 19, 2026' } : r));
      a.unresolved = false;
      a.activity.push({ when: 'Sep 19, 2026', what: 'Fact added: ' + v.slice(0, 40), who: 'You · ' + (scope === 'profile' ? 'also saved to profile' : 'only this application') });
    }
    toast('Fact saved — ' + (scope === 'profile' ? 'also added to My profile' : 'this application only'));
    render(); return;
  }
  if (act === 'accept-gaps') { a.unresolved = false; a.activity.push({ when: 'Sep 19, 2026', what: 'Gaps accepted as they are', who: 'You' }); toast('Gaps accepted — you can still address them in the cover letter'); render(); return; }
  if (act === 'keep-saved') { a.status = 'saved'; toast('Kept as Saved'); render(); return; }
  if (act === 'show-source') { toast('Evidence panel: the exact line from your profile is highlighted.'); return; }
  if (act === 'open-posting') { toast('Would open the employer site in a new tab. Your status is unchanged.'); return; }
  if (act === 'copy-job') { toast('Posting text copied.'); return; }
  if (act === 'job-text-save') { a.activity.push({ when: 'Sep 19, 2026', what: 'Posting text edited — new snapshot', who: 'You' }); toast('New snapshot saved — the previous analysis is now marked out of date'); render(); return; }
  if (act === 'job-reimport') { toast('Re-importing would create another snapshot. The current one is kept.'); return; }

  /* ---- Ask ---- */
  if (act === 'ask' || act === 'ask-quick') {
    const q = act === 'ask-quick' ? target.dataset.q : (($('#ask') || {}).value || '');
    if (!q.trim()) { toast('Type a question first.'); return; }
    S.ui.askInput = q;
    S.ui.asked = answerQuestion(q, a);
    render(); return;
  }

  /* ---- Tailor / documents ---- */
  if (act === 'tailor') { S.modal = { type: 'tailor', appId: id }; render(); return; }
  if (act === 'cover-choice') { S.ui.coverChoice = target.checked; return; }
  if (act === 'confirm-tailor') {
    const wantCover = S.ui.coverChoice;
    S.modal = null;
    S.quota.used++;
    S.saveState = 'Saving…';
    await runTask('Preparing your resume', ['Drafting from your confirmed profile', 'Reviewing every claim against your profile', 'Checking the document output']);
    a.draft = a.draft || { version: 0, summary: '', bullets: [], userEdited: false, cover: null, coverFailed: false, changes: [] };
    a.draft.version++;
    a.draft.summary = 'Operations professional with experience coordinating cross-functional onboarding projects.';
    a.draft.bullets = ['Coordinated onboarding projects across sales and customer support.', 'Built weekly reporting used by three teams to track onboarding progress.'];
    a.draft.changes = [
      { text: 'Summary reworded to lead with operations work', reason: 'The posting names cross-functional coordination first.' },
      { text: 'Bullet 1 moved up under Experience', reason: 'Closest match to the core requirement.' },
      { text: 'Removed "detail-oriented"', reason: 'No evidence in your profile, so it was dropped rather than invented.' }
    ];
    if (wantCover) {
      if (S.demo.partial) { a.draft.cover = null; a.draft.coverFailed = true; }
      else { a.draft.cover = { body: 'I am applying for the Operations Manager role at Northstar Co. In my current role I owned the onboarding programme for new clients and built the reporting three teams relied on.' }; a.draft.coverFailed = false; }
    }
    a.checks = a.checks || { contact: true, extractable: true, overflow: true, reviewed: false, pdfFail: false };
    a.checks.reviewed = false;
    if (a.status === 'saved') a.status = 'drafting';
    a.activity.push({ when: 'Sep 19, 2026', what: 'Resume draft v' + a.draft.version + ' created', who: 'You' });
    S.saveState = 'Saved';
    go('documents', a.id);
    render();
    if (a.draft.coverFailed) toast('Resume is ready. The cover letter failed — retry it without using another credit.');
    return;
  }
  if (act === 'doc-tab') { S.ui.docTab = target.dataset.value; S.ui.para = null; render(); return; }
  if (act === 'sel-para') { S.ui.para = S.ui.para === target.dataset.value ? null : target.dataset.value; S.ui.editPara = null; render(); return; }
  if (act === 'keep-change') { toast('Kept. The change log will show it as accepted by you.'); return; }
  if (act === 'restore') { toast('Restored the previous wording for this paragraph.'); render(); return; }
  if (act === 'rewrite') {
    const mode = target.dataset.value;
    if (S.ui.para === 'summary') a.draft.summary = mode === 'p' ? 'Operations professional who keeps onboarding projects moving.' : mode === 'm' ? 'Operations professional with cross-functional coordination experience, matching the posting\'s first requirement.' : 'Operations professional with cross-functional coordination experience.';
    else { const i = Number((S.ui.para || 'b0').replace('b', '')) || 0; a.draft.bullets[i] = REWRITES[mode]; }
    a.draft.changes.push({ text: 'Paragraph rewritten (' + ({ s: 'shorter', m: 'matched to a requirement', p: 'plain language' }[mode]) + ')', reason: 'You asked for this on the selected paragraph.' });
    a.checks.reviewed = false;
    toast('Rewritten — review again before export');
    render(); return;
  }
  if (act === 'para-edit') { S.ui.editPara = S.ui.para; render(); return; }
  if (act === 'para-cancel') { S.ui.editPara = null; render(); return; }
  if (act === 'para-save') {
    const v = ($('#para-edit') || {}).value || '';
    const key = target.dataset.value;
    if (key === 'summary') a.draft.summary = v; else { const i = Number(key.replace('b', '')) || 0; a.draft.bullets[i] = v; }
    a.draft.userEdited = true;
    a.draft.changes.push({ text: 'You edited this paragraph yourself', reason: 'Your wording is stored separately and AI rewrites will not overwrite it.' });
    a.checks.reviewed = false; S.ui.editPara = null;
    toast('Saved as your wording');
    render(); return;
  }
  if (act === 'gen-cover') {
    await runTask('Writing your cover letter', ['Reading the posting', 'Drafting one page', 'Checking length and facts']);
    a.draft.cover = { body: 'I am applying for the Operations Manager role at Northstar Co. In my current role I owned the onboarding programme for new clients and built the reporting three teams relied on.' };
    a.draft.coverFailed = false; toast('Cover letter generated — one page'); render(); return;
  }
  if (act === 'retry-cover') {
    await runTask('Retrying the cover letter', ['Retrying only the failed step']);
    a.draft.cover = { body: 'I am applying to Northstar Co. for the Operations Manager role.' };
    a.draft.coverFailed = false; toast('Retried — no extra draft credit used'); render(); return;
  }
  if (act === 'remove-cover') { a.draft.cover = null; a.draft.coverFailed = false; S.ui.docTab = 'resume'; toast('Cover letter removed'); render(); return; }

  /* ---- P07 ---- */
  if (act === 'review-check') { a.checks.reviewed = target.checked; S.saveState = target.checked ? 'Saved' : 'Saved · unsaved review state'; render(); return; }
  if (act === 'export') {
    if (a.unresolved) { toast('Resolve the flagged item first — export stays disabled until you decide.'); return; }
    if (!a.checks.reviewed) { toast('Tick "I have reviewed this version" first.'); return; }
    go('export', a.id); render(); return;
  }
  if (act === 'download') {
    const k = target.dataset.kind;
    S.saveState = 'Saved';
    toast(k === 'pdf' ? 'Resume PDF downloaded · status unchanged' : k === 'docx' ? 'DOCX downloaded · the PDF is still marked as not passed' : k === 'letter' ? 'Cover letter PDF downloaded' : k === 'copy' ? 'Cover letter text copied' : k === 'fix' ? 'Scrolled to the section that caused the failure' : 'Downloaded');
    render(); return;
  }
  if (act === 'version-history') { S.modal = { type: 's11' }; toast('Version history: v2 current, v1 from Sep 19. Submitted versions are locked.'); return; }

  /* ---- P08 ---- */
  if (act === 'profile-update') {
    S.setup.proposed = [
      { id: 'p1', field: 'Experience · Operations Specialist', before: 'Jan 2022 – Present', after: 'Jan 2022 – Present · added "led two contractors"' },
      { id: 'p2', field: 'Skills', before: 'Not listed', after: 'Project coordination, Reporting, Vendor management' }
    ];
    toast('New file read — review the proposed changes below');
    render(); return;
  }
  if (act === 'proposal-accept') { S.setup.proposed = S.setup.proposed.filter((c) => c.id !== target.dataset.id); S.profile.skills = ['Project coordination', 'Reporting', 'Vendor management']; toast('Accepted — recorded as your confirmation'); render(); return; }
  if (act === 'proposal-reject') { S.setup.proposed = S.setup.proposed.filter((c) => c.id !== target.dataset.id); toast('Kept your current version'); render(); return; }
  if (act === 'profile-add-role') { S.profile.experience.push({ id: 'e' + Date.now(), title: 'New role', company: '—', dates: 'Dates unknown', text: 'Add the detail here.', confirmed: false, editedByUser: true }); toast('Blank role added — fill it in'); render(); return; }
  if (act === 'view-evidence') { toast('Showing the exact line from the file this fact came from.'); return; }
  if (act === 'delete-source') { S.profile.sourceFile = null; toast('Source file deleted. The facts you confirmed are kept.'); render(); return; }

  /* ---- P09 ---- */
  if (act === 'toggle-fields') { S.ui.showFields = !S.ui.showFields; render(); return; }
  if (act === 'export-data') { toast('Export requested. A secure, expiring download link would appear here.'); return; }
  if (act === 'open-d02') { S.ui.confirmDelete = ''; S.modal = { type: 'd02', scope: target.dataset.scope }; render(); return; }
  if (act === 'confirm-delete') {
    const scope = target.dataset.scope;
    if (scope === 'account') {
      if (S.ui.confirmDelete !== 'DELETE') { toast('Type DELETE exactly to confirm.'); return; }
      S.modal = null; toast('Account deletion confirmed. Export your data first in a real product.'); resetToSignin(); return;
    }
    if (scope === 'job') { S.modal = null; toast('That application and its history would be removed. Others stay.'); render(); return; }
    S.modal = null; S.profile.sourceFile = null; toast('Source file removed. Confirmed facts are kept.'); render(); return;
  }

  /* ---- Task overlay ---- */
  if (act === 'leave-task') { go('applications'); S.task = null; render(); return; }
  if (act === 'cancel-task') { S.task = null; render(); return; }
  if (act === 'open-d01') { S.modal = { type: 'd01', appId: id, mode: target.dataset.mode || 'status' }; render(); return; }
  if (act === 'confirm-applied') {
    const date = ($('#m-date') || {}).value || 'Unknown';
    const docs = ($('#m-docs') || {}).value || 'External documents';
    a.applied = { date, version: docs, note: ($('#m-note') || {}).value || '' };
    a.status = 'applied';
    a.activity.push({ when: date, what: 'Status: ' + statusLabel(a.status) + ' → Applied', who: 'You · ' + docs });
    S.modal = null;
    toast('Recorded as applied. We did not submit anything.');
    render(); return;
  }
  if (act === 'confirm-status') {
    const st = ($('#m-status') || {}).value;
    const d = ($('#m-edate') || {}).value || 'Unknown';
    a.status = st;
    a.activity.push({ when: d, what: 'Status changed to ' + statusLabel(st), who: 'You' });
    S.modal = null; toast('Status updated — history preserved');
    render(); return;
  }
});

/* article fallback: keep resetToSignin defined before use */
function resetToSignin() { S = seedState(); go('signin'); render(); }

async function createAndAnalyze() {
  const read = S.imp.read || {};
  const job = {
    id: 'a' + Date.now(),
    title: read.title || 'Untitled role',
    company: read.company || 'Unknown company',
    location: read.location || 'Not stated',
    arrangement: read.arrangement || 'Not stated',
    employment: read.employment || '',
    deadline: '',
    status: 'saved',
    importedAt: 'Sep 19, 2026',
    sourceUrl: S.imp.url && read.domain !== 'pasted text' ? S.imp.url : '',
    sourceDomain: read.domain || '',
    jobText: read.domain === 'pasted text' ? (S.imp.pasted || JOB_TEXT) : JOB_TEXT,
    requirements: [],
    unresolved: false,
    draft: null,
    checks: null,
    applied: null,
    activity: [{ when: 'Sep 19, 2026', what: read.domain === 'pasted text' ? 'Job added by pasting text' : 'Job imported from URL', who: 'You' }]
  };
  S.apps.unshift(job);
  S.imp = { url: '', reading: false, read: null, error: false, pasted: '' };
  S.ui.jobTab = 'fit'; S.ui.moreReqs = false;
  go('job', job.id);
  render();
  await runTask('Analysing this posting', ['Reading the posting', 'Comparing it with your confirmed profile', 'Writing the fit summary']);
  job.requirements = reqsFor('full');
  job.unresolved = true;
  job.activity.push({ when: 'Sep 19, 2026', what: 'Fit analysis completed', who: 'System' });
  toast('Analysis done — 6 of 9 requirements have evidence');
  render();
}

/* keep modal delete field in sync */
document.addEventListener('input', (e) => {
  if (e.target.id === 'del') S.ui.confirmDelete = e.target.value;
  if (e.target.id === 'ask') S.ui.askInput = e.target.value;
  if (e.target.id === 'fact') S.ui.newFact = e.target.value;
});

window.addEventListener('hashchange', () => { render(); });
render();
