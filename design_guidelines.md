{
  "brand": {
    "name": "Talentiv Jobs",
    "attributes": [
      "bersih & modern (neo-minimal)",
      "skill-first (fokus kompetensi, bukan gelar)",
      "emosional-aspiratif (menguatkan: skill-mu berharga)",
      "tepercaya untuk kandidat & HR",
      "mobile-first, cepat terasa (skeleton + optimistic UI)"
    ],
    "language": "Bahasa Indonesia",
    "icon_system": "lucide-react (minimal, konsisten)"
  },

  "design_tokens": {
    "locked_palette_hex": {
      "forgotten_blue": "#1E2A3A",
      "jungle_teal": "#0D9488",
      "fountain_mint": "#DBF7EF",
      "background": "#F8FAFC",
      "white": "#FFFFFF",
      "gray_200": "#E5E7EB"
    },
    "css_variables_to_set_in_index_css": {
      "note": "Update :root HSL tokens to match the locked palette. Keep shadcn variable names; only change values. Avoid adding new palette beyond these tokens; derive tints via opacity.",
      "root": {
        "--background": "210 40% 98%  /* #F8FAFC */",
        "--foreground": "215 32% 17%  /* approx #1E2A3A */",
        "--card": "0 0% 100%  /* #FFFFFF */",
        "--card-foreground": "215 32% 17%",
        "--popover": "0 0% 100%",
        "--popover-foreground": "215 32% 17%",
        "--primary": "174 83% 32%  /* #0D9488 */",
        "--primary-foreground": "0 0% 100%",
        "--secondary": "165 63% 92%  /* #DBF7EF */",
        "--secondary-foreground": "215 32% 17%",
        "--muted": "210 40% 96%  /* use background-ish */",
        "--muted-foreground": "215 16% 40%",
        "--accent": "165 63% 92%",
        "--accent-foreground": "215 32% 17%",
        "--destructive": "0 84% 60%  /* keep default red for errors */",
        "--destructive-foreground": "0 0% 100%",
        "--border": "220 13% 91%  /* #E5E7EB */",
        "--input": "220 13% 91%",
        "--ring": "174 83% 32%  /* teal focus ring */",
        "--radius": "1rem  /* maps to rounded-2xl feel; buttons override to full */"
      },
      "additional_custom_properties": {
        "--tv-text": "#1E2A3A",
        "--tv-teal": "#0D9488",
        "--tv-mint": "#DBF7EF",
        "--tv-bg": "#F8FAFC",
        "--tv-border": "#E5E7EB",
        "--tv-shadow-sm": "0 1px 2px rgba(30,42,58,0.06)",
        "--tv-shadow-md": "0 10px 30px rgba(30,42,58,0.10)",
        "--tv-shadow-hover": "0 16px 40px rgba(30,42,58,0.14)",
        "--tv-focus": "0 0 0 4px rgba(13,148,136,0.18)",
        "--tv-noise-opacity": "0.06"
      }
    },
    "radius_rules": {
      "cards": "rounded-2xl",
      "buttons_and_pills": "rounded-full",
      "inputs": "rounded-xl (search bar can be rounded-full on desktop)"
    },
    "shadow_system": {
      "card_default": "shadow-[0_1px_2px_rgba(30,42,58,0.06)]",
      "card_hover": "hover:shadow-[0_16px_40px_rgba(30,42,58,0.14)]",
      "floating_panel": "shadow-[0_10px_30px_rgba(30,42,58,0.10)]"
    },
    "border_system": {
      "default": "border border-[#E5E7EB]",
      "hover_accent": "hover:border-[#0D9488]",
      "active": "border-[#0D9488]"
    },
    "spacing_system": {
      "container": "px-4 sm:px-6 lg:px-8",
      "section_padding": "py-10 sm:py-14 lg:py-16",
      "card_padding": "p-5 sm:p-6",
      "stack_gaps": "gap-3 (tight), gap-4 (default), gap-6 (airy), gap-8 (section)"
    }
  },

  "typography": {
    "fonts": {
      "body": {
        "family": "Poppins",
        "google_fonts": "https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap"
      },
      "display": {
        "family": "DM Serif Display",
        "google_fonts": "https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&display=swap"
      },
      "implementation": {
        "note": "Add <link> tags in public/index.html OR import in index.css. Then set body font-family to Poppins; headings use DM Serif Display via utility class.",
        "tailwind_util_classes": {
          "display_heading": "font-[\"DM Serif Display\"] tracking-[-0.02em] text-[#1E2A3A]",
          "body_text": "font-[Poppins] text-[#1E2A3A]"
        }
      }
    },
    "type_scale": {
      "h1": "text-4xl sm:text-5xl lg:text-6xl leading-[1.05]",
      "h2": "text-base md:text-lg text-[#1E2A3A]/80",
      "h3": "text-xl sm:text-2xl font-semibold",
      "body": "text-sm sm:text-base leading-relaxed",
      "small": "text-xs sm:text-sm",
      "ui_label": "text-xs font-medium tracking-wide"
    },
    "copy_tone_examples_id": {
      "hero_supporting": "Cari kerja berdasarkan skill, bukan sekadar gelar. Bangun portofolio, dapat rekomendasi, dan temukan peluang yang cocok.",
      "cta_primary": "Cari Lowongan",
      "cta_secondary": "Lihat Kategori",
      "empty_state": "Belum ada hasil. Coba ubah kata kunci atau lokasi."
    }
  },

  "layout_and_grid": {
    "global": {
      "max_width": "max-w-6xl (marketing) / max-w-7xl (dashboard)",
      "grid": "12-col on lg; 4-col on mobile",
      "reading_flow": "Left-aligned content; avoid centered paragraphs except hero headline block on mobile only."
    },
    "home_page_skeleton": {
      "hero": "Two-column on lg: left copy + search; right illustration/photo card. On mobile: stacked with search first.",
      "category_grid": "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6",
      "akselerasi_section": "grid grid-cols-1 lg:grid-cols-2 gap-4 sm:gap-6",
      "footer": "4-column on lg, accordion/collapsible on mobile"
    },
    "job_search_page": {
      "desktop": "Sidebar filters (w-80) + results (flex-1) with sticky top filter summary.",
      "mobile": "Filters in Sheet (right) triggered by button; results list first."
    },
    "dashboards": {
      "candidate": "Top stats row (4 cards) + AI recommendations (bento) + applications table",
      "employer": "Top stats row + job list with quick actions + post job form (stepper-like sections)"
    }
  },

  "decorative_system": {
    "dotted_pattern": {
      "placement": [
        "Behind hero only (top section), anchored top-right and mid-left as two layers",
        "Optional small strip behind category header (not behind cards)"
      ],
      "opacity": "0.10–0.16 max",
      "color": "Use Forgotten Blue at low opacity OR Teal at 10% opacity; never full-saturation dots.",
      "implementation": {
        "preferred": "Inline SVG background via CSS background-image (data URI) to avoid extra requests.",
        "tailwind_example": "relative overflow-hidden bg-[#F8FAFC]",
        "css_snippet": ".tv-dots{background-image:radial-gradient(rgba(30,42,58,0.14) 1px, transparent 1px);background-size:14px 14px;}"
      }
    },
    "noise_overlay": {
      "rule": "Use subtle noise only on hero background and large empty surfaces; keep opacity <= var(--tv-noise-opacity).",
      "implementation": "Add pseudo-element with repeating-radial-gradient or SVG noise; do not affect readability."
    }
  },

  "components": {
    "component_path": {
      "shadcn_primary": "/app/frontend/src/components/ui/",
      "use_components": [
        "button.jsx",
        "input.jsx",
        "select.jsx",
        "badge.jsx",
        "card.jsx",
        "breadcrumb.jsx",
        "sheet.jsx",
        "drawer.jsx",
        "tabs.jsx",
        "table.jsx",
        "skeleton.jsx",
        "separator.jsx",
        "tooltip.jsx",
        "progress.jsx",
        "slider.jsx",
        "checkbox.jsx",
        "radio-group.jsx",
        "textarea.jsx",
        "sonner.jsx"
      ]
    },

    "buttons": {
      "shape": "rounded-full",
      "variants": {
        "primary": {
          "usage": "CTA utama: Cari Lowongan, Lamar, Simpan",
          "classes": "bg-[#0D9488] text-white hover:bg-[#0B7F76] focus-visible:ring-2 focus-visible:ring-[#0D9488] focus-visible:ring-offset-2",
          "motion": "transition-colors duration-200; active:scale-[0.98]"
        },
        "secondary": {
          "usage": "CTA pendamping: Lihat Detail, Pelajari Program",
          "classes": "bg-[#DBF7EF] text-[#1E2A3A] hover:bg-[#CFF3EA] border border-[#E5E7EB]",
          "motion": "transition-colors duration-200; active:scale-[0.98]"
        },
        "ghost": {
          "usage": "Toolbar actions: Filter, Sort, Bookmark",
          "classes": "bg-transparent hover:bg-[#DBF7EF]/60 text-[#1E2A3A]",
          "motion": "transition-colors duration-200"
        }
      },
      "sizes": {
        "sm": "h-9 px-4 text-sm",
        "md": "h-11 px-5 text-sm",
        "lg": "h-12 px-6 text-base"
      },
      "data_testid_examples": [
        "data-testid=\"hero-search-submit-button\"",
        "data-testid=\"job-card-view-details-button\"",
        "data-testid=\"job-detail-apply-button\"",
        "data-testid=\"job-detail-save-button\""
      ]
    },

    "forms_and_inputs": {
      "search_bar_integrated": {
        "anatomy": [
          "Input keyword (left)",
          "Select lokasi (middle)",
          "Button Cari (right)"
        ],
        "desktop_layout": "flex items-center gap-2 rounded-full border border-[#E5E7EB] bg-white p-2 shadow-[0_10px_30px_rgba(30,42,58,0.08)]",
        "mobile_layout": "grid grid-cols-1 gap-2 rounded-2xl border border-[#E5E7EB] bg-white p-3",
        "input_classes": "h-11 rounded-xl border-[#E5E7EB] focus-visible:ring-0 focus-visible:shadow-[var(--tv-focus)]",
        "select_classes": "h-11 rounded-xl",
        "validation": "Inline error text in destructive color; keep Indonesian microcopy."
      },
      "filters_sidebar": {
        "components": ["Input", "Select", "Checkbox", "RadioGroup", "Slider"],
        "grouping": "Use Card sections with headings + Separator; keep 2–3 controls per group.",
        "mobile": "Use Sheet for filters with Apply + Reset sticky footer."
      },
      "auth_forms": {
        "layout": "Centered card (max-w-md) on bg-[#F8FAFC] with subtle dots behind top area.",
        "role_selector": "Use Tabs or RadioGroup for Kandidat vs Perusahaan.",
        "data_testid": [
          "login-email-input",
          "login-password-input",
          "login-submit-button",
          "signup-role-tabs",
          "signup-submit-button"
        ]
      }
    },

    "cards": {
      "global_card_anatomy": {
        "base": "rounded-2xl bg-white border border-[#E5E7EB] shadow-[0_1px_2px_rgba(30,42,58,0.06)]",
        "hover": "hover:border-[#0D9488] hover:shadow-[0_16px_40px_rgba(30,42,58,0.14)]",
        "motion": "transition-[box-shadow,border-color,background-color] duration-200"
      },
      "category_card": {
        "layout": "flex items-stretch justify-between gap-4 p-5",
        "left": "Title + small count; keep text left aligned",
        "right_media": "Illustration/photo in AspectRatio; add white-to-transparent overlay gradient on left edge",
        "image_motion": "group-hover:scale-[1.04] transition-transform duration-300",
        "data_testid": "category-card"
      },
      "akselerasi_card": {
        "background": "bg-[#DBF7EF]",
        "icon_badge": "h-12 w-12 rounded-full bg-[#0D9488] text-white flex items-center justify-center",
        "cta": "Secondary button inside card; keep rounded-full",
        "data_testid": ["akselerasi-bootcamp-card", "akselerasi-sertifikasi-card"]
      },
      "job_card": {
        "layout": "p-5 flex flex-col gap-3",
        "top_row": "Avatar/logo + title block + bookmark icon button",
        "badges": "Use Badge for work mode, employment type; mint background badges",
        "match_score": "Small Progress bar + label 'Kecocokan' (AI) with tooltip",
        "cta": "Button ghost/secondary 'Lihat Detail'",
        "data_testid": [
          "job-card",
          "job-card-save-button",
          "job-card-match-score",
          "job-card-view-details-button"
        ]
      },
      "salary_insight_card_ai": {
        "style": "bg-[#DBF7EF]/60 border border-[#E5E7EB] rounded-2xl p-5",
        "content": "Explain range + confidence; keep short; add info tooltip",
        "data_testid": "salary-insight-card"
      }
    },

    "navigation": {
      "header": {
        "desktop": "Top nav with logo left, links center, auth buttons right. Sticky with backdrop blur.",
        "classes": "sticky top-0 z-40 bg-[#F8FAFC]/80 backdrop-blur border-b border-[#E5E7EB]",
        "mobile": "Use Sheet/Drawer for nav; trigger icon button.",
        "data_testid": ["mobile-nav-open-button", "header-login-link", "header-signup-button"]
      },
      "breadcrumb": {
        "use": "Job Detail + dashboards",
        "component": "breadcrumb.jsx",
        "data_testid": "page-breadcrumb"
      },
      "pagination": {
        "use": "Job search results",
        "component": "pagination.jsx",
        "data_testid": "job-results-pagination"
      }
    },

    "tables_and_lists": {
      "applications_table": {
        "component": "table.jsx",
        "row_hover": "hover:bg-[#DBF7EF]/35",
        "status_badges": "Badge variants: success/neutral/warn using teal + opacity (no new colors; use teal with alpha + text in forgotten blue)",
        "data_testid": "applications-table"
      }
    },

    "feedback_states": {
      "loading": {
        "component": "skeleton.jsx",
        "patterns": [
          "JobCard skeleton: logo circle + 2 lines + badges row + button",
          "Dashboard stats skeleton: 4 cards"
        ],
        "data_testid": "loading-skeleton"
      },
      "empty": {
        "style": "Card with mint tint + icon + CTA",
        "copy": "Belum ada data di sini. Mulai dengan menyimpan lowongan atau lengkapi profil skill-mu.",
        "data_testid": "empty-state"
      },
      "error": {
        "style": "Alert component with destructive variant",
        "component": "alert.jsx",
        "data_testid": "error-alert"
      },
      "toasts": {
        "library": "sonner",
        "component": "/app/frontend/src/components/ui/sonner.jsx",
        "use_cases": ["Lowongan disimpan", "Lamaran terkirim", "Gagal memuat data"],
        "data_testid": "toast"
      }
    }
  },

  "motion_and_microinteractions": {
    "principles": [
      "Motion is functional: highlight hover, confirm actions, guide attention",
      "Prefer subtle scale (0.98 press), shadow lift, and border-color transitions",
      "Respect prefers-reduced-motion"
    ],
    "do_not": ["Do not use transition: all"],
    "recommended_library": {
      "framer_motion": {
        "when": "Hero entrance, card stagger, sheet transitions (optional)",
        "install": "npm i framer-motion",
        "usage_notes": "Use for page-level animations only; keep durations 0.25–0.45s; ease-out."
      }
    },
    "interaction_specs": {
      "card_hover": "translate-y-[-2px] + shadow hover; image scale inside category cards",
      "button_press": "active:scale-[0.98]",
      "pill_pulse": "For 'Kecocokan AI' badge: subtle pulse once on load (opacity change), not infinite",
      "scroll": "Hero dots parallax: background-position shift 8–16px on scroll (optional, lightweight)"
    }
  },

  "accessibility": {
    "wcag": "Target AA",
    "focus": "Use visible focus ring in teal; never remove outline without replacement",
    "hit_targets": "Min 44px height for primary actions",
    "contrast": "Forgotten Blue text on white/mint; teal used for accents and buttons with white text",
    "aria": "Sheet/Drawer triggers must have aria-label in Indonesian"
  },

  "performance_and_responsiveness": {
    "mobile_first": "All layouts start stacked; enhance at sm/md/lg",
    "skeleton": "Use Skeleton for lists and dashboards; avoid layout shift",
    "optimistic_ui": "Save/bookmark and apply actions should update UI immediately; rollback on error with toast",
    "images": "Use AspectRatio + lazy loading; keep hero media optional"
  },

  "image_urls": {
    "hero_support_media": [
      {
        "url": "https://images.unsplash.com/photo-1637665662134-db459c1bbb46?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85",
        "category": "hero",
        "description": "Foto ruang meeting minimal untuk kartu ilustrasi di hero (opsional)."
      }
    ],
    "category_card_media": [
      {
        "url": "https://images.unsplash.com/photo-1495576775051-8af0d10f19b1?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85",
        "category": "kategori",
        "description": "Foto profesional minimal untuk placeholder ilustrasi kategori (gunakan overlay gradient putih→transparan)."
      }
    ],
    "auth_or_dashboard_header": [
      {
        "url": "https://images.unsplash.com/photo-1573878411897-35205a33028f?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85",
        "category": "dashboard",
        "description": "Foto orang bekerja untuk header kecil dashboard/empty state (opsional, gunakan crop kecil)."
      }
    ],
    "dotted_pattern_reference": [
      {
        "url": "https://images.unsplash.com/photo-1658248165124-30918129aee9?crop=entropy&cs=srgb&fm=jpg&ixlib=rb-4.1.0&q=85",
        "category": "pattern_reference",
        "description": "Referensi tekstur/pola titik; implementasi sebaiknya via CSS radial-gradient (bukan gambar besar)."
      }
    ]
  },

  "instructions_to_main_agent": {
    "critical_fixes": [
      "Remove CRA default App.css styles (dark centered header). Do NOT center the whole app container.",
      "Update /app/frontend/src/index.css :root tokens to match locked palette; set body font to Poppins.",
      "Add DM Serif Display for large headings only (hero headline, section titles).",
      "Ensure every interactive element and key info has data-testid (kebab-case).",
      "Use shadcn components from /components/ui (no raw HTML dropdown/calendar/toast).",
      "Implement dotted pattern behind hero only with low opacity; keep gradients within restriction rules (and avoid saturated/dark gradients)."
    ],
    "page_build_order": [
      "1) Home (Hero + Search + Category Grid + Akselerasi Karier + Footer)",
      "2) Job Search (filters sidebar + results + pagination + skeleton)",
      "3) Job Detail (breadcrumb + apply/save + salary insight + related)",
      "4) Auth (Login/Signup with role selector)",
      "5) Candidate Dashboard",
      "6) Employer Dashboard"
    ],
    "testing_hooks": {
      "rule": "Add data-testid to: nav links, buttons, inputs, selects, filter controls, cards, badges showing match score, toast messages, empty/error states.",
      "examples": [
        "job-search-keyword-input",
        "job-search-location-select",
        "job-search-filters-open-button",
        "job-search-apply-filters-button",
        "job-search-reset-filters-button",
        "job-detail-related-jobs-section"
      ]
    }
  },

  "general_ui_ux_design_guidelines_appendix": "- You must **not** apply universal transition. Eg: `transition: all`. This results in breaking transforms. Always add transitions for specific interactive elements like button, input excluding transforms\n- You must **not** center align the app container, ie do not add `.App { text-align: center; }` in the css file. This disrupts the human natural reading flow of text\n- NEVER: use AI assistant Emoji characters like`🤖🧠💭💡🔮🎯📚🎭🎬🎪🎉🎊🎁🎀🎂🍰🎈🎨🎰💰💵💳🏦💎🪙💸🤑📊📈📉💹🔢🏆🥇 etc for icons. Always use **FontAwesome cdn** or **lucid-react** library already installed in the package.json\n\n **GRADIENT RESTRICTION RULE**\nNEVER use dark/saturated gradient combos (e.g., purple/pink) on any UI element.  Prohibited gradients: blue-500 to purple 600, purple 500 to pink-500, green-500 to blue-500, red to pink etc\nNEVER use dark gradients for logo, testimonial, footer etc\nNEVER let gradients cover more than 20% of the viewport.\nNEVER apply gradients to text-heavy content or reading areas.\nNEVER use gradients on small UI elements (<100px width).\nNEVER stack multiple gradient layers in the same viewport.\n\n**ENFORCEMENT RULE:**\n    • Id gradient area exceeds 20% of viewport OR affects readability, **THEN** use solid colors\n\n**How and where to use:**\n   • Section backgrounds (not content backgrounds)\n   • Hero section header content. Eg: dark to light to dark color\n   • Decorative overlays and accent elements only\n   • Hero section with 2-3 mild color\n   • Gradients creation can be done for any angle say horizontal, vertical or diagonal\n\n- For AI chat, voice application, **do not use purple color. Use color like light green, ocean blue, peach orange etc**\n\n</Font Guidelines>\n\n- Every interaction needs micro-animations - hover states, transitions, parallax effects, and entrance animations. Static = dead. \n   \n- Use 2-3x more spacing than feels comfortable. Cramped designs look cheap.\n\n- Subtle grain textures, noise overlays, custom cursors, selection states, and loading animations: separates good from extraordinary.\n   \n- Before generating UI, infer the visual style from the problem statement (palette, contrast, mood, motion) and immediately instantiate it by setting global design tokens (primary, secondary/accent, background, foreground, ring, state colors), rather than relying on any library defaults. Don't make the background dark as a default step, always understand problem first and define colors accordingly\n    Eg: - if it implies playful/energetic, choose a colorful scheme\n           - if it implies monochrome/minimal, choose a black–white/neutral scheme\n\n**Component Reuse:**\n\t- Prioritize using pre-existing components from src/components/ui when applicable\n\t- Create new components that match the style and conventions of existing components when needed\n\t- Examine existing components to understand the project's component patterns before creating new ones\n\n**IMPORTANT**: Do not use HTML based component like dropdown, calendar, toast etc. You **MUST** always use `/app/frontend/src/components/ui/ ` only as a primary components as these are modern and stylish component\n\n**Best Practices:**\n\t- Use Shadcn/UI as the primary component library for consistency and accessibility\n\t- Import path: ./components/[component-name]\n\n**Export Conventions:**\n\t- Components MUST use named exports (export const ComponentName = ...)\n\t- Pages MUST use default exports (export default function PageName() {...})\n\n**Toasts:**\n  - Use `sonner` for toasts\"\n  - Sonner component are located in `/app/src/components/ui/sonner.tsx`\n\nUse 2–4 color gradients, subtle textures/noise overlays, or CSS-based noise to avoid flat visuals."
}
