![mutiara-hadith](/custom_components/mutiara_hadith/brand/dark_logo.png)

[![GitHub Repo stars](https://img.shields.io/github/stars/zubir2k/homeassistant-mutiarahadith?style=social)](https://github.com/zubir2k/homeassistant-mutiarahadith/stargazers)
[![hacs_badge](https://img.shields.io/badge/HACS-Integration-41BDF5.svg)](https://github.com/hacs/integration)
![GitHub all releases](https://img.shields.io/badge/dynamic/json?color=41BDF5&logo=home-assistant&label=Download%20Count&suffix=%20installs&cacheSeconds=15600&url=https://analytics.home-assistant.io/custom_integrations.json&query=$.mutiara_hadith.total)
[![Buy](https://img.shields.io/badge/Belanja-Coffee-yellow.svg)](https://zubirco.de/buymecoffee)
[![GitHub Release](https://img.shields.io/github/release/zubir2k/homeassistant-mutiarahadith.svg)](https://github.com/zubir2k/homeassistant-mutiarahadith/releases/)

Assalamu'alaikum

This is a custom integration for **Mutiara Hadith (JAKIM)** from [MyHadith](https://myhadith.islam.gov.my) for your Home Assistant 🏠 \
_May this benefit you, inshaAllah._

## 🚩 Features
- Fetches the official **Mutiara Hadith** featured by JAKIM (Jabatan Kemajuan Islam Malaysia).
- Bundles complete content: Arabic **Matan**, Malay **Maksud** (Translation), **Penghayatan** (Lessons/Reflections), and **Sumber Rujukan** (References).
- Comprehensive metadata: Hadith number (`nombor_hadith`), collection (`koleksi`), book (`kitab`), chapter (`bab`), narrator (`perawi`), and authenticity status (`status`: Sahih, Hasan, Dhaif, etc.).
- Bundled dashboard card (**Mutiara Hadith Card**) that automatically registers without manual resource configuration.
- Database optimization: long text attributes are unrecorded from the recorder database to keep your database lean.
- Configurable scan/refresh interval (1 to 24 hours, default 6 hours).
- Complete setup support: UI config flow, options flow, reconfigure flow, and diagnostics with API key redaction.

## 🎯 Use Cases
- Display daily featured Mutiara Hadith on your Home Assistant dashboard with elegant Arabic typography (Amiri font).
- Automate hadith sharing via instant messaging (e.g. WhatsApp, Telegram) or family notifications.
- Read and reflect on the lessons (penghayatan) and review authentic citations directly from your smart home.

## 🕹️ Installation
#### With Marketplace/HACS
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=zubir2k&repository=homeassistant-mutiarahadith&category=integration)

> [!Tip]
> If you are unable to use the button above, manually add `https://github.com/zubir2k/homeassistant-mutiarahadith` as a Custom Repository in Marketplace/HACS (Category: `Integration`).

#### Manual
1. Copy the `mutiara_hadith` directory from `custom_components` in this repository and place inside your Home Assistant's `custom_components` directory.
2. Restart Home Assistant
3. Follow the instructions in the `Setup` section

> [!WARNING]
> If installing manually, in order to be alerted about new releases, you will need to subscribe to releases from this repository.

## 📦 Setup
[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=mutiara_hadith)

> [!Tip]
> If you are unable to use the button above, follow the steps below:
> 1. Navigate to the Home Assistant Integrations page (**Settings → Devices & Services**)
> 2. Click the `+ ADD INTEGRATION` button in the lower right-hand corner
> 3. Search for `Mutiara Hadith (JAKIM)`
> 4. Select your preferred data source mode (default: `Website`) and press Submit

## 🌐 Data Source

| Mode | How it works | Status |
|---|---|---|
| **Website (scrape)** | Reads the MyHadith homepage carousel, then that hadith's page. Only 2 polite requests per refresh. | Default |
| **MyHadith API** | `GET /api/hadith` with an `X-API-KEY` issued by JAKIM. | Supported (waiting for key) |

> [!NOTE]
> The official Smart Hadith mobile app is no longer active (its Firebase backend was decommissioned), making the MyHadith website the public authoritative source. Once JAKIM issues you an API key, simply go to **Settings → Devices & Services → Mutiara Hadith → ⋮ → Reconfigure** to switch modes seamlessly.

## 📊 Entities & Attributes

`sensor.mutiara_hadith`: the primary sensor whose state represents the Hadith title.

| Attribute | Description / Example |
|---|---|
| `hadith_id` | `1061` |
| `url` | `https://myhadith.islam.gov.my/hadith/1061` |
| `matan` | Arabic matan text with takhrij |
| `maksud` | Malay translation |
| `penghayatan` | Lessons, reflections, and guidance |
| `sumber_rujukan` | List of references / citations |
| `nombor_hadith` | `2141` |
| `koleksi` | `Sunan Ibnu Majah` |
| `kitab` | `Kitab Perniagaan` |
| `bab` | `Galakan Mencari Rezeki` |
| `perawi` | `Abdullah bin Khubaib RA` |
| `status` | Hadith authenticity status (`Sahih` / `Hasan` / `Dhaif` / `Maudhu` / `Tiada Status`) |

> [!NOTE]
> Long text attributes (`matan`, `maksud`, `penghayatan`, `sumber_rujukan`) are unrecorded from the recorder database by design to avoid inflating database size.

## 🃏 Mutiara Hadith Card

The integration ships with its own dashboard card (**Mutiara Hadith Card**) and automatically loads it on all dashboards. No manual resource configuration is required.

- Arabic text rendered in the bundled **Amiri** font (SIL Open Font License) in right-to-left layout.
- Interactive tabbed view switching between **Maksud**, **Penghayatan**, and **Butiran** (Hadith details & status).
- Native Home Assistant light and dark theme support.
- Visual editor support in the Lovelace card picker or configurable via YAML:

```yaml
type: custom:mutiara-hadith-card
entity: sensor.mutiara_hadith      # optional
default_tab: maksud                 # maksud | penghayatan | butiran
pane_height: 220                    # px (tabs scroll past this; 0 = grow to fit)
show_takhrij: true                  # show the takhrij line under Arabic text
show_attribution: true              # show attribution in footer
```

## ⚙️ Options & Configuration

- **Refresh Interval**: Change how frequently Home Assistant checks for a new featured hadith (1 to 24 hours, default: 6 hours) via **Settings → Devices & Services → Mutiara Hadith → Configure**.
- **Reconfigure / Reauth**: Easily switch to API mode or update your API key via the integration options menu.

## 🗑️ Removal

1. Remove any Mutiara Hadith cards from your dashboards.
2. Go to **Settings → Devices & services → Mutiara Hadith → ⋮ → Delete**.
3. Uninstall from HACS / the Marketplace (or delete `custom_components/mutiara_hadith`) and restart Home Assistant.

## 📢 Disclaimer & Data Source

- This integration is an unofficial, community-driven project providing convenient access to public Islamic religious content for Home Assistant users.
- Data and content are copyright © **Jabatan Kemajuan Islam Malaysia (JAKIM)** via [MyHadith](https://myhadith.islam.gov.my).
- Every hadith attribute provides a direct permalink back to the source hadith on MyHadith for verification and reference.

## 🎖️ Credits
- Content & Hadith data provided by [MyHadith - Jabatan Kemajuan Islam Malaysia (JAKIM)](https://myhadith.islam.gov.my)
- Typography: [Amiri Font](https://github.com/aliftype/amiri) (SIL Open Font License)

## 📢 Join the Community
- [Home Assistant Malaysia](https://www.facebook.com/groups/homeassistantmalaysia)
- [Home Assistant Official Community](https://community.home-assistant.io)
