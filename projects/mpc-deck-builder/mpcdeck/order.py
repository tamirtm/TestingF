"""Write an MPC Autofill order.xml that points at local image files.

Format matches chilli-axe/mpc-autofill's desktop tool (desktop-tool/src/order.py, constants.py):
an <id> that is an existing file path is used as a local file. Paths are written relative to the
output folder, so run the autofill program from inside that folder.
"""
from xml.etree import ElementTree as ET

# MakePlayingCards quantity brackets (the tool picks the smallest that fits). Check MPC if an order fails.
BRACKETS = [18, 36, 55, 72, 90, 108, 126, 144, 162, 180, 198, 216, 234, 396, 504, 612]
STOCKS = {"S27": "(S27) Smooth", "S30": "(S30) Standard Smooth", "S33": "(S33) Superior Smooth",
          "M31": "(M31) Linen", "P10": "(P10) Plastic"}


def bracket_for(n: int) -> int:
    for b in BRACKETS:
        if n <= b:
            return b
    raise ValueError(f"{n} cards exceeds MPC's largest bracket ({BRACKETS[-1]}); split the order")


def _card(parent: ET.Element, path: str, slots: list[int], name: str) -> None:
    c = ET.SubElement(parent, "card")
    ET.SubElement(c, "id").text = path
    ET.SubElement(c, "sourceType").text = "Local File"
    ET.SubElement(c, "slots").text = ",".join(map(str, slots))
    ET.SubElement(c, "name").text = name
    ET.SubElement(c, "query").text = name.rsplit(".", 1)[0].lower()


def build(fronts: list[tuple[str, list[int]]], backs: list[tuple[str, list[int]]], cardback: str,
          total: int, stock: str = "S30", foil: bool = False) -> str:
    """fronts/backs: (relative image path, slot numbers). Returns the XML text."""
    root = ET.Element("order")
    det = ET.SubElement(root, "details")
    ET.SubElement(det, "quantity").text = str(total)
    ET.SubElement(det, "bracket").text = str(bracket_for(total))
    ET.SubElement(det, "stock").text = STOCKS[stock]
    ET.SubElement(det, "foil").text = "true" if foil else "false"
    fe = ET.SubElement(root, "fronts")
    for path, slots in fronts:
        _card(fe, path, slots, path.rsplit("/", 1)[-1])
    if backs:
        be = ET.SubElement(root, "backs")
        for path, slots in backs:
            _card(be, path, slots, path.rsplit("/", 1)[-1])
    ET.SubElement(root, "cardback").text = cardback
    ET.indent(root)
    return ET.tostring(root, encoding="unicode") + "\n"
