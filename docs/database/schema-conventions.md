# Schema Conventions

> Fill in / adjust to match what your services already do — then keep new work consistent with it.

- **Tables**: snake_case, singular or plural — pick what the existing schema does and stay
  consistent per service.
- **PKs**: uuid (or the platform's established strategy); no mixing strategies within a service.
- **Timestamps**: `created_at`, `updated_at` as UTC timestamps; audit columns consistent across
  tables.
- **FKs**: real constraints for real relationships; a deliberately-missing FK is documented in
  `ai/PROJECT_MEMORY.md`.
- **Indexes**: named `idx_<table>_<cols>`; every column used in hot filters/joins/sorts is a
  candidate — verified, not guessed (`ai/skills/database/references/optimize-query.md`).
- **Enums**: stored as varchar with a check constraint or app-enforced set — pick per platform
  standard; never bare magic integers.
- **Money**: numeric/decimal, never float.
