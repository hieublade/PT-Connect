# 🎨 MASTERPLAN: MIGRATING PT-CONNECT FRONTEND FROM STREAMLIT TO REACT

> **Target**: Replace the monolithic Python Streamlit frontend with a high-performance, modern, mobile-responsive **React + TypeScript + Tailwind CSS + shadcn/ui** Single Page Application (SPA), integrating seamlessly with the newly migrated **FastAPI backend (`http://localhost:8080/api/v1`)**.
> **Benchmark Reference**: **Everfit** (clean visual cards, mobile-first aesthetics), **ABC Trainerize** (interactive calendar scheduling, client badges), and **TrueCoach** (rapid workout & attendance workflow).

---

## 1. Streamlit As-Is Analysis & Technical Pain Points

### 1.1 Existing Streamlit Architecture
Currently located in `/home/thanhvv17@fsoft.fpt.vn/cicd-lab/PT-Connect/frontend`:
* **Core Router (`app.py`)**: Monolithic script with role-based `st.sidebar` and conditional `render_*_page()` calls.
* **Màn hình Đăng nhập / Đăng ký (`pages/login.py`)**: 2 tabs for Login and Student/PT onboarding with file uploader for avatar and certificates.
* **Màn hình Học viên (`pages/student.py`)**: 7 tabs (Explore PTs, PT Profile & Course Enrollment, Booking Slots, My Schedule & OTP Attendance, Enrolled Packages & Contract PDF, Internal Wallet & Deposit, Profile). Contains hacky JS injection (`parentDoc.querySelectorAll('button[data-baseweb="tab"]')`) to switch tabs programmatically.
* **Màn hình Huấn luyện viên (`pages/pt.py`)**: 6 tabs (Overview KPI cards, Booking Approval, Availability Slot Grid, Course CRUD, Workout Plan Builder, Profile & Credentials).
* **Màn hình Quản trị viên (`pages/admin.py`)**: 3 tabs (Pending PT Verifications, User List & Ban/Active toggles, Platform Analytics & Revenue Charts).

### 1.2 Pain Points of Streamlit for Production
1. **Full-page Re-renders**: Every button click, radio select, or form submit re-executes the Python script from top to bottom, causing screen flashes, scroll position jumps, and sluggish UX.
2. **Hackish Tab/State Navigation**: Tab switching requires raw DOM JavaScript injection into parent iframe (`parentDoc.querySelectorAll`).
3. **Responsive Mobile Limitations**: Clunky tables and static column layouts break on smartphones (crucial because PTs and gym-goers manage bookings primarily on mobile).
4. **No Real-Time Capabilities**: Polling via `st_autorefresh` is heavy and cannot easily support WebSocket live booking notifications or instant messaging.
5. **Rigid Custom Styling**: Overriding Streamlit CSS with `unsafe_allow_html=True` is brittle across Streamlit version upgrades.

---

## 2. Industry Benchmark & Reference Analysis (PT Platforms)

| Feature / UX Pattern | **Everfit** (Modern Reference) | **ABC Trainerize** (Feature Hub) | **PT-Connect React Target** |
| :--- | :--- | :--- | :--- |
| **Design Language** | Sleek, dark/light glassmorphism, rounded-2xl cards | Vibrant, gamified, rich widgets | **Modern Minimalist**: Slate-900 / Emerald-500 accents, clean card borders, smooth framer-motion transitions |
| **Booking & Schedule** | Day/Week slot picker with instant visual availability | Full interactive calendar with drag-to-reschedule | **FullCalendar / DayGrid**: Visual morning/afternoon/evening slot selector with instant color-coded states |
| **Attendance Verification** | GPS check-in / QR scan | Manual check-in toggle | **Dynamic OTP Drawer**: 6-digit countdown timer for Student with instant PT one-click verification |
| **Contract Signing & PDF** | In-app digital agreement preview | Downloadable PDF document | **Embedded PDF Viewer + Modal**: Preview contract inline with signature confirmation before wallet deduction |
| **Financial / Wallet** | Stripe checkout flow | In-app credit ledger | **Wallet Card & Quick Top-Up**: Balance pill, quick deposit buttons (+100k, +500k, +1M), audit transaction timeline |

---

## 3. Target Technology Stack

* **Core Framework**: React 19 / 18 + **Vite 6** (sub-second HMR, optimized tree-shaking).
* **Language**: TypeScript 5.5+ (strict mode, 100% type safety).
* **Styling & Design System**: 
  * **Tailwind CSS v4** for utility-first styling.
  * **shadcn/ui** (built on top of Radix UI primitives) for accessible, keyboard-navigable components:
    * `Dialog`, `Sheet` (drawer), `DropdownMenu`, `Tabs`, `Table`, `Badge`, `Avatar`, `Calendar`, `Card`, `Toast (Sonner)`, `Skeleton`.
  * **Lucide React** for consistent, modern icons.
* **State Management & Data Fetching**:
  * **TanStack Query (React Query v5)**: Server state caching, automatic garbage collection, background refetching, and optimistic updates.
  * **Zustand**: Lightweight client state for Auth session, JWT tokens, and Theme (Light/Dark).
* **Routing**: **React Router v7 / v6** with nested layout routes and Role-based Route Guards (`<ProtectedRoute allowedRoles={['PT']} />`).
* **Forms & Validation**: **React Hook Form** + **Zod** (schema validation 100% synchronized with FastAPI Pydantic models).
* **Data Visualization**: **Recharts** (responsive SVG charts for Revenue, Booking trends, and Client completion rates).
* **HTTP Client**: **Axios** with global interceptors for Bearer Token injection and auto-logout on 401.

---

## 4. Frontend Project Structure (`frontend-react/`)

```
frontend-react/
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── routes/
│   │   ├── index.tsx                 # Route definitions & RouterProvider
│   │   ├── ProtectedRoute.tsx        # Role-based route guard
│   │   └── RootLayout.tsx            # Global shell with Navbar & Toast provider
│   ├── assets/
│   ├── components/
│   │   ├── ui/                       # shadcn/ui components (button, dialog, card, etc.)
│   │   ├── common/
│   │   │   ├── Navbar.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── UserMenu.tsx
│   │   │   ├── StatCard.tsx
│   │   │   └── EmptyState.tsx
│   │   ├── student/
│   │   │   ├── PtCard.tsx
│   │   │   ├── PtFilterBar.tsx
│   │   │   ├── BookingModal.tsx
│   │   │   ├── OtpAttendanceModal.tsx
│   │   │   ├── ContractPdfViewer.tsx
│   │   │   └── WalletDepositDialog.tsx
│   │   ├── pt/
│   │   │   ├── SlotSchedulerGrid.tsx
│   │   │   ├── BookingApprovalTable.tsx
│   │   │   ├── CourseCrudModal.tsx
│   │   │   └── WorkoutPlanDrawer.tsx
│   │   └── admin/
│   │       ├── PendingPtTable.tsx
│   │       ├── UserManagementTable.tsx
│   │       └── AnalyticsCharts.tsx
│   ├── features/                     # Feature modules (API hooks + types)
│   │   ├── auth/
│   │   │   ├── authApi.ts
│   │   │   ├── useAuth.ts
│   │   │   └── authSchemas.ts
│   │   ├── student/
│   │   │   └── studentApi.ts
│   │   ├── pt/
│   │   │   └── ptApi.ts
│   │   ├── bookings/
│   │   │   └── bookingApi.ts
│   │   ├── wallet/
│   │   │   └── walletApi.ts
│   │   └── admin/
│   │       └── adminApi.ts
│   ├── hooks/
│   │   ├── useDebounce.ts
│   │   └── useMediaQuery.ts
│   ├── stores/
│   │   └── authStore.ts              # Zustand auth & user store
│   ├── types/
│   │   └── api.ts                    # Global TypeScript interfaces matching FastAPI schemas
│   └── lib/
│       ├── axios.ts                  # Configured Axios instance with interceptors
│       └── utils.ts                  # cn() class merger
```

---

## 5. Detailed Screen & Feature Migration Roadmap

### Phase 1: Foundation, Design System & Auth (Weeks 1)
- [ ] Scaffold Vite + React + TypeScript + Tailwind CSS + shadcn/ui.
- [ ] Configure Axios instance with `VITE_API_URL` pointing to `http://localhost:8080/api/v1`.
- [ ] Setup Zustand `useAuthStore` with localStorage persistence.
- [ ] Build **Login & Registration Pages**:
  - Tabbed or split-screen modern card with animated transitions.
  - Role selection pill (Học viên vs. Huấn luyện viên).
  - Form validation with Zod and Toast notifications.
  - Automatic redirect based on role (`/student`, `/pt`, `/admin`).

### Phase 2: Student Experience (Week 2)
- [ ] **Explore & Search PTs (`/student/explore`)**:
  - Filter bar (price range slider, specialization multi-select tags, rating sort).
  - Responsive Grid of `PtCard` with avatar, verified badge, hourly rate, and "Book Now" CTA.
- [ ] **PT Profile & Course Enrollment (`/student/pt/:id`)**:
  - Bio, verified certificates modal, reviews with star ratings.
  - Course package cards with "Enroll & Sign Contract" button.
- [ ] **Slot Booking Calendar (`/student/book/:ptId`)**:
  - Interactive weekly slot picker showing available time blocks.
  - Confirmation sheet displaying fee calculation and one-click booking.
- [ ] **My Schedule & Attendance (`/student/schedule`)**:
  - Upcoming sessions list.
  - One-click **Generate Attendance OTP** with 6-digit countdown display.
- [ ] **Wallet & Contract Center (`/student/wallet`)**:
  - Credit card style wallet visualization with balance.
  - Deposit modal with quick amounts.
  - Contracts table with instant PDF preview and download.

### Phase 3: Personal Trainer (PT) Portal (Week 3)
- [ ] **Trainer Dashboard (`/pt/dashboard`)**:
  - KPI Stat cards (Total Active Clients, Monthly Revenue, Pending Requests, Completed Sessions).
  - Upcoming appointments timeline.
- [ ] **Slot & Availability Manager (`/pt/slots`)**:
  - Weekly recurring availability template builder (e.g., Monday-Friday 08:00 - 11:00 & 14:00 - 18:00).
  - Single slot open/close toggle.
- [ ] **Booking Management & OTP Check-in (`/pt/bookings`)**:
  - Status tabs: Pending, Confirmed, Completed, Cancelled.
  - One-click Approve / Reject with reason dialog.
  - Check-in OTP verification input: PT enters Student's 6-digit OTP to confirm completed session.
- [ ] **Course Packages & Workout Plans (`/pt/courses`)**:
  - Course CRUD modal (price, number of sessions, description).
  - Workout routine template builder.

### Phase 4: Admin & Analytics Portal (Week 4)
- [ ] **PT Verification Hub (`/admin/pending-pts`)**:
  - Review submitted bio, credentials, and certificates in high-res lightbox.
  - Instant Approve / Reject buttons with feedback note.
- [ ] **User & System Management (`/admin/users`)**:
  - Data table with sorting, search, pagination, and role filters.
  - Lock / Unlock user account action menu.
- [ ] **Platform Analytics (`/admin/analytics`)**:
  - Recharts: Revenue breakdown, monthly booking volume, top 5 earning PTs.

### Phase 5: Containerization, Testing & Deployment
- [ ] Write Multi-stage production `Dockerfile` (Node 22 build -> Nginx Alpine static serving with SPA fallback `try_files $uri /index.html`).
- [ ] Update root `docker-compose.yml` to replace `frontend` service with new React container.
- [ ] End-to-end testing with Playwright / Cypress for Auth, Booking, and Payment flows.

---

## 6. AI Agent Skill & Tooling Recommendations

To accelerate development and ensure 100% adherence to modern web standards:
1. **Modern Web Guidance Plugin**:
   - Official plugin: `<plugin-card catalog-id="antigravity-plugins-official/plugin/modern-web-guidance-plugin"></plugin-card>`
   - Provides linting, React 19 best practices, server state caching guidelines, and accessibility standards.
2. **Generative UI Skill**:
   - Built-in `generative_ui` skill for fast component prototyping and visual mockups directly inside Antigravity before committing to code.
