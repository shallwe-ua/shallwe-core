# Shallwe (demo)

> ⚠️ Work in Progress. This repo is one part of a bigger codebase. The product itself is paused; I’m open‑sourcing a stable demo for portfolio and tech practice. It’s not the final structure.

> Usage: Evaluation-Only (see LICENSE)

---

📜 Background

Shallwe was aimed to be the first Ukrainian flatmate‑matching platform focused on quality matches. Active development stopped in July 2024 (docs outside GitHub were mostly lost). What you see here is a clean, working slice turned into a demo.

- Status: stable demo of core features; future work is not planned beyond polishing.
- Purpose: showcase architecture/engineering; allow you to run and click around.

---

✅ What’s implemented (and works)

- Authentication: Google OAuth2 only (intentionally first for faster iteration and no email handling).
- Access control: protected endpoints, simple access checks.
- Locations system: hierarchical Ukrainian KATOTTG mapping with constraints and search helpers.
- Profiles: create/update/delete profile; validated fields and preferences based on real interview/survey signals (e.g., rent ranges, rent duration, smoking/guests/bedtime/neatness, pets, interests, couple/children flags).
- Photos pre‑verification: format/size checks + free AI library for face presence/harmful content pre‑moderation (note: synthetic faces are possible; post‑moderation was planned).
- API docs: Swagger/OpenAPI (public spec link below).

Not included: full search and chats (specs existed; implementation postponed due to project pause).

---

🏗 Architecture (short)

- Simplified Modulith: layered Django apps (MVC by nature) within a single deployable unit. It kept the MVP lean, changeable, and easy to reason about.
- Clear module boundaries: `shallwe_auth`, `shallwe_access`, `shallwe_locations`, `shallwe_profile`, `shallwe_photo`, etc. HTTP/API layer is thin; domain logic is inside modules; validations are expressed as model constraints and serializers.
- As least environment difference as possible, app code totally kept away from depending on whether it's local, Compose, Cloud Infra or whatever - you just change the config, the app doesn't care. 12-Factor-App adherence was kept in mind whenever possible with constraints. 
- Rationale: time/budget constraints and pre‑product‑market‑fit stage. Intentionally avoided premature microservices/Kafka/K8s. Scale‑out wasn’t the problem to solve before users.

---

🧭 How to run locally (Docker Compose)

1) Copy envs
- Copy `.env.example` → `.env` and fill the required values. Keep defaults where possible.

2) Pick a profile
- The compose files are documented at the top of each file. Typical options:
  - `mock-only`: Frontend only (mock/dev), no backend. For quick UI checks.
  - `api-only`: Backend only (dev, hot reload). For API/dev work.
  - `mock-dev`: Frontend (dev) + Backend (dev). Recommended for playing end‑to‑end.
  - `mock-prod`: Frontend prod build + Backend dev. For closer‑to‑prod FE build.
  - `qa`: Nginx + pulled images, resembling prod layout.

3) Run examples
- Dev combo (FE+BE):
  - `docker compose -f compose.base.yaml -f compose.dev.yaml --profile mock-dev up`
- API only:
  - `docker compose -f compose.base.yaml -f compose.dev.yaml --profile api-only up`
- QA layout:
  - `docker compose -f compose.base.yaml -f compose.qa.yaml --profile qa up`

Notes
- Frontend is a minimal mock used for manual checks; the real public demo will be separate.
- You can also inspect Dockerfiles/entrypoints for manual local runs if you don’t want Compose.

---

🌐 Deployment (separate infra repo)

- Infrastructure: Terraform AWS (stage/QA) for backend is live (paused lately to spare my free-tier usage; will be up again alongside true frontend)
- Frontend: planned deployment on Vercel (or similar) to keep it free and easy
- Infra repo: see `shallwe-infra` — https://github.com/shallwe-ua/shallwe-infra

If you want to launch beyond local Compose, that repo is the place to start. However, changing a bit Compose to quickly deploy as a standalone monolith without configuration overhead in cloud is possible too. You'll have to change a couple of config definitions for public access, though, but generally they should work anywhere as is.

---

🗺 Locations model (why it’s convenient)

- Based on Ukraine’s KATOTTG. Each location has a compact `hierarchy` code (e.g., `UA002001...`) reflecting containment.
- Matching/containment becomes a simple prefix comparison on those hierarchy codes (e.g., district ⊂ city ⊂ region ⊂ country). It’s robust, fast for the Ukrainian launch and gave us extremely simple queries and match logic.
- Porting to other countries may require a different hierarchy source; this one was optimized for Ukraine, which was our go‑to‑market.

---

🧪 Testing

- Core functionality is unit‑tested with Django’s test framework and passed manual QA in alpha.
- Manual QA: executed via Postman collections covering typical user flows (auth, profile lifecycle, photo checks, locations), plus edge cases and error validations.
- Run tests:
  - All tests: `python3 manage.py test`
  - Per app/module: `python3 manage.py test shallwe_profile` or `python3 manage.py test shallwe_profile.tests.test_models`
- Tests ensure robust validations and error cases across the main modules.

---

📦 Data and admin

- Fixtures for testing are included; the latest KATOTTG CSV is bundled. You can load and play immediately, then add your own data via APIs or Django admin.
- Admin user is created from envs when using Docker Compose (check `.env.example`).

---

🛠 Tech note (short)

- Stack at a glance: Python/Django REST + PostgreSQL, with a minimal Next.js mock frontend and Nginx in the QA layout. The focus here is clean domain logic, fast development and predictable ops rather than trendy tooling.

---

📚 API docs

- Swagger/OpenAPI (current public spec): https://app.swaggerhub.com/apis/S3MCHANNEL/shallwe-api/0.6.1
  - Note: one minor gap vs latest code (healthcheck endpoint addition). The rest matches the running demo.

---

📈 Plans and constraints

- Nearest plans (short):
  - Decouple testing and migrations from entrypoint.
  - Add CI/CD.
  - Provide a minimal demo frontend that covers all features (separate from `mock_frontend`).
  - Keep AWS deployment available as a showcase.
- Limitations (intentionally simplified given a $0/month budget):
  - No Kubernetes/EKS; potentially ECS for backend later.
  - No ECR; images hosted in a cheaper/free registry.
  - One EC2 free‑tier instance for now; Next.js likely on Vercel.
  - No Secrets Manager; simple environment variable approach instead.

---

🔐 License and usage

This repository is provided for evaluation purposes only (read‑only). All rights reserved.

- You may: clone, read, run locally/in private cloud, and evaluate as part of recruiting/technical review.
- You may not: use, modify, distribute, or incorporate the code or assets in any product, service, or derivative work.
- No license is granted for reuse or redistribution. Copyright © the project author.

If you need broader rights for a specific purpose, contact me directly.

---

🙋‍♂️ Contact

- Feel free to reach out for a quick walkthrough or architecture chat.
