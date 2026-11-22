"""Parser tests against saved MyHadith pages."""
from custom_components.mutiara_hadith.client import parse_featured_ids, parse_hadith_page

from .conftest import load_fixture


def test_featured_ids() -> None:
    ids = parse_featured_ids(load_fixture("home.html"))
    assert ids[0] == 1061
    assert len(ids) >= 5


def test_parse_hadith_1061() -> None:
    h = parse_hadith_page(load_fixture("hadith_1061.html"), 1061)
    assert h.title == "Kekayaan VS Kesihatan"
    assert h.status == "Sahih"
    assert h.koleksi == "Sunan Ibnu Majah"
    assert h.nombor_hadith == "2141"
    assert h.perawi == "Abdullah bin Khubaib RA"
    assert h.matan.startswith("عَنْ")
    assert h.maksud.startswith("Daripada")
    # "<strong>Sumber rujukan:</strong><br />1. ..." style
    assert h.sumber_rujukan[0] == "Kitab Sunan Ibn Majah"
    assert "Sumber" not in h.penghayatan


def test_parse_hadith_945() -> None:
    h = parse_hadith_page(load_fixture("hadith_945.html"), 945)
    assert h.status == "Tiada Status"
    assert h.bab == "Ilmu dan berpesan pada waktu malam"
    # "<p>Sumber Rujukan :</p><ol>" style
    assert len(h.sumber_rujukan) == 5
    assert h.url == "https://myhadith.islam.gov.my/hadith/945"
