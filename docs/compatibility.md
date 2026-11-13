# Onderzochte compatibiliteit

Gecontroleerd op 13 november 2026 tegen [PS4 Games Installer](https://github.com/e1z0/PS4-Games-Installer/tree/f9212596bafd1011aec594cd8c5bd0d05cff938a), revisie `f9212596bafd1011aec594cd8c5bd0d05cff938a`.

Gelezen bronnen:

- [README: installatie en bediening](https://github.com/e1z0/PS4-Games-Installer/blob/f9212596bafd1011aec594cd8c5bd0d05cff938a/README.md)
- [EXPERT: catalogusformaat, HTTPS en downloadgedrag](https://github.com/e1z0/PS4-Games-Installer/blob/f9212596bafd1011aec594cd8c5bd0d05cff938a/EXPERT.md)
- [DEVELOPMENT: hosttests en implementatie](https://github.com/e1z0/PS4-Games-Installer/blob/f9212596bafd1011aec594cd8c5bd0d05cff938a/DEVELOPMENT.md)
- [De daadwerkelijke catalogusparser](https://github.com/e1z0/PS4-Games-Installer/blob/f9212596bafd1011aec594cd8c5bd0d05cff938a/src/catalog.cpp)
- [PKG-headercontrole van de installer](https://github.com/e1z0/PS4-Games-Installer/blob/f9212596bafd1011aec594cd8c5bd0d05cff938a/src/package.cpp)
- [FPKGi README en JSON-voorbeeld](https://github.com/ItsJokerZz/FPKGi/blob/release/README.md)

De parser vereist een object `DATA` dat HTTP(S)-URL's aan metadataobjecten koppelt. Een niet-lege naam is verplicht. De gebruikte velden `name`, `title_id`, `content_id`, `region`, `version`, `min_fw`, `cover_url`, `release`, `description`, `package_type` en `size` worden daadwerkelijk gelezen.
`size` mag in de installer integer bytes of een decimale string zijn; deze catalogus gebruikt integers. De limieten zijn 8 MiB JSON, 50.000 items, URL kleiner dan 2048 bytes en naam kleiner dan 600 bytes.
Bron, onderzoeksnotities en controlebewijzen horen in research.json en sources.json.

`scripts/check_installer_compat.py` haalt alleen de vastgezette upstream parser, metadatahelper, headers en cJSON op, compileert deze in GitHub Actions en roept `psgi::parseCatalog` aan met onze games.json. Er wordt geen aangepaste PS4-app gemaakt.
De bronbestanden worden tijdelijk gebruikt, met hun bestaande auteursrechtinformatie; ze worden niet in deze repository gekopieerd of als eigen werk gepubliceerd.

Aanvullend onderzocht: [Brewology games](https://store.brewology.com/ps4/games/) en [PKG-Zone](https://pkg-zone.com/). Veel Brewology-games vereisen eigen commerciële data of een externe spelserver. Daarom zijn de eerste items zelfstandig te starten software van officiële GitHub-releases:

- [PS4 2048 v1.0](https://github.com/skidgfx/PS4-2048/releases/tag/v1.0), oorspronkelijke ontwikkelaar, [broncode](https://github.com/skidgfx/PS4-2048).
- [Apollo Save Tool v2.4.0](https://github.com/bucanero/apollo-ps4/releases/tag/v2.4.0), oorspronkelijke ontwikkelaar, [GPLv3-broncode](https://github.com/bucanero/apollo-ps4).

PKG-Zone-downloads voor 2048 en Mandelbrot Zoom gaven bij anonieme Range-requests HTTP 403 en zijn niet opgenomen. De catalogus claimt niet de nieuwere PKG-Zone-versie van 2048 te bevatten.

De controles bewijzen het formaat en bereikbaarheid vanaf de testmachine/CI. Het gedrag op de eigen PS4, firmware/TLS-compatibiliteit, volledige package-integriteit en succesvolle installatie vereisen een hardwaretest.

## Uitgevoerde MVP-controles

De eerste [GitHub Actions-run](https://github.com/Damian98v/personal-ps4-catalog/actions/runs/43442818297) is geslaagd. De originele C++-parser rapporteerde `Upstream PS4 Games Installer accepted 2 packages`. Pages is gepubliceerd en de publieke JSON is via anonieme HTTPS GET byte-inhoudelijk als JSON vergeleken met het lokale catalogusobject.
De packageprobes zijn voor beide releases uitgevoerd (anonieme HEAD, correcte Range-responses, PS4-signatuur, grootte, SFO en laatste byte). Beide covers geven HTTP 200 en zijn PNG-bestanden van 512 × 512 pixels.
Herhaald toevoegen van dezelfde twee namen liet Git-status ongewijzigd. De Python-tests gebruiken afzonderlijke fixtures zodat latere toevoegingen of verwijderingen van echte games de tests niet veranderen.
