#!/usr/bin/env bash
#
# scripts/release.sh — Flusso di release per PETRA.
#
# Uso:
#   scripts/release.sh <versione>     # es. 2.1.0
#
# Prerequisiti:
#   - Essere nella root del repo petra
#   - .venv/ attivo o presente con pytest installato
#   - gh CLI autenticata (gh auth status)
#   - File ~/Progetti/labs/RELEASE_NOTES_v<versione>.md già preparato
#   - Working tree pulito prima di iniziare
#
# Fa:
#   1. Bump versioni (root + resolver)
#   2. Pausa: aggiornare CHANGELOG.md manualmente
#   3. Test (root + resolver)
#   4. Commit + tag annotato
#   5. Archivio .zip + SHA256 nella cartella padre
#   6. Push main + tag
#   7. GitHub Release con asset
#   8. Promemoria stampato per l'upload manuale su Zenodo
#
set -euo pipefail

# ---------- Configurazione ----------
CONCEPT_DOI="10.5281/zenodo.22741778"
CONCEPT_RECORD_URL="https://zenodo.org/records/22741778"
PARENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"  # ~/Progetti/labs
REPO_DIR="$(cd "${PARENT_DIR}/petra" && pwd)"

# ---------- Colori ----------
C_RESET='\033[0m'
C_BOLD='\033[1m'
C_GREEN='\033[0;32m'
C_YELLOW='\033[0;33m'
C_RED='\033[0;31m'
C_BLUE='\033[0;34m'

say()  { printf "${C_BLUE}==>${C_RESET} %s\n" "$*"; }
ok()   { printf "${C_GREEN}✅${C_RESET} %s\n" "$*"; }
warn() { printf "${C_YELLOW}⚠️ ${C_RESET}%s\n" "$*"; }
die()  { printf "${C_RED}❌${C_RESET} %s\n" "$*" >&2; exit 1; }

# ---------- Argomenti ----------
VERSION="${1:-}"
if [[ -z "${VERSION}" ]]; then
  die "Uso: $0 <versione>   (es. 2.1.0)"
fi

if [[ ! "${VERSION}" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  die "Formato versione non valido: '${VERSION}'. Atteso: X.Y.Z"
fi

TAG="v${VERSION}"
ARCHIVE="${PARENT_DIR}/PETRA-${VERSION}.zip"
CHECKSUM="${PARENT_DIR}/PETRA-${VERSION}.sha256"
NOTES="${PARENT_DIR}/RELEASE_NOTES_v${VERSION}.md"

# ---------- Controlli preliminari ----------
say "Release PETRA ${TAG}"

[[ -f "pyproject.toml" ]] || die "pyproject.toml non trovato: esegui dalla root del repo petra."
[[ -d "resolver" ]]      || die "Directory resolver/ non trovata."

if [[ -n "$(git status --porcelain)" ]]; then
  warn "Working tree non pulito:"
  git status --short
  read -rp "Continuare comunque? [y/N] " ans
  [[ "${ans}" =~ ^[Yy]$ ]] || die "Interrotto dall'utente."
fi

if git rev-parse "${TAG}" >/dev/null 2>&1; then
  die "Il tag ${TAG} esiste già. Scegli un'altra versione o cancellalo."
fi

if [[ ! -f "${NOTES}" ]]; then
  warn "Release notes non trovate: ${NOTES}"
  warn "Il comando 'gh release create' fallirà senza di esse."
  read -rp "Continuare comunque? [y/N] " ans
  [[ "${ans}" =~ ^[Yy]$ ]] || die "Interrotto dall'utente."
fi

if [[ ! -d ".venv" ]]; then
  warn ".venv/ non trovato. Verrà usato il python di sistema."
fi

# ---------- 1. Bump versioni ----------
say "1/8 — Bump versioni: ${VERSION}"
sed -i.bak "s/^version = \".*\"/version = \"${VERSION}\"/" pyproject.toml
sed -i.bak "s/^version = \".*\"/version = \"${VERSION}\"/" resolver/pyproject.toml
rm -f pyproject.toml.bak resolver/pyproject.toml.bak

grep -n '^version' pyproject.toml resolver/pyproject.toml

# ---------- 2. Changelog (manuale) ----------
say "2/8 — Aggiorna CHANGELOG.md"
warn "Aggiungi la voce [${VERSION}] in cima a CHANGELOG.md."
warn "Non proseguire finché il changelog non è pronto."
read -rp "Premi INVIO quando CHANGELOG.md è aggiornato..." _

grep -q "^## \[${VERSION}\]" CHANGELOG.md || die "Voce [${VERSION}] non trovata nel CHANGELOG.md."
ok "Voce [${VERSION}] presente nel changelog."

# ---------- 3. Test ----------
say "3/8 — Test"
if [[ -d ".venv" ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

python -m pip install -e ".[test]" -q
python -m pip install -e "resolver/" -q

say "  → test root"
python -m pytest tests/ -q
say "  → test resolver"
python -m pytest resolver/tests/ -q
ok "Test superati."

# ---------- 4. Commit + tag ----------
say "4/8 — Commit + tag"
git add CHANGELOG.md pyproject.toml resolver/pyproject.toml
git commit -m "release: PETRA ${TAG}"
git tag -a "${TAG}" -m "PETRA ${TAG} — Prime Exponent Tower Recursive Algebra"
ok "Commit e tag ${TAG} creati."

# ---------- 5. Archivio + checksum ----------
say "5/8 — Archivio + SHA256"
rm -f "${ARCHIVE}" "${CHECKSUM}"
(
  cd "${PARENT_DIR}"
  git -C petra archive --format=zip --prefix="PETRA-${VERSION}/" \
    -o "${ARCHIVE}" "${TAG}"
  sha256sum "$(basename "${ARCHIVE}")" > "$(basename "${CHECKSUM}")"
  sha256sum -c "$(basename "${CHECKSUM}")"
)
ok "Archivio: ${ARCHIVE}"
ok "Checksum: ${CHECKSUM}"

# ---------- 6. Push ----------
say "6/8 — Push su origin"
git push origin main
git push origin "${TAG}"
ok "Push completato."

# ---------- 7. GitHub Release ----------
say "7/8 — GitHub Release"
if gh release view "${TAG}" >/dev/null 2>&1; then
  warn "Release ${TAG} già esistente su GitHub. Salto."
else
  if [[ -f "${NOTES}" ]]; then
    gh release create "${TAG}" \
      --title "PETRA ${TAG} — Prime Exponent Tower Recursive Algebra" \
      --notes-file "${NOTES}" \
      --latest
  else
    gh release create "${TAG}" \
      --title "PETRA ${TAG} — Prime Exponent Tower Recursive Algebra" \
      --generate-notes \
      --latest
  fi
  gh release upload "${TAG}" "${ARCHIVE}" "${CHECKSUM}"
  ok "GitHub Release ${TAG} pubblicata."
fi

# ---------- 8. Promemoria Zenodo ----------
say "8/8 — Promemoria Zenodo"
cat <<REMINDER

${C_BOLD}============================================================${C_RESET}
${C_BOLD}  ✅ Release GitHub completata.${C_RESET}
${C_YELLOW}  ⚠️  PASSO MANUALE RICHIESTO: upload su Zenodo${C_RESET}
${C_BOLD}============================================================${C_RESET}

  1. Apri il record concept su Zenodo:
     ${C_BLUE}${CONCEPT_RECORD_URL}${C_RESET}
     (Concept DOI: ${CONCEPT_DOI})

  2. Clicca ${C_BOLD}"New version"${C_RESET} in alto a destra.

  3. Carica i file:
       ${ARCHIVE}
       ${CHECKSUM}

  4. Compila i campi:
       Title:         PETRA — Prime Exponent Tower Recursive Algebra ${TAG}
       Version:       ${VERSION}
       License:       MIT License
       Resource type: Software
       Description:   incolla il contenuto di
                      ${NOTES}

  5. Clicca ${C_BOLD}"Publish"${C_RESET} e annota il nuovo Version DOI.

  6. (Opzionale) Aggiorna il CHANGELOG con la sezione "### Published"
     e committa:
       docs: annotate Zenodo version DOI for ${TAG}

${C_BOLD}============================================================${C_RESET}
REMINDER

ok "Fatto. Ricordati l'upload su Zenodo."
